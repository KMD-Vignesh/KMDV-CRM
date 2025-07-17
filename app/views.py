
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import F, Q, Sum, DecimalField, ExpressionWrapper
from django.http import JsonResponse    
from django.shortcuts import get_object_or_404, redirect, render


from .forms import CustomUserCreationForm, UserEditForm, UserUpdateForm
from .models import Category, Inventory, Order, Product, UserProfile, Vendor
from django.contrib.auth.forms import SetPasswordForm
from django.utils.dateparse import parse_date
from decimal import Decimal, DivisionByZero, InvalidOperation

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
        messages.success(
            request,
            f"Category - {category.name} updated successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("category_list")
    return render(request, "app/edit_category.html", {"category": category})
    return render(request, "app/edit_category.html", {"category": category})


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(
            request,
            f"Category - {category.name} deleted successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("category_list")
    return render(request, "app/delete_category.html", {"category": category})


@login_required
def product_list(request):
    products = Product.objects.all().order_by('name')
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
        messages.success(
            request,
            f"Product - {name} created successfully!",
            extra_tags="auto-dismiss page-specific",
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
        messages.success(
            request,
            f"Product - {product.name} updated successfully!",
            extra_tags="auto-dismiss page-specific",
        )
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
        messages.success(
            request,
            f"Product - {product.name} deleted successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("product_list")
    return render(request, "app/delete_product.html", {"product": product})


@login_required
def vendor_list(request):
    vendors = Vendor.objects.all().order_by('name')
    return render(request, "app/vendor_list.html", {"vendors": vendors})


@login_required
def add_vendor(request):
    if request.method == "POST":
        name = request.POST["name"]
        address = request.POST["address"]
        Vendor.objects.create(name=name, address=address)
        messages.success(
            request,
            f"Vendor - {name} created successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("vendor_list")
    return render(request, "app/add_vendor.html")


@login_required
def edit_vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == "POST":
        vendor.name = request.POST["name"]
        vendor.address = request.POST["address"]
        vendor.save()
        messages.success(
            request,
            f"Vendor - {vendor.name} updated successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("vendor_list")
    return render(request, "app/edit_vendor.html", {"vendor": vendor})


@login_required
def delete_vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == "POST":
        vendor.delete()
        messages.success(
            request,
            f"Vendor - {vendor.name} deleted successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("vendor_list")
    return render(request, "app/delete_vendor.html", {"vendor": vendor})


@login_required
def inventory_list(request):
    inventory = Inventory.objects.annotate(
        total_price=ExpressionWrapper(F('stock_quantity') * F('product__price'), output_field=DecimalField(max_digits=10, decimal_places=2))
    )

    total_inward_qty = inventory.aggregate(Sum('inward_qty'))['inward_qty__sum'] or 0
    total_current_stock = inventory.aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0
    total_price = inventory.aggregate(Sum('total_price'))['total_price__sum'] or 0

    return render(request, "app/inventory_list.html", {
        "inventory": inventory,
        "total_inward_qty": total_inward_qty,
        "total_current_stock": total_current_stock,
        "total_price": total_price
    })

@login_required
def add_inventory(request):
    if request.method == "POST":
        product_id = request.POST["product"]
        vendor_id = request.POST["vendor"]
        qty = request.POST["qty"]
        Inventory.objects.create(
            product_id=product_id, vendor_id=vendor_id, stock_quantity=qty
        )
        messages.success(
            request,
            f"Inventory for Product - {product_id} for Vendor - {vendor_id} created successfully!",
            extra_tags="auto-dismiss page-specific",
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
        messages.success(
            request,
            f"Inventory for Product - {inventory.product.name} for Vendor - {inventory.vendor.name} updated successfully!",
            extra_tags="auto-dismiss page-specific",
        )
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
        messages.success(
            request,
            f"Inventory for Product - {inventory.product.name} for Vendor - {inventory.vendor.name} deleted successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("inventory_list")
    return render(request, "app/delete_inventory.html", {"inventory": inventory})


@login_required
def order_list(request):
    query = Q()
    
    order_id = request.GET.get('order_id')
    if order_id:
        query &= Q(id=order_id)
    
    product_name = request.GET.get('product')
    if product_name:
        query &= Q(product__name__icontains=product_name)
    
    quantity = request.GET.get('quantity')
    if quantity:
        query &= Q(quantity=quantity)
    
    vendor_name = request.GET.get('vendor')
    if vendor_name:
        query &= Q(vendor__name__icontains=vendor_name)
    
    order_date = request.GET.get('order_date')
    if order_date:
        parsed_date = parse_date(order_date)
        if parsed_date:
            query &= Q(order_date__date=parsed_date)
    
    product_price = request.GET.get('product_price')
    if product_price:
        query &= Q(product__price=product_price)
    
    total_price = request.GET.get('total_price')
    if total_price:
        try:
            total_price_decimal = Decimal(total_price)
            # Filter by calculated total_price
            query &= Q(total_price=total_price_decimal)
        except (InvalidOperation, DivisionByZero):
            pass
    
    status = request.GET.get('status')
    if status == 'cancelled':
        query &= Q(is_cancelled=True)
    elif status == 'active':
        query &= Q(is_cancelled=False)
    
    # Annotate total_price for each order
    orders = Order.objects.annotate(
        total_price=ExpressionWrapper(F('quantity') * F('product__price'), output_field=DecimalField(max_digits=10, decimal_places=2))
    ).filter(query).order_by('-order_date')
    
    # Aggregate total values
    orders_total = orders.aggregate(
        total_quantity=Sum("quantity"),
        active_count=Sum("quantity", filter=Q(is_cancelled=False)),
        cancelled_count=Sum("quantity", filter=Q(is_cancelled=True)),
        total_price=Sum(ExpressionWrapper(F('quantity') * F('product__price'), output_field=DecimalField(max_digits=10, decimal_places=2)))
    )
    
    return render(request, "app/order_list.html", {"orders": orders, "orders_total": orders_total})
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
                f"Order # {order.id} with Qty({order.quantity}) for Product ({product.name}) created successfully!",
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
    messages.success(
        request,
        f"Order - {order.id} updated successfully!",
        extra_tags="auto-dismiss page-specific",
    )
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
        messages.success(
            request,
            f"Order - {order.id} cancelled successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("order_list")
    return render(request, "app/cancel_order.html", {"order": order})


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
            messages.success(request, 'Account created successfully.')
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'app/profile.html', {'form': form})

get_user_model()

@login_required
def user_list(request):
    users = User.objects.all().order_by('id')
    return render(request, 'app/user_list.html', {'users': users})

@login_required
def user_add(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created!')
            return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/user_form.html', {'form': form})

@login_required
def user_edit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated.')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user_obj)
    return render(request, 'app/user_form.html', {'form': form, 'title': 'Edit'})
@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted.')
        return redirect('user_list')
    return render(request, 'app/user_confirm_delete.html', {'user': user})

@login_required
def user_reset_password(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password for {user.username} has been reset.')
            return redirect('user_list')
    else:
        form = SetPasswordForm(user)
    return render(request, 'app/user_reset_password.html',
                  {'form': form, 'user_obj': user})