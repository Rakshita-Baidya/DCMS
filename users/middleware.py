from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils.timezone import now
from datetime import timedelta


class TokenRefreshMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if not access_token or not refresh_token:
            return None

        try:
            token = AccessToken(access_token)
            expiry = token['exp']
            expiry_datetime = now() + timedelta(seconds=(expiry - now().timestamp()))
            if (expiry_datetime - now()) < timedelta(minutes=5):
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                new_refresh_token = str(
                    refresh) if 'refresh' in refresh else refresh_token

                request.new_access_token = new_access_token
                request.new_refresh_token = new_refresh_token
        except TokenError:
            pass

        return None

    def process_response(self, request, response):
        if hasattr(request, 'new_access_token'):
            response.set_cookie(
                key='access_token',
                value=request.new_access_token,
                httponly=True,
                secure=True,
                samesite='Lax'
            )
            response.set_cookie(
                key='refresh_token',
                value=request.new_refresh_token,
                httponly=True,
                secure=True,
                samesite='Lax'
            )
        return response
