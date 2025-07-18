from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from app.forms import CustomUserCreationForm, UserEditForm


@login_required
def user_list(request):
    users = User.objects.select_related("userprofile").all().order_by("id")
    return render(request, "app/user/user_list.html", {"users": users})


@login_required
def user_add(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created!")
            return redirect("user_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "app/user/user_form.html", {"form": form})


@login_required
def user_edit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated.")
            return redirect("user_list")
    else:
        form = UserEditForm(instance=user_obj)
    return render(request, "app/user/user_form.html", {"form": form, "title": "Edit"})


@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted.")
        return redirect("user_list")
    return render(request, "app/user/user_confirm_delete.html", {"user": user})


@login_required
def user_reset_password(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Password for {user.username} has been reset.")
            return redirect("user_list")
    else:
        form = SetPasswordForm(user)
    return render(
        request, "app/user/user_reset_password.html", {"form": form, "user_obj": user}
    )
