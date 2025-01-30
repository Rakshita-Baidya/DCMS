from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Staff, Doctor


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'address', 'contact', 'username',
                  'email', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['position']


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'qualification', 'nmc_no']

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'address', 'contact', 'email']
