import stat
from turtle import st

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from app import models

from .decorators import admin_required, permission_required
from .forms import CustomUserCreationForm
from .models import Category, Inventory, Order, Product, UserProfile, Vendor


@login_required
def dashboard(request):
    products_count = Product.objects.count()
    inventory_summary = list(
        Inventory.objects.values("product__name").annotate(total=Sum("stock_quantity"))
    )
    products = Product.objects.all()
    categories = Category.objects.all()
    inventory = Inventory.objects.all()

    order_summary = (
        Order.objects.values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("-total")
    )
    orders_count = Order.objects.count()

    total_stock = Inventory.objects.aggregate(t=Sum("stock_quantity"))["t"] or 0
    total_orders = Order.objects.aggregate(total=Sum("quantity"))["total"] or 0

    context = {
        "products_count": products_count,
        "orders_count": orders_count,
        "inventory_summary": inventory_summary,
        "order_summary": order_summary,
        "products": products,
        "categories": categories,
        "inventory": inventory,
        "total_stock": total_stock,
        "total_orders": total_orders,
    }

    return render(request, "app/dashboard.html", context)


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "app/category_list.html", {"categories": categories})


@login_required
def add_category(request):
    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST.get("description", "")
        Category.objects.create(name=name, description=description)
        messages.success(
            request,
            f"Category - {name} created successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("category_list")
    return render(request, "app/add_category.html")


@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.name = request.POST["name"]
        category.description = request.POST.get("description", "")
        category.save()
        return redirect("category_list")
    return render(request, "app/edit_category.html", {"category": category})


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect("category_list")
    return render(request, "app/delete_category.html", {"category": category})


@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, "app/product_list.html", {"products": products})


@login_required
def add_product(request):
    if request.method == "POST":
        name = request.POST["name"]
        category_id = request.POST["category"]
        price = request.POST["price"]
        description = request.POST.get("description", "")
        Product.objects.create(
            name=name, category_id=category_id, price=price, description=description
        )
        return redirect("product_list")
    categories = Category.objects.all()
    return render(request, "app/add_product.html", {"categories": categories})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.name = request.POST["name"]
        product.category_id = request.POST["category"]
        product.price = request.POST["price"]
        product.description = request.POST.get("description", "")
        product.save()
        return redirect("product_list")
    categories = Category.objects.all()
    return render(
        request, "app/edit_product.html", {"product": product, "categories": categories}
    )


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "app/delete_product.html", {"product": product})


@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, "app/vendor_list.html", {"vendors": vendors})


@login_required
def add_vendor(request):
    if request.method == "POST":
        name = request.POST["name"]
        address = request.POST["address"]
        Vendor.objects.create(name=name, address=address)
        return redirect("vendor_list")
    return render(request, "app/add_vendor.html")


@login_required
def edit_vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == "POST":
        vendor.name = request.POST["name"]
        vendor.address = request.POST["address"]
        vendor.save()
        return redirect("vendor_list")
    return render(request, "app/edit_vendor.html", {"vendor": vendor})


@login_required
def delete_vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == "POST":
        vendor.delete()
        return redirect("vendor_list")
    return render(request, "app/delete_vendor.html", {"vendor": vendor})


@login_required
def inventory_list(request):
    inventory = Inventory.objects.all()
    return render(request, "app/inventory_list.html", {"inventory": inventory})


@login_required
def add_inventory(request):
    if request.method == "POST":
        product_id = request.POST["product"]
        vendor_id = request.POST["vendor"]
        qty = request.POST["qty"]
        Inventory.objects.create(
            product_id=product_id, vendor_id=vendor_id, stock_quantity=qty
        )
        return redirect("inventory_list")
    products = Product.objects.all()
    vendors = Vendor.objects.all()
    return render(
        request, "app/add_inventory.html", {"products": products, "vendors": vendors}
    )


@login_required
def edit_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        inventory.product_id = request.POST["product"]
        inventory.vendor_id = request.POST["vendor"]
        inventory.stock_quantity = request.POST["qty"]
        inventory.save()
        return redirect("inventory_list")
    products = Product.objects.all()
    vendors = Vendor.objects.all()
    return render(
        request,
        "app/edit_inventory.html",
        {"inventory": inventory, "products": products, "vendors": vendors},
    )


@login_required
def delete_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        inventory.delete()
        return redirect("inventory_list")
    return render(request, "app/delete_inventory.html", {"inventory": inventory})


@login_required
def order_list(request):
    orders = Order.objects.all()
    orders_total = orders.aggregate(
        total_quantity=Sum("quantity"),
        active_count=Sum("quantity", filter=Q(is_cancelled=False)),
        cancelled_count=Sum("quantity", filter=Q(is_cancelled=True)),
    )
    return render(
        request, "app/order_list.html", {"orders": orders, "orders_total": orders_total}
    )


@login_required
def add_order(request):
    if request.method == "POST":
        product_id = request.POST.get("product")
        vendor_id = request.POST.get("vendor")
        quantity = int(request.POST.get("qty"))

        try:
            product = get_object_or_404(Product, id=product_id)
            vendor = get_object_or_404(Vendor, id=vendor_id)

            # ------------------------------------------------------------------
            # 1) SUM total stock (handles multiple Inventory rows)
            # ------------------------------------------------------------------
            total_stock = (
                Inventory.objects.filter(product=product, vendor=vendor).aggregate(
                    total=Sum("stock_quantity")
                )["total"]
                or 0
            )

            if total_stock < quantity:
                messages.error(
                    request,
                    f"Insufficient stock. Available: {total_stock}, Requested: {quantity}",
                    extra_tags="auto-dismiss page-specific",
                )
                return redirect("add_order")

            # ------------------------------------------------------------------
            # 2) Deduct quantity row-by-row (FIFO)
            # ------------------------------------------------------------------
            remaining = quantity
            for inv in Inventory.objects.filter(
                product=product, vendor=vendor, stock_quantity__gt=0
            ).order_by("id"):
                take = min(remaining, inv.stock_quantity)
                inv.stock_quantity = F("stock_quantity") - take
                inv.save(update_fields=["stock_quantity"])
                remaining -= take
                if remaining == 0:
                    break

            # ------------------------------------------------------------------
            # 3) Create the order
            # ------------------------------------------------------------------
            order = Order.objects.create(
                user=request.user, product=product, vendor=vendor, quantity=quantity
            )

            messages.success(
                request,
                f"Order #{order.id} created successfully!",
                extra_tags="auto-dismiss page-specific",
            )
            return redirect("order_list")

        except Exception as e:
            messages.error(
                request,
                f"Error creating order: {str(e)}",
                extra_tags="auto-dismiss page-specific",
            )

    # GET ---------------------------------------------------------------
    products = Product.objects.all()
    vendors = Vendor.objects.all()
    return render(
        request, "app/add_order.html", {"products": products, "vendors": vendors}
    )


@login_required
def load_vendors(request):
    """AJAX view to load vendors based on selected product
    – sums stock when the same vendor appears more than once."""
    product_id = request.GET.get("product_id")
    if not product_id:
        return JsonResponse({"vendors": []})

    qs = (
        Inventory.objects.filter(product_id=product_id)
        .values("vendor")
        .annotate(total_stock=Sum("stock_quantity"))
        .filter(total_stock__gt=0)
    )

    vendors = [
        {
            "id": row["vendor"],
            "name": Vendor.objects.get(pk=row["vendor"]).name,
            "stock": row["total_stock"],
        }
        for row in qs
    ]
    return JsonResponse({"vendors": vendors})


@login_required
def get_stock_quantity(request):
    """AJAX view to get summed stock quantity for selected product-vendor."""
    product_id = request.GET.get("product_id")
    vendor_id = request.GET.get("vendor_id")

    if not (product_id and vendor_id):
        return JsonResponse({"stock_quantity": 0})

    total = (
        Inventory.objects.filter(product_id=product_id, vendor_id=vendor_id).aggregate(
            total=Sum("stock_quantity")
        )["total"]
        or 0
    )
    return JsonResponse({"stock_quantity": total})


# def load_vendors(request):
#     """AJAX view to load vendors based on selected product"""
#     product_id = request.GET.get('product_id')
#     vendors = []

#     if product_id:
#         # Get vendors who have stock for this product
#         inventory_items = Inventory.objects.filter(
#             product_id=product_id,
#             stock_quantity__gt=0
#         ).select_related('vendor')

#         vendors = [
#             {
#                 'id': item.vendor.id,
#                 'name': item.vendor.name,
#                 'stock': item.stock_quantity
#             }
#             for item in inventory_items if item.vendor
#         ]

#     return JsonResponse({'vendors': vendors})

# def get_stock_quantity(request):
#     """AJAX view to get stock quantity for selected product-vendor combination"""
#     product_id = request.GET.get('product_id')
#     vendor_id = request.GET.get('vendor_id')

#     stock_quantity = 0
#     if product_id and vendor_id:
#         try:
#             inventory = Inventory.objects.get(
#                 product_id=product_id,
#                 vendor_id=vendor_id
#             )
#             stock_quantity = inventory.stock_quantity
#         except Inventory.DoesNotExist:
#             stock_quantity = 0

#     return JsonResponse({'stock_quantity': stock_quantity})


@login_required
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.product_id = request.POST["product"]
        order.vendor_id = request.POST["vendor"]
        order.quantity = request.POST["qty"]
        order.save()
        return redirect("order_list")
    products = Product.objects.all()
    vendors = Vendor.objects.all()
    return render(
        request,
        "app/edit_order.html",
        {"order": order, "products": products, "vendors": vendors},
    )


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.is_cancelled = True
        order.save()
        return redirect("order_list")
    return render(request, "app/cancel_order.html", {"order": order})


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally create a UserProfile
            UserProfile.objects.create(user=user, role="staff")
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_profile.role = request.POST.get("role", user_profile.role)
        user_profile.permissions = request.POST.get(
            "permissions", user_profile.permissions
        )
        user_profile.save()

        messages.success(
            request,
            "Profile updated successfully!",
            extra_tags="auto-dismiss page-specific duration-10",
        )
        return redirect("profile")
    return render(
        request,
        "app/profile.html",
        {"user_profile": user_profile, "user": request.user},
    )
