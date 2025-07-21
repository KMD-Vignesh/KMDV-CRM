from decimal import Decimal, DivisionByZero, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from app.models import Inventory, Order, Product, Vendor



@login_required
def order_list(request):
    query = Q()

    order_id = request.GET.get("order_id")
    if order_id:
        query &= Q(id=order_id)

    product_q = request.GET.get("product")
    if product_q:
        query &= Q(product__name__icontains=product_q) | Q(
            product__product_id__icontains=product_q
        )

    quantity = request.GET.get("quantity")
    if quantity:
        query &= Q(quantity=quantity)

    vendor_q = request.GET.get("vendor")  # keep the same param name
    if vendor_q:
        query &= Q(vendor__name__icontains=vendor_q) | Q(
            vendor__vendor_id__icontains=vendor_q
        )

    order_date = request.GET.get("order_date")
    if order_date:
        parsed_date = parse_date(order_date)
        if parsed_date:
            query &= Q(order_date__date=parsed_date)

    product_price = request.GET.get("product_price")
    if product_price:
        query &= Q(product__price=product_price)

    total_price = request.GET.get("total_price")
    if total_price:
        try:
            total_price_decimal = Decimal(total_price)
            query &= Q(total_price=total_price_decimal)
        except (InvalidOperation, DivisionByZero):
            pass

    status = request.GET.get("status")
    if status == "cancelled":
        query &= Q(is_cancelled=True)
    elif status == "active":
        query &= Q(is_cancelled=False)

    # Annotate total_price for each order
    orders = (
        Order.objects.annotate(
            total_price=ExpressionWrapper(
                F("quantity") * F("product__price"),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )
        .filter(query)
        .order_by("-id")
    )

    # Aggregate total values
    orders_total = orders.aggregate(
        total_quantity=Sum("quantity"),
        active_count=Sum("quantity", filter=Q(is_cancelled=False)),
        cancelled_count=Sum("quantity", filter=Q(is_cancelled=True)),
        total_price=Sum(
            ExpressionWrapper(
                F("quantity") * F("product__price"),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        ),
    )

    return render(
        request,
        "app/order/order_list.html",
        {"orders": orders, "orders_total": orders_total},
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
        request, "app/order/add_order.html", {"products": products, "vendors": vendors}
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
            "vendor_id": Vendor.objects.get(pk=row["vendor"]).vendor_id,
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
        messages.success(
            request,
            f"Order - {order.id} updated successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("order_list")
    products = Product.objects.all()
    vendors = Vendor.objects.all()

    return render(
        request,
        "app/order/edit_order.html",
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
    return render(request, "app/order/cancel_order.html", {"order": order})
