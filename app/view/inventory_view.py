from decimal import DivisionByZero, InvalidOperation, Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, ExpressionWrapper, F, Sum, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from app.models import Inventory, Product, Vendor

@login_required
def inventory_list(request):
    query = Q()

    # ----- filters -----------------------------------------------------------
    product_q = request.GET.get("product")
    if product_q:
        query &= Q(product__name__icontains=product_q) | \
                 Q(product__product_id__icontains=product_q)

    vendor_q = request.GET.get("vendor")
    if vendor_q:
        query &= Q(vendor__name__icontains=vendor_q) | \
                 Q(vendor__vendor_id__icontains=vendor_q)

    stock_quantity = request.GET.get("stock_quantity")
    if stock_quantity:
        try:
            query &= Q(stock_quantity=int(stock_quantity))
        except ValueError:
            pass

    inward_qty = request.GET.get("inward_qty")
    if inward_qty:
        try:
            query &= Q(inward_qty=int(inward_qty))
        except ValueError:
            pass

    inward_date = request.GET.get("inward_date")
    if inward_date:
        parsed_date = parse_date(inward_date)
        if parsed_date:
            query &= Q(inward_date__date=parsed_date)

    total_price = request.GET.get("total_price")
    if total_price:
        try:
            total_price_decimal = Decimal(total_price)
            query &= Q(total_price=total_price_decimal)
        except (InvalidOperation, DivisionByZero):
            pass
    status = request.GET.get("status")
    if status:
        query &= Q(status=status)
    # -------------------------------------------------------------------------

    inventory = (
        Inventory.objects
        .annotate(
            total_price=ExpressionWrapper(
                F("stock_quantity") * F("product__price"),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )
        .filter(query)
        .order_by("-last_updated")
    )

    # ---- totals -------------------------------------------------------------
    total_inward_qty = (
        inventory.aggregate(Sum("inward_qty"))["inward_qty__sum"] or 0
    )
    total_current_stock = (
        inventory.aggregate(Sum("stock_quantity"))["stock_quantity__sum"] or 0
    )
    total_price = (
        inventory.aggregate(Sum("total_price"))["total_price__sum"] or 0
    )

    return render(
        request,
        "app/inventory/inventory_list.html",
        {
            "inventory": inventory,
            "total_inward_qty": total_inward_qty,
            "total_current_stock": total_current_stock,
            "total_price": total_price,
        },
    )

@login_required
def add_inventory(request):
    if request.method == "POST":
        product_id = request.POST["product"]
        vendor_id = request.POST["vendor"]
        qty = request.POST["qty"]
        Inventory.objects.create(
            product_id=product_id,
            vendor_id=vendor_id,
            stock_quantity=qty,
            inward_qty=qty,
            status=request.POST.get("status", "INWARD_REQUESTED"),
        )
        messages.success(
            request,
            f"Inventory Qty {qty} for (Product:{product_id},Vendor:{vendor_id}) created successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("inventory_list")

    return render(
        request,
        "app/inventory/add_inventory.html",
        {
            "products": Product.objects.all(),
            "vendors": Vendor.objects.all(),
            "status_choices": Inventory.STATUS_CHOICES,
        },
    )


@login_required
def edit_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        inventory.product_id = request.POST["product"]
        inventory.vendor_id = request.POST["vendor"]
        inventory.stock_quantity = request.POST["qty"]
        inventory.status = request.POST.get("status", "INWARD_REQUESTED")
        inventory.save()
        messages.success(
            request,
            f"Inventory Product - {inventory.product.name}, Vendor - {inventory.vendor.name} updated successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("inventory_list")
    return render(
        request,
        "app/inventory/edit_inventory.html",
        {
            "inventory": inventory,
            "products": Product.objects.all(),
            "vendors": Vendor.objects.all(),
            "status_choices": Inventory.STATUS_CHOICES,
        },
    )


@login_required
def delete_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        inventory.delete()
        messages.success(
            request,
            f"Inventory Product - {inventory.product.name}, Vendor - {inventory.vendor.name} deleted successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("inventory_list")
    return render(
        request, "app/inventory/delete_inventory.html", {"inventory": inventory}
    )
