from django.db import models
from django.contrib.auth.models import AbstractUser, Group

# Create your models here.
ROLE_CHOICES = [
    ('Administrator', 'Administrator'),
    ('Staff', 'Staff'),
    ('Doctor', 'Doctor'),
]

# APPROVAL_STATUS = [
#     ('Pending', 'Pending'),
#     ('Approved', 'Approved'),
#     ('Rejected', 'Rejected'),
# ]


class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    contact = models.CharField(
        max_length=10, blank=True, null=True, unique=True)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES)
    # is_active = models.BooleanField(default=False)
    # is_approved = models.CharField(
    #     choices=APPROVAL_STATUS, default="Pending"
    # )
    profile_image = models.ImageField(
        upload_to='images/profile/',
        default='images/profile/default.jpg',
        blank=True,
        null=True,
    )

    # Fields specific to Staff
    position = models.CharField(max_length=100, blank=True, null=True)

    # Fields specific to Doctor
    specialization = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    nmc_no = models.CharField(max_length=5, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
