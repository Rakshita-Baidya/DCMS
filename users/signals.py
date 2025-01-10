from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User


@receiver(pre_save, sender=User)
def track_user_changes(sender, instance, **kwargs):
    if instance.pk:  # Only for existing users
        previous = sender.objects.get(pk=instance.pk)
        instance._is_approved_changed = previous.is_approved != instance.is_approved
    else:
        instance._is_approved_changed = False


@receiver(post_save, sender=User)
def notify_user_on_status_change(sender, instance, created, **kwargs):
    # Ensure email is sent only for updates
    if not created:
        if instance._is_approved_changed:  # Only if is_approved was updated
            if instance.is_active:
                # User approved
                send_mail(
                    subject="Account Approved",
                    message=(
                        f"Dear {
                            instance.username},\n\nYour account for DCMS has been approved. "
                        f"You can now log in and access the system as a {
                            instance.role.capitalize()}."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=False,
                )
            else:
                # User denied
                send_mail(
                    subject="Account Denied",
                    message=(
                        f"Dear {
                            instance.username},\n\nWe regret to inform you that your account request "
                        f"for DCMS has been denied."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=False,
                )
