from datetime import datetime
from django.db import models
from users.models import User

# Create your models here.
TRANSACTION_TYPE = [
    ('Income', 'Income'),
    ('Expense', 'Expense'),
    ('Payment', 'Payment'),
]


class Transaction(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='transaction_profile')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=datetime.now)
    type = models.CharField(choices=TRANSACTION_TYPE, default="Income")

    def __str__(self):
        return super().__str__()


class Patient(models.Model):
    reg_no = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=13)
    address = models.CharField(max_length=150)
    dob = models.DateField()
    gender = models.CharField(max_length=6)
    blood_group = models.CharField(max_length=3)
    age = models.CharField(max_length=3)
    email = models.EmailField()
    telephone = models.CharField()
    occupation = models.CharField()
    nationality = models.CharField()
    marital_status = models.CharField()
    photo = models.ImageField()

    def __str__(self):
        return super().__str__()

