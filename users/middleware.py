from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils.timezone import now
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class TokenRefreshMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if not access_token or not refresh_token:
            logger.debug("No access or refresh token found in cookies.")
            return None

        try:
            token = AccessToken(access_token)
            expiry = token['exp']
            expiry_datetime = now().fromtimestamp(expiry, tz=now().tzinfo)
            time_until_expiry = expiry_datetime - now()

            if time_until_expiry < timedelta(minutes=5):
                logger.debug("Access token near expiry, attempting refresh.")
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                new_refresh_token = str(refresh)

                request.new_access_token = new_access_token
                request.new_refresh_token = new_refresh_token
                logger.info("New access and refresh tokens generated.")
            else:
                logger.debug(
                    f"Access token still valid for {time_until_expiry}.")
        except TokenError as e:
            logger.error(f"Token error: {str(e)}")
            request.clear_tokens = True

        return None

    def process_response(self, request, response):
        if hasattr(request, 'clear_tokens') and request.clear_tokens:
            logger.info("Clearing invalid tokens from cookies.")
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
        elif hasattr(request, 'new_access_token'):
            logger.info("Setting new tokens in cookies.")
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
