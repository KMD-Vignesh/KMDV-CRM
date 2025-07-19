from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from app.models import PurchaseOrder

@login_required
def approval_request_list(request):
    orders = PurchaseOrder.objects.filter(approval_status='PENDING')
    return render(request, 'app/approval/approval_request_list.html', {'orders': orders})


@login_required
def approval_manager_list(request):
    orders = PurchaseOrder.objects.filter(approval_status='PENDING')
    return render(request, 'app/approval/approval_manager_list.html', {'orders': orders})

@login_required
def approve_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        order.approval_status = 'APPROVED'
        order.status = 'PO_APPROVED'
        order.save()
        messages.success(request, f'Purchase Order {order.id} request approved.')
        return redirect('approval_manager_list')
    return render(request, 'app/approval/approve_purchase_order.html', {'order': order})


@login_required
def reject_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        order.approval_status = 'CANCELLED'
        order.save()
        messages.success(request, f'Purchase Order {order.id} request cancelled.')
        return redirect('approval_manager_list')
    return render(request, 'app/approval/reject_purchase_order.html', {'order': order})

@login_required
def approval_request_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'app/approval/approval_request_detail.html', {'order': order})