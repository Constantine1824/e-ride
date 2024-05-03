from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.Accounts.models import User
from base.email import send_verification_mail

@receiver(post_save, sender= User)
def send_mail(sender, instance, created, **kwargs):
    if created:
        user = instance
        print(user)
        try:
            send_verification_mail(user)
        except Exception as e:
            #This should save it in db created specially for internal application exceptions
            pass