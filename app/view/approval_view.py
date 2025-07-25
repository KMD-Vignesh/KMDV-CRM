from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, ExpressionWrapper, F, Q
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Inventory, Order, PurchaseOrder

MODELS = {
    "po": PurchaseOrder,
    "inventory": Inventory,
    "order": Order,
}

# common mapping for status when approval changes
STATUS_MAP = {
    "po": {
        "PENDING": "PO_RAISED",
        "APPROVED": "PO_APPROVED",
        "CANCELLED": "PO_REJECTED",
    },
    "inventory": {
        "PENDING": "INWARD_REQUESTED",
        "APPROVED": "INWARD_APPROVED",
        "CANCELLED": "INWARD_REJECTED",
    },
    "order": {
        "PENDING": "ORDER_RAISED",
        "APPROVED": "ORDER_APPROVED",
        "CANCELLED": "ORDER_REJECTED",
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
        {
            "purchase_orders": purchase_orders,
            "inventories": inventories,
            "orders": orders,
        },
    )


@login_required
def approval_manager_list(request):
    purchase_orders = PurchaseOrder.objects.filter(approval_status="PENDING")
    inventories = Inventory.objects.filter(approval_status="PENDING")
    orders = Order.objects.filter(approval_status="PENDING")
    return render(
        request,
        "app/approval/approval_manager_list.html",
        {
            "purchase_orders": purchase_orders,
            "inventories": inventories,
            "orders": orders,
        },
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
    return render(
        request, "app/approval/approval_request_detail.html", {"orders": orders}
    )

@login_required
def update_approval(request, model):
    Model = MODELS[model]

    if request.method == "POST":
        pk = request.POST["pk"]
        action = request.POST["action"]
        obj = get_object_or_404(Model, pk=pk)
        obj.approval_status = action
        obj.status = STATUS_MAP[model][action]
        obj.save(update_fields=["approval_status", "status"])
        messages.success(request, f"{model.title()} #{pk} set to {action}")
        return redirect("update_approval", model=model)

    # --- Build query filters ---
    query = Q()

    # ID filter
    id_q = request.GET.get("id")
    if id_q:
        query &= Q(id=id_q)

    # Vendor filter
    vendor_q = request.GET.get("vendor")
    if vendor_q:
        query &= Q(vendor__name__icontains=vendor_q) | Q(
            vendor__vendor_id__icontains=vendor_q
        )

    # Product filter
    product_q = request.GET.get("product")
    if product_q:
        query &= Q(product__name__icontains=product_q) | Q(
            product__product_id__icontains=product_q
        )

    # Product price filter - same logic as order_list
    product_price = request.GET.get("product_price")
    if product_price:
        try:
            product_price_decimal = Decimal(product_price)
            query &= Q(product__price=product_price_decimal)
        except (InvalidOperation, ValueError):
            pass

    # Quantity filter
    qty_q = request.GET.get("qty")
    if qty_q:
        try:
            qty_val = int(qty_q)
            if model == "inventory":
                query &= Q(inward_qty=qty_q)
            else:
                query &= Q(quantity=qty_q)
        except ValueError:
            pass

    # Total price filter - using the same logic as order_list
    total_price = request.GET.get("total_price")
    if total_price:
        try:
            total_price_decimal = Decimal(total_price)
            query &= Q(total_price=total_price_decimal)
        except (InvalidOperation, ValueError):
            pass

    # Status filter - Use the same approach as order_list
    status_q = request.GET.get("status")
    if status_q:
        query &= Q(status=status_q)


    # Approval Status filter
    approval_status_q = request.GET.get("approval_status")
    if approval_status_q:
        query &= Q(approval_status=approval_status_q)

    # --- choose the right queryset ---
    if model == "inventory":
        qs = Model.objects.select_related("product", "vendor").annotate(
            qty=F("inward_qty"),
            total_price=ExpressionWrapper(
                F("inward_qty") * F("product__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
    else:  # po / order
        qs = Model.objects.select_related("product", "vendor").annotate(
            qty=F("quantity"),
            total_price=ExpressionWrapper(
                F("quantity") * F("product__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )

    # Apply filters
    qs = qs.filter(query)

    # Status choices for filter dropdown - Use the same approach as order_list
    status_choices = Model.STATUS_CHOICES

    if status_q:
        print(f"Sample record status: {qs.first().status if qs.exists() else 'No records'}")
    context = {
        "records": qs,
        "model": model,
        "title": {"po": "PO", "inventory": "Inward", "order": "Order"}[model],
        "status_class_prefix": {"po": "po", "inventory": "inventory", "order": "order"}[
            model
        ],
        "status_choices": status_choices,
    }

    return render(request, "app/approval/update_approval.html", context)

@login_required
def mark_approved(request, model, pk):
    return _handle_approval(request, model, pk, "APPROVED", "approve")


@login_required
def mark_rejected(request, model, pk):
    return _handle_approval(request, model, pk, "CANCELLED", "reject")


def _handle_approval(request, model, pk, action, verb):
    Model = MODELS[model]
    # build the annotated queryset
    if model == "inventory":
        qs = Model.objects.select_related("product", "vendor").annotate(
            qty=F("inward_qty"),
            total_price=ExpressionWrapper(
                F("inward_qty") * F("product__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
    else:  # po / order
        qs = Model.objects.select_related("product", "vendor").annotate(
            qty=F("quantity"),
            total_price=ExpressionWrapper(
                F("quantity") * F("product__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )

    obj = get_object_or_404(qs, pk=pk)

    if request.method == "POST":
        obj.approval_status = action
        obj.status = STATUS_MAP[model][action]
        obj.save(update_fields=["approval_status", "status"])
        messages.success(request, f"{model.title()} #{pk} marked {verb}.")
        return redirect("approval_manager_list")

    # GET → confirmation page
    context = {"object": obj, "model": model, "verb": verb, "action": action}
    return render(request, "app/approval/confirm_approval.html", context)
