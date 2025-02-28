from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User


@receiver(post_save, sender=User)
def send_user_creation_email(sender, instance, created, raw, **kwargs):
    if created and not raw:
        username = instance.username
        email = instance.email

        password = getattr(instance, '_password', None)
        login_url = f"http://127.0.0.1:8000/users/login/"

        if password:
            subject = 'Welcome to the DCMS Platform!'
            message = (
                f"Dear {username},\n\n"
                f"Your account for the DCMS system has been successfully created.\n"
                f"Username: {username}\n"
                f"Password: {password}\n"
                f"Please log in here: {login_url}\n\n"
                "For security, we recommend changing your password after your first login.\n\n"
                "Best regards,\nThe DCMS Team"
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
