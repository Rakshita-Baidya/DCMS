from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.shortcuts import redirect


class UnauthenticatedUser:
    def __init__(self, view_func):
        self.view_func = view_func

    def __call__(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'You are not authorized to view this page')
            return redirect('core:error')
        return self.view_func(request, *args, **kwargs)


class AllowedUsers:
    def __init__(self, allowed_roles=[]):
        self.allowed_roles = allowed_roles

    def __call__(self, view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.exists():
                user_groups = request.user.groups.values_list(
                    'name', flat=True)
                if any(group in self.allowed_roles for group in user_groups):
                    return view_func(request, *args, **kwargs)
            messages.error(request, 'You are not authorized to view this page')
            return redirect('core:error')
        return wrapper


class AdminOnly:
    def __init__(self, view_func):
        self.view_func = view_func

    def __call__(self, request, *args, **kwargs):
        if request.user.groups.exists():
            user_groups = request.user.groups.values_list('name', flat=True)
            if 'Administrator' in user_groups:
                return self.view_func(request, *args, **kwargs)
        messages.error(request, 'You are not authorized to view this page')
        return redirect('core:error')
