from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from users.models import User
from users.forms import LoginForm, UserEditForm, DoctorEditForm
from django.urls import reverse


class AuthenticationAndUserTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username='testuser',
            email='test@example.com',
            role='Staff',
            first_name='Test',
            last_name='User'
        )
        self.user.set_password('password123')
        self.user.save()

    def test_login_user_invalid_credentials(self):
        user = authenticate(username='wronguser', password='wrongpassword')
        print(
            f"Test 16: authenticate('wronguser', 'wrongpassword') returned: {user}")
        self.assertIsNone(user)

    def test_user_profile_update_empty_email(self):
        form = UserEditForm(
            instance=self.user,
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': '',
                'username': 'testuser',
                'role': 'Staff',
                'position': 'Receptionist'
            }
        )

        print(f"Test 17: Form valid: {form.is_valid()}, Errors: {form.errors}")
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0],
                         'This field is required.')

    def test_view_non_existent_staff_profile(self):
        result = User.objects.filter(role='Staff', id=999).first()
        print(
            f"Test 18: Query for non-existent Staff (id=999) returned: {result}")
        self.assertIsNone(result)


class DoctorProfilesTests(TestCase):
    def setUp(self):
        self.valid_doctor_data = {
            'username': 'drsmith',
            'email': 'drsmith@example.com',
            'first_name': 'Dr.',
            'last_name': 'Smith',
            'role': 'Doctor',
            'specialization': 'Cardiology',
            'qualification': 'MD',
            'nmc_no': '12345',
            'type': 'Regular'
        }

    def test_add_doctor_invalid_nmc_number(self):
        form_data = self.valid_doctor_data.copy()
        form_data['nmc_no'] = ''  # Empty nmc_no
        form = DoctorEditForm(data=form_data)
        print(f"Test 10: Form valid: {form.is_valid()}, Errors: {form.errors}")
        self.assertFalse(form.is_valid())
        self.assertIn('nmc_no', form.errors)
        self.assertEqual(form.errors['nmc_no'][0],
                         'NMC number is required for Doctors.')

    def test_view_non_existent_doctor_profile(self):
        result = User.objects.filter(role='Doctor', id=999).first()
        print(
            f"Test 11: Query for non-existent Doctor (id=999) returned: {result}")
        self.assertIsNone(result)
