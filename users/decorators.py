from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(
                request, 'You are not authorized to view this page')
            return redirect('core:error')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request, 'You are not authorized to view this page')
                return redirect('core:error')
        return wrapper_func
    return decorator


def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name

        if group == 'Doctor' or group == 'Staff':
            messages.error(
                request, 'You are not authorized to view this page')
            return redirect('core:error')

        if group == 'Administrator':
            return view_func(request, *args, **kwargs)

    return wrapper_function
