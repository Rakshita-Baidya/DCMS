from datetime import timezone
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
        User, on_delete=models.CASCADE, related_name='doctor_profile')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    amount = models.DecimalField()
    date = models.DateTimeField(default=timezone.now)
    type = models.CharField(choices=TRANSACTION_TYPE, default="Income")

    def __str__(self):
        return super().__str__()
