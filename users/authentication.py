from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import RegistrationRequest


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user, auth = super().authenticate(request)
        try:
            reg_request = RegistrationRequest.objects.get(user=user)

            if reg_request.status == 'Pending':
                raise AuthenticationFailed(
                    'Your registration is still pending. Please wait for approval.')
            elif reg_request.status == 'Denied':
                raise AuthenticationFailed('Your registration was denied.')

            if reg_request.status == 'Approved':
                user.is_active = True
                user.save()

        except RegistrationRequest.DoesNotExist:
            raise AuthenticationFailed(
                'User registration request was not found.')

        return user, auth
