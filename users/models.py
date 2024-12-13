from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
ROLE_CHOICES = [
    ('admin', 'Administrator'),
    ('receptionist', 'Receptionist'),
    ('doctor', 'Doctor'),
]

# STATUS_CHOICES = [
#     ('Pending', 'Pending'),
#     ('Approved', 'Approved'),
#     ('Denied', 'Denied'),
# ]


class User(AbstractUser):
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    # is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return super().__str__()


# class RegistrationRequest(models.Model):

#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     status = models.CharField(
#         max_length=20, choices=STATUS_CHOICES, default='Pending')

#     def __str__(self):
#         return super().__str__()
