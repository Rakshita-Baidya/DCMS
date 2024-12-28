from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User


@receiver(post_save, sender=User)
def notify_user_on_status_change(sender, instance, created, **kwargs):
    # Check if this is an update and not a new user creation
    if not created:
        if instance.is_active:
            # User approved
            send_mail(
                subject="Account Approved",
                message=f"Dear {instance.username},\n\nYour account for DCMS has been approved. You can now log in and access the system as a {
                    instance.role.capitalize()}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
        else:
            # User denied
            send_mail(
                subject="Account Denied",
                message=f"Dear {
                    instance.username},\n\nWe regret to inform you that your account request for DCMS has been denied.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
