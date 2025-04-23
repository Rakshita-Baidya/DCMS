from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden

User = get_user_model()


def jwt_required(login_url='login'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            access_token = request.COOKIES.get('access_token')
            if not access_token:
                messages.error(request, 'Please log in to access this page.')
                return redirect(login_url)

            try:
                token = AccessToken(access_token)
                token.verify()
                user_id = token['user_id']
                user = User.objects.get(id=user_id)
                request.user = user
            except (InvalidToken, TokenError, User.DoesNotExist):
                if hasattr(request, 'new_access_token'):
                    try:
                        token = AccessToken(request.new_access_token)
                        user_id = token['user_id']
                        user = User.objects.get(id=user_id)
                        request.user = user
                    except (InvalidToken, TokenError, User.DoesNotExist):
                        messages.error(
                            request, 'Session expired or invalid. Please log in again.')
                        response = redirect(login_url)
                        response.delete_cookie('access_token')
                        response.delete_cookie('refresh_token')
                        return response
                else:
                    messages.error(
                        request, 'Session expired or invalid. Please log in again.')
                    response = redirect(login_url)
                    response.delete_cookie('access_token')
                    response.delete_cookie('refresh_token')
                    return response

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class UnauthenticatedUser:
    def __init__(self, view_func):
        self.view_func = view_func

    def __call__(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access_token')
        if access_token:
            try:
                token = AccessToken(access_token)
                token.verify()
                messages.error(request, 'You are already logged in.')
                return redirect('core:dashboard')
            except (InvalidToken, TokenError):
                pass
        return self.view_func(request, *args, **kwargs)


class AllowedUsers:
    def __init__(self, allowed_roles=[]):
        self.allowed_roles = allowed_roles

    def __call__(self, view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user:
                messages.error(request, 'Not authenticated.')
                return redirect('core:error')

            if request.user.role in self.allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'You are not authorized to view this page')
            return redirect('core:error')
        return wrapper


class AdminOnly:
    def __init__(self, view_func):
        self.view_func = view_func

    def __call__(self, request, *args, **kwargs):
        if not hasattr(request, 'user') or not request.user:
            messages.error(request, 'Not authenticated.')
            return redirect('core:error')

        if request.user.role == 'Administrator':
            return self.view_func(request, *args, **kwargs)
        messages.error(request, 'You are not authorized to view this page')
        return redirect('core:error')
