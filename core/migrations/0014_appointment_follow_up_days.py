# Generated by Django 5.1.4 on 2025-03-22 09:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_treatmentdoctor_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='follow_up_days',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(365)]),
        ),
    ]
