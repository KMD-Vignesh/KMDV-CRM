from decimal import Decimal, DivisionByZero, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods
from django.db import transaction
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

    vendor_q = request.GET.get("vendor")
    if vendor_q:
        query &= Q(vendor__name__icontains=vendor_q) | Q(
            vendor__vendor_id__icontains=vendor_q
        )

    order_date = request.GET.get("order_date")
    if order_date:
        try:
            parsed_date = parse_date(order_date)
            query &= Q(order_date__date=parsed_date)
        except ValueError:
            pass

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
    if status:
        query &= Q(status=status)

    # Annotate total_price once
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

    # 1) Overall aggregates
    orders_total = orders.aggregate(
        total_quantity=Sum("quantity"),
        grand_total_price=Sum("total_price"),
    )

    # 2) Quantity totals per status (flat dict for template)
    status_totals = dict(
        orders.values("status")
        .annotate(qty=Sum("quantity"))
        .values_list("status", "qty")
    )

    return render(
        request,
        "app/order/order_list.html",
        {
            "orders": orders,
            "orders_total": orders_total,
            "status_totals": status_totals,
            "status_choices": Order.STATUS_CHOICES,
        },
    )


@login_required
@transaction.atomic
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
@transaction.atomic
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    original_qty = order.quantity

    # statuses to hide if order is already approved
    DISALLOWED_AFTER_APPROVAL = {"ORDER_RAISED", "ORDER_REJECTED"}

    if order.approval_status == "APPROVED":
        allowed_status = [(k, v) for k, v in Order.STATUS_CHOICES
                          if k not in DISALLOWED_AFTER_APPROVAL]
    else:
        allowed_status = []   # template will not render the dropdown

    if request.method == "POST":
        # ---------- 1) “Request Approval” button ----------
        if "request_approval" in request.POST:
            order.approval_status = "PENDING"
            order.save(update_fields=["approval_status"])
            messages.success(
                request,
                f"Approval re-requested for Order #{order.id}.",
                extra_tags="auto-dismiss page-specific",
            )
            return redirect("edit_order", pk=pk)

        # ---------- 2) normal save ----------
        product_id = int(request.POST["product"])
        vendor_id  = int(request.POST["vendor"])
        new_qty    = int(request.POST["qty"])

        product = get_object_or_404(Product, pk=product_id)
        vendor  = get_object_or_404(Vendor, pk=vendor_id)

        # editable stock = physical stock + what this order already holds
        current_stock = (
            Inventory.objects.filter(product=product, vendor=vendor)
            .aggregate(total=Sum("stock_quantity"))["total"] or 0
        )
        available = current_stock + original_qty

        if new_qty > available:
            messages.error(
                request,
                f"Insufficient stock. Available for edit: {available}, Requested: {new_qty}",
                extra_tags="auto-dismiss page-specific",
            )
            return redirect("edit_order", pk=pk)

        # restore old qty to inventory (FIFO reverse)
        restore = original_qty
        for inv in Inventory.objects.filter(
            product=order.product, vendor=order.vendor
        ).order_by("id"):
            give = min(restore, inv.stock_quantity + restore)
            inv.stock_quantity = F("stock_quantity") + give
            inv.save(update_fields=["stock_quantity"])
            restore -= give
            if restore == 0:
                break

        # deduct new qty from inventory (FIFO forward)
        deduct = new_qty
        for inv in Inventory.objects.filter(
            product=product, vendor=vendor, stock_quantity__gt=0
        ).order_by("id"):
            take = min(deduct, inv.stock_quantity)
            inv.stock_quantity = F("stock_quantity") - take
            inv.save(update_fields=["stock_quantity"])
            deduct -= take
            if deduct == 0:
                break

        # update order
        order.product_id = product_id
        order.vendor_id  = vendor_id
        order.quantity   = new_qty
        if allowed_status:  # only when dropdown was shown
            order.status = request.POST["status"]
        order.save()

        messages.success(
            request,
            f"Order {order.id} updated successfully!",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("order_list")

    # GET ---------------------------------------------------------------
    products = Product.objects.all()
    vendors  = Vendor.objects.all()
    return render(
        request,
        "app/order/edit_order.html",
        {
            "order": order,
            "products": products,
            "vendors": vendors,
            "allowed_status": allowed_status,
        },
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


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        # 1. Restore stock (FIFO)
        remaining = order.quantity
        inventories = (
            Inventory.objects
            .filter(product=order.product, vendor=order.vendor)
            .order_by("id")
        )
        for inv in inventories:
            add = min(remaining, inv.stock_quantity + remaining)
            inv.stock_quantity = F("stock_quantity") + add
            inv.save(update_fields=["stock_quantity"])
            remaining -= add
            if remaining == 0:
                break

        # 2. Delete the order
        order.delete()

        messages.success(
            request,
            f"Order {order.id} deleted and stock restored.",
            extra_tags="auto-dismiss page-specific",
        )
        return redirect("order_list")

    # GET: show confirmation page
    return render(request, "app/order/delete_order.html", {"order": order})
