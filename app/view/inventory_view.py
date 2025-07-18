from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Inventory, Product, Vendor


@login_required
def inventory_list(request):
    inventory = Inventory.objects.annotate(
        total_price=ExpressionWrapper(
            F("stock_quantity") * F("product__price"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    )

    total_inward_qty = inventory.aggregate(Sum("inward_qty"))["inward_qty__sum"] or 0
    total_current_stock = (
        inventory.aggregate(Sum("stock_quantity"))["stock_quantity__sum"] or 0
    )
    total_price = inventory.aggregate(Sum("total_price"))["total_price__sum"] or 0

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
