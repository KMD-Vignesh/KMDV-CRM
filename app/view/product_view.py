from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Category, Product



@login_required
def product_list(request):
    products = Product.objects.all().order_by("name")
    return render(request, "app/product/product_list.html", {"products": products})


@login_required
def add_product(request):
    if request.method == "POST":
        pid = request.POST["product_id"].strip()
        if Product.objects.filter(product_id__iexact=pid).exists():
            messages.error(request, f"Product ID “{pid}” already exists!")
            return redirect("add_product")

        Product.objects.create(
            product_id=pid,
            name=request.POST["name"],
            category_id=request.POST["category"],
            price=request.POST["price"],
            description=request.POST.get("description", ""),
        )
        messages.success(request, f"Product {pid} created.")
        return redirect("product_list")

    categories = Category.objects.all()
    return render(request, "app/product/add_product.html", {"categories": categories})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        pid = request.POST["product_id"].strip()
        if Product.objects.filter(product_id__iexact=pid).exclude(pk=pk).exists():
            messages.error(
                request, f"Product ID “{pid}” is already taken by another product!"
            )
            return redirect("edit_product", pk=pk)

        product.product_id = pid
        product.name = request.POST["name"]
        product.category_id = request.POST["category"]
        product.price = request.POST["price"]
        product.description = request.POST.get("description", "")
        product.save()
        messages.success(request, f"Product {pid} updated.")
        return redirect("product_list")

    categories = Category.objects.all()
    return render(
        request,
        "app/product/edit_product.html",
        {"product": product, "categories": categories},
    )


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(
            request,
            f"Product - {product.name} deleted successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("product_list")
    return render(request, "app/product/delete_product.html", {"product": product})
