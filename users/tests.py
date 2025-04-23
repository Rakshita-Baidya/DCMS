import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import User
from .views import login


class WhiteboxUnitTestsIteration1(TestCase):
    def test_login_user_invalid_credentials(self):
        result = login(username="invalid", password="wrong")
        assert result is None, "Login should fail with invalid credentials"

    def test_user_profile_update_empty_email(self):
        user = User.objects.create(
            username="testuser", email="test@example.com")
        with pytest.raises(ValidationError):
            user.email = ""
            user.save()
