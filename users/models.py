from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
ROLE_CHOICES = [
    ('admin', 'Administrator'),
    ('staff', 'Staff'),
    ('doctor', 'Doctor'),
]


class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    address = models.CharField(max_length=200, blank=True, null=True)
    contact = models.CharField(max_length=10, blank=True, null=True)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_approved = models.CharField(default="Pending")

    def __str__(self):
        return super().__str__()


class Staff(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='staff_profile')
    position = models.CharField(max_length=100)

    def __str__(self):
        return super().__str__()


class Doctor(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    nmc_no = models.CharField(max_length=5)

    def __str__(self):
        return super().__str__()
