from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """Decorator to ensure only admin users can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            user_profile = request.user.userprofile
            if not user_profile.is_admin():
                messages.error(request, "Access denied. Admin privileges required.")
                return redirect('dashboard')
        except:
            messages.error(request, "Profile not found.")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def permission_required(page, action):
    """Decorator to check specific permissions"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                user_profile = request.user.userprofile
                if not user_profile.is_admin() and not user_profile.has_permission(page, action):
                    messages.error(request, f"Access denied. You don't have permission to {action} {page}.")
                    return redirect('dashboard')
            except:
                messages.error(request, "Profile not found.")
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator