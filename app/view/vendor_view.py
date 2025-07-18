from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Vendor


@login_required
def vendor_list(request):
    vendors = Vendor.objects.all().order_by("name")
    return render(request, "app/vendor/vendor_list.html", {"vendors": vendors})


@login_required
def add_vendor(request):
    if request.method == "POST":
        vid = request.POST["vendor_id"].strip()
        name = request.POST["name"]
        address = request.POST["address"]

        if Vendor.objects.filter(vendor_id__iexact=vid).exists():
            messages.error(request, f"Vendor ID “{vid}” already exists!")
            return redirect("add_vendor")

        try:
            Vendor.objects.create(vendor_id=vid, name=name, address=address)
            messages.success(request, f"Vendor {vid} created.")
            return redirect("vendor_list")
        except IntegrityError:
            messages.error(request, f"Vendor ID “{vid}” already exists!")
            return redirect("add_vendor")

    return render(request, "app/vendor/add_vendor.html")


@login_required
def edit_vendor(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == "POST":
        vid = request.POST["vendor_id"].strip()
        name = request.POST["name"]
        address = request.POST["address"]

        if Vendor.objects.filter(vendor_id__iexact=vid).exclude(pk=pk).exists():
            messages.error(request, f"Vendor ID “{vid}” is already taken!")
            return redirect("edit_vendor", pk=pk)

        vendor.vendor_id = vid
        vendor.name = name
        vendor.address = address
        vendor.save()
        messages.success(request, f"Vendor {vid} updated.")
        return redirect("vendor_list")

    return render(request, "app/vendor/edit_vendor.html", {"vendor": vendor})


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
    return render(request, "app/vendor/delete_vendor.html", {"vendor": vendor})
