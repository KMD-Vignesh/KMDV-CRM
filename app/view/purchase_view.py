from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from app.models import Product, PurchaseOrder, Vendor


@login_required
def purchase_list(request):
    query = Q()

    # --- filters -------------------------------------------------------------
    po_id = request.GET.get("po_id")
    if po_id:
        query &= Q(id=po_id)

    product_q = request.GET.get("product")
    if product_q:
        query &= Q(product__name__icontains=product_q) | Q(
            product__product_id__icontains=product_q
        )

    vendor_q = request.GET.get("vendor")
    if vendor_q:
        query &= Q(vendor__name__icontains=vendor_q) | Q(
            vendor__vendor_id__icontains=vendor_q
        )

    quantity = request.GET.get("quantity")
    if quantity:
        try:
            query &= Q(quantity=int(quantity))
        except ValueError:
            pass

    total_price = request.GET.get("total_price")
    if total_price:
        try:
            query &= Q(total_price=Decimal(total_price))
        except InvalidOperation:
            pass

    created_date = request.GET.get("created_date")
    if created_date:
        parsed = parse_date(created_date)
        if parsed:
            query &= Q(created_at__date=parsed)

    status = request.GET.get("status")
    if status:
        query &= Q(status=status)
    # ------------------------------------------------------------------------

    orders = (
        PurchaseOrder.objects.select_related("product", "vendor")
        .annotate(
            total_price=ExpressionWrapper(
                F("quantity") * F("product__price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .filter(query)
        .order_by("-id")
    )

    # status counts
    status_totals = dict(
        orders.values("status")
        .annotate(total=Sum("quantity"))
        .values_list("status", "total")
    )
    STATUS_KEYS = [
        "PO_RAISED",
        "PO_APPROVED",
        "PO_REJECTED",
        "PO_SHIPPED",
        "PO_DELIVERED",
        "INWARD_REQUESTED",
    ]
    summary = {k: status_totals.get(k, 0) for k in STATUS_KEYS}


    grand_total = orders.aggregate(
        total_quantity=Sum("quantity"),
        grand_total_price=Sum("total_price"),
    )

    return render(
        request,
        "app/purchase/purchase_list.html",
        {
            "orders": orders,
            "summary": summary,
            "grand_total": grand_total,
        },
    )


@login_required
def add_purchase(request):
    if request.method == "POST":
        PurchaseOrder.objects.create(
            product_id=request.POST["product"],
            vendor_id=request.POST["vendor"],
            quantity=request.POST["qty"],
            status="PO_RAISED",  # default
        )
        messages.success(
            request,
            f"Purchase order (ProductID: {request.POST['product']}, VendorID: {request.POST['vendor']}) created successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("purchase_list")
    products = Product.objects.all()
    vendors = Vendor.objects.all()
    return render(
        request,
        "app/purchase/add_purchase.html",
        {"products": products, "vendors": vendors},
    )


@login_required
def edit_purchase(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)

    # ---- Statuses that are **never** selectable after approval
    DISALLOWED_AFTER_APPROVAL = {"PO_RAISED", "PO_REJECTED"}

    # ---- Build the list that will reach the template
    if order.approval_status == "APPROVED":
        allowed_choices = [
            (k, v)
            for k, v in PurchaseOrder.STATUS_CHOICES
            if k not in DISALLOWED_AFTER_APPROVAL
        ]
    else:
        allowed_choices = []  # empty ⇒ drop-down not rendered

    if request.method == "POST":
        if "request_approval" in request.POST:
            order.approval_status = "PENDING"
            order.save(update_fields=["approval_status"])
            messages.success(request, f"Approval requested for PO #{order.id}.")
            return redirect("edit_purchase", pk=pk)

        order.product_id = request.POST["product"]
        order.vendor_id = request.POST["vendor"]
        order.quantity = request.POST["qty"]
        # Only save status if the widget was shown
        if allowed_choices:  # same condition as in template
            order.status = request.POST["status"]
        order.save()
        messages.success(
            request,
            f"Purchase order (PO_ID: {order.id}) updated successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("purchase_list")

    products = Product.objects.all()
    vendors = Vendor.objects.all()
    return render(
        request,
        "app/purchase/edit_purchase.html",
        {
            "order": order,
            "products": products,
            "vendors": vendors,
            "status_choices": allowed_choices,  # ← filtered list
        },
    )


@login_required
def delete_purchase(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    order_id = f"{order.id}"
    if request.method == "POST":
        order.delete()
        messages.success(
            request,
            f"Purchase order (PO_ID: {order_id}) deleted successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("purchase_list")
    return render(request, "app/purchase/delete_purchase.html", {"order": order})


@login_required
def print_purchase_order(request, pk):
    po = get_object_or_404(
        PurchaseOrder.objects.select_related("product", "vendor"), pk=pk
    )
    total = po.quantity * po.product.price
    return render(
        request, "app/purchase/purchase_print.html", {"po": po, "total": total}
    )
