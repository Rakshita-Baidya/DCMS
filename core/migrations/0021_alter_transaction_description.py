# Generated by Django 5.1.4 on 2025-04-11 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_alter_transaction_amount_alter_transaction_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='description',
            field=models.TextField(blank=True, max_length=150, null=True),
        ),
    ]
