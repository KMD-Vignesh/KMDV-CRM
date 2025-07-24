from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import F, ExpressionWrapper, DecimalField

from app.models import Inventory, PurchaseOrder, Order


MODELS = {
    'po':        PurchaseOrder,
    'inventory': Inventory,
    'order':     Order,
}

# common mapping for status when approval changes
STATUS_MAP = {
    'po': {
        'PENDING':  'PO_RAISED',
        'APPROVED': 'PO_APPROVED',
        'CANCELLED':'PO_REJECTED',
    },
    'inventory': {
        'PENDING':  'INWARD_REQUESTED',
        'APPROVED': 'INWARD_APPROVED',
        'CANCELLED':'INWARD_REJECTED',
    },
    'order': {
        'PENDING':  'ORDER_RAISED',
        'APPROVED': 'ORDER_APPROVED',
        'CANCELLED':'ORDER_REJECTED',
    },
}
@login_required
def approval_request_list(request):
    purchase_orders = PurchaseOrder.objects.filter(approval_status="PENDING")
    inventories = Inventory.objects.filter(approval_status="PENDING")
    orders = Order.objects.filter(approval_status="PENDING")
    return render(
        request,
        "app/approval/approval_request_list.html",
        {"purchase_orders": purchase_orders, "inventories": inventories, "orders":orders},
    )


@login_required
def approval_manager_list(request):
    purchase_orders = PurchaseOrder.objects.filter(approval_status="PENDING")
    inventories = Inventory.objects.filter(approval_status="PENDING")
    orders = Order.objects.filter(approval_status="PENDING")
    return render(
        request,
        "app/approval/approval_manager_list.html",
        {"purchase_orders": purchase_orders, "inventories": inventories, "orders":orders},
    )


@login_required
def po_approval_request_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(
        request, "app/approval/approval_request_detail.html", {"order": order}
    )


@login_required
def inventory_approval_request_detail(request, pk):
    inv = get_object_or_404(Inventory, pk=pk)
    return render(request, "app/approval/approval_request_detail.html", {"inv": inv})


@login_required
def order_approval_request_detail(request, pk):
    orders = get_object_or_404(Order, pk=pk)
    return render(request, "app/approval/approval_request_detail.html", {"orders": orders})


@login_required
def update_approval(request, model):
    Model = MODELS[model]

    if request.method == 'POST':
        pk     = request.POST['pk']
        action = request.POST['action']
        obj    = get_object_or_404(Model, pk=pk)
        obj.approval_status = action
        obj.status          = STATUS_MAP[model][action]
        obj.save(update_fields=['approval_status', 'status'])
        messages.success(request, f"{model.title()} #{pk} set to {action}")
        return redirect('update_approval', model=model)

    # --- choose the right queryset ---
    if model == 'inventory':
        qs = (
            Model.objects
            .select_related('product', 'vendor')
            .annotate(
                qty=F('inward_qty'),
                total_price=ExpressionWrapper(
                    F("inward_qty") * F("product__price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )
    else:   # po / order
        qs = (
            Model.objects
            .select_related('product', 'vendor')
            .annotate(
                qty=F('quantity'),
                total_price=ExpressionWrapper(
                    F("quantity") * F("product__price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )

    context = {
        'records': qs,
        'model':   model,
        'title':   {'po':'PO','inventory':'Inward','order':'Order'}[model],
        'status_class_prefix': {'po':'po','inventory':'inventory','order':'order'}[model],
    }
    return render(request, 'app/approval/update_approval.html', context)


@login_required
def mark_approved(request, model, pk):
    return _handle_approval(request, model, pk, 'APPROVED', 'approve')

@login_required
def mark_rejected(request, model, pk):
    return _handle_approval(request, model, pk, 'CANCELLED', 'reject')

def _handle_approval(request, model, pk, action, verb):
    Model = MODELS[model]
        # build the annotated queryset
    if model == 'inventory':
        qs = (
            Model.objects
            .select_related('product', 'vendor')
            .annotate(
                qty=F('inward_qty'),
                total_price=ExpressionWrapper(
                    F("inward_qty") * F("product__price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )
    else:  # po / order
        qs = (
            Model.objects
            .select_related('product', 'vendor')
            .annotate(
                qty=F('quantity'),
                total_price=ExpressionWrapper(
                    F("quantity") * F("product__price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )

    obj = get_object_or_404(qs, pk=pk)

    if request.method == 'POST':
        obj.approval_status = action
        obj.status          = STATUS_MAP[model][action]
        obj.save(update_fields=['approval_status', 'status'])
        messages.success(request, f"{model.title()} #{pk} marked {verb}.")
        return redirect('approval_manager_list')


    # GET → confirmation page
    context = {'object': obj, 'model': model, 'verb': verb, 'action': action}
    return render(request, 'app/approval/confirm_approval.html', context)