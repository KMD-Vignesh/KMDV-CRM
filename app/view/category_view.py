from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Category


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(
        request, "app/category/category_list.html", {"categories": categories}
    )


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
    return render(request, "app/category/add_category.html")


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
    return render(request, "app/category/edit_category.html", {"category": category})


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
    return render(request, "app/category/delete_category.html", {"category": category})
