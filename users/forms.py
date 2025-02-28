from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, ROLE_CHOICES


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'address', 'contact',
                  'role', 'profile_image', 'position', 'specialization', 'qualification', 'nmc_no']
        widgets = {
            'role': forms.Select(choices=ROLE_CHOICES),
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        # Role-specific validation
        if role == 'Doctor':
            if not cleaned_data.get('specialization'):
                self.add_error('specialization',
                               "Specialization is required for Doctors.")
            if not cleaned_data.get('nmc_no'):
                self.add_error('nmc_no', "NMC number is required for Doctors.")
            if not cleaned_data.get('qualification'):
                self.add_error('qualification',
                               "Qualification is required for Doctors.")
        elif role == 'Staff':
            if not cleaned_data.get('position'):
                self.add_error('position', "Position is required for Staff.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'address',
                  'contact', 'username', 'email', 'profile_image', 'role', 'specialization', 'qualification', 'nmc_no', 'position']
