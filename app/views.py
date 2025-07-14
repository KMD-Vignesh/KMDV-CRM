from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Inventory, Vendor, Order, UserProfile
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib import messages

@login_required
def dashboard(request):
    products_count = Product.objects.count()
    inventory_summary = list(Inventory.objects.values('product__name').annotate(total=Sum('stock_quantity')))
    products = Product.objects.all()
    categories = Category.objects.all()
    inventory = Inventory.objects.all()
    return render(request, 'app/dashboard.html', {
        'products_count': products_count,
        'inventory_summary': inventory_summary,
        'products': products,
        'categories': categories,
        'inventory': inventory
    })

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'app/category_list.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST.get('description', '')
        Category.objects.create(name=name, description=description)
        return redirect('category_list')
    return render(request, 'app/add_category.html')

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST['name']
        category.description = request.POST.get('description', '')
        category.save()
        return redirect('category_list')
    return render(request, 'app/edit_category.html', {'category': category})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'app/delete_category.html', {'category': category})

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'app/product_list.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        category_id = request.POST['category']
        price = request.POST['price']
        description = request.POST.get('description', '')
        Product.objects.create(name=name, category_id=category_id, price=price, description=description)
        return redirect('product_list')
    categories = Category.objects.all()
    return render(request, 'app/add_product.html', {'categories': categories})

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.category_id = request.POST['category']
        product.price = request.POST['price']
        product.description = request.POST.get('description', '')
        product.save()
        return redirect('product_list')
    categories = Category.objects.all()
    return render(request, 'app/edit_product.html', {'product': product, 'categories': categories})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'app/delete_product.html', {'product': product})

@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'app/vendor_list.html', {'vendors': vendors})

@login_required
def add_vendor(request):
    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        Vendor.objects.create(name=name, address=address)
        return redirect('vendor_list')
    return render(request, 'app/add_vendor.html')

@login_required
def edit_vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.name = request.POST['name']
        vendor.address = request.POST['address']
        vendor.save()
        return redirect('vendor_list')
    return render(request, 'app/edit_vendor.html', {'vendor': vendor})

@login_required
def delete_vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.delete()
        return redirect('vendor_list')
    return render(request, 'app/delete_vendor.html', {'vendor': vendor})

@login_required
def inventory_list(request):
    inventory = Inventory.objects.all()
    return render(request, 'app/inventory_list.html', {'inventory': inventory})

@login_required
def add_inventory(request):
    if request.method == 'POST':
        product_id = request.POST['product']
        vendor_id = request.POST['vendor']
        qty = request.POST['qty']
        Inventory.objects.create(product_id=product_id, vendor_id=vendor_id, stock_quantity=qty)
        return redirect('inventory_list')
    products = Product.objects.all()
    vendors = Vendor.objects.all()
    return render(request, 'app/add_inventory.html', {'products': products, 'vendors': vendors})

@login_required
def edit_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        inventory.product_id = request.POST['product']
        inventory.vendor_id = request.POST['vendor']
        inventory.stock_quantity = request.POST['qty']
        inventory.save()
        return redirect('inventory_list')
    products = Product.objects.all()
    vendors = Vendor.objects.all()
    return render(request, 'app/edit_inventory.html', {'inventory': inventory, 'products': products, 'vendors': vendors})

@login_required
def delete_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        inventory.delete()
        return redirect('inventory_list')
    return render(request, 'app/delete_inventory.html', {'inventory': inventory})

@login_required
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'app/order_list.html', {'orders': orders})

@login_required
def add_order(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        vendor_id = request.POST.get('vendor')
        qty = request.POST.get('qty')
        if not qty or not qty.isdigit():
            messages.error(request, "Invalid quantity. Please enter a valid number.")
            return redirect('add_order')
        qty = int(qty)  # Convert to integer
        product = get_object_or_404(Product, id=product_id)
        vendor = get_object_or_404(Vendor, id=vendor_id) if vendor_id else None
        order = Order(user=request.user, product=product, vendor=vendor, quantity=qty)
        order.save()
        messages.success(request, "Order added successfully!")
        return redirect('order_list')
    else:
        products = Product.objects.all()
        vendors = Vendor.objects.all()
        return render(request, 'app/add_order.html', {'products': products, 'vendors': vendors})
    
@login_required
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.product_id = request.POST['product']
        order.vendor_id = request.POST['vendor']
        order.quantity = request.POST['qty']
        order.save()
        return redirect('order_list')
    products = Product.objects.all()
    vendors = Vendor.objects.all()
    return render(request, 'app/edit_order.html', {'order': order, 'products': products, 'vendors': vendors})

@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.is_cancelled = True
        order.save()
        return redirect('order_list')
    return render(request, 'app/cancel_order.html', {'order': order})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally create a UserProfile
            UserProfile.objects.create(user=user, role='staff')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_profile.role = request.POST.get('role', user_profile.role)
        user_profile.permissions = request.POST.get('permissions', user_profile.permissions)
        user_profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    return render(request, 'app/profile.html', {'user_profile': user_profile, 'user': request.user})

