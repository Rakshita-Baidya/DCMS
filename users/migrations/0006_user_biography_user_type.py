# Generated by Django 5.1.4 on 2025-04-17 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_email_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='biography',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='type',
            field=models.CharField(blank=True, choices=[('On-Call', 'On-Call'), ('Regular', 'Regular'), ('Other', 'Other')], max_length=10, null=True),
        ),
    ]
