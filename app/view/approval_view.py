from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import F, ExpressionWrapper, DecimalField

from app.models import Inventory, PurchaseOrder, Order


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
def approve_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == "POST":
        order.approval_status = "APPROVED"
        order.status = "PO_APPROVED"
        order.save()
        messages.success(request, f"Purchase Order {order.id} request approved.")
        return redirect("approval_manager_list")
    return render(request, "app/approval/approve_purchase_order.html", {"order": order})


@login_required
def reject_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == "POST":
        order.approval_status = "CANCELLED"
        order.save()
        messages.success(request, f"Purchase Order {order.id} request cancelled.")
        return redirect("approval_manager_list")
    return render(request, "app/approval/reject_purchase_order.html", {"order": order})


@login_required
def po_approval_request_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(
        request, "app/approval/approval_request_detail.html", {"order": order}
    )


@login_required
def update_po_approval(request):
    orders = (
            PurchaseOrder.objects
            .select_related("product", "vendor")
            .annotate(
                total_price=ExpressionWrapper(
                    F("quantity") * F("product__price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )
    if request.method == "POST":
        po_id = request.POST["po_id"]
        action = request.POST["action"]  # PENDING / APPROVED / CANCELLED
        po = get_object_or_404(PurchaseOrder, pk=po_id)

        po.approval_status = action
        if action == "PENDING":
            po.status = "PO_RAISED"
        elif action == "APPROVED":
            po.status = "PO_APPROVED"
        elif action == "CANCELLED":
            po.status = "PO_REJECTED"  # or keep PO_RAISED, adjust as needed
        po.save(update_fields=["approval_status", "status"])
        messages.success(
            request, f"PO #{po.id} set to {po.get_approval_status_display()}."
        )
        return redirect("update_po_approval")

    return render(request, "app/approval/update_po_approval.html", {"orders": orders})


@login_required
def approve_inventory(request, pk):
    inv = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        inv.approval_status = "APPROVED"
        inv.status = "INWARD_APPROVED"  # workflow step
        inv.save()
        messages.success(request, f"Inventory #{inv.pk} request approved.")
        return redirect("approval_manager_list")
    return render(request, "app/approval/approve_inventory.html", {"inv": inv})


@login_required
def reject_inventory(request, pk):
    inv = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        inv.approval_status = "CANCELLED"
        inv.status = "INWARD_REJECTED"
        inv.save()
        messages.success(request, f"Inventory #{inv.pk} request cancelled.")
        return redirect("approval_manager_list")
    return render(request, "app/approval/reject_inventory.html", {"inv": inv})


@login_required
def inventory_approval_request_detail(request, pk):
    inv = get_object_or_404(Inventory, pk=pk)
    return render(request, "app/approval/approval_request_detail.html", {"inv": inv})


@login_required
def update_inventory_approval(request):
    inventories = (
            Inventory.objects
            .select_related("product", "vendor")
            .annotate(
                total_price=ExpressionWrapper(
                    F("inward_qty") * F("product__price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )
    if request.method == "POST":
        inv_id = request.POST["inv_id"]
        action = request.POST["action"]  # PENDING / APPROVED / CANCELLED
        inv = get_object_or_404(Inventory, pk=inv_id)

        inv.approval_status = action
        if action == "PENDING":
            inv.status = "INWARD_REQUESTED"
        elif action == "APPROVED":
            inv.status = "INWARD_APPROVED"
        elif action == "CANCELLED":
            inv.status = "INWARD_REJECTED"
        inv.save(update_fields=["approval_status", "status"])
        messages.success(
            request, f"Inward #{inv.id} set to {inv.get_approval_status_display()}."
        )
        return redirect("update_inventory_approval")

    return render(
        request,
        "app/approval/update_inventory_approval.html",
        {"inventories": inventories},
    )

# Approve an order
@login_required
def approve_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.approval_status = "APPROVED"
        order.status = "ORDER_APPROVED"
        order.save()
        messages.success(request, f"Order {order.id} request approved.")
        return redirect("approval_manager_list")
    return render(request, "app/approval/approve_order.html", {"order": order})

# Reject an order
@login_required
def reject_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.approval_status = "CANCELLED"
        order.status = "ORDER_REJECTED"
        order.save()
        messages.success(request, f"Order {order.id} request cancelled.")
        return redirect("approval_manager_list")
    return render(request, "app/approval/reject_order.html", {"order": order})

# Update order approval status
@login_required
def update_order_approval(request):
    orders = (
        Order.objects
        .select_related("product", "vendor")
        .annotate(
            total_price=ExpressionWrapper(
                F("quantity") * F("product__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
    )
    

    if request.method == "POST":
        order_id = request.POST["order_id"]
        action = request.POST["action"]  # PENDING / APPROVED / CANCELLED
        order = get_object_or_404(Order, pk=order_id)

        order.approval_status = action
        if action == "PENDING":
            order.status = "ORDER_RAISED"
        elif action == "APPROVED":
            order.status = "ORDER_APPROVED"
        elif action == "CANCELLED":
            order.status = "ORDER_REJECTED"
        order.save(update_fields=["approval_status", "status"])
        messages.success(
            request, f"Order #{order.id} set to {order.get_approval_status_display()}."
        )
        return redirect("update_order_approval")

    return render(
        request,
        "app/approval/update_order_approval.html",
        {"orders": orders},
    )