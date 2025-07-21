from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm, UserUpdateForm
from .models import Category, Inventory, Order, Product, UserProfile


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

    # NEW / UPDATED AGGREGATES
    total_inward_qty = (
        Inventory.objects.aggregate(total=Sum("inward_qty"))["total"] or 0
    )

    total_order_price = (
        Order.objects.aggregate(total=Sum(F("quantity") * F("product__price")))["total"]
        or 0
    )

    total_stock_price = (
        Inventory.objects.aggregate(
            total=Sum(F("stock_quantity") * F("product__price"))
        )["total"]
        or 0
    )

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
        "total_inward_qty": total_inward_qty,
        "total_order_price": total_order_price,
        "total_stock_price": total_stock_price,
    }

    return render(request, "app/base/dashboard.html", context)


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create profile with the new data
            UserProfile.objects.create(
                user=user,
                role="staff",
                # if you store first/last name in profile you can copy them here
            )
            messages.success(request, "Account created successfully.")
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated!")
            return redirect("profile")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, "app/base/profile.html", {"form": form})
