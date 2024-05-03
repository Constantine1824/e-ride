from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import threading
from .utils import UrlSign
from django.conf import settings

class EmailThread(threading.Thread):

    def __init__(self, email,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email = email

    def run(self):
        self.email.send()

encoder = UrlSign()

def send_verification_mail(user):
    to = user.email
    encode = encoder.url_encode(user.username)
    context = {
        "url" : f'{settings.BASE_URL}/{encode}'
    }
    message = render_to_string('emails/verify-mail.html', context=context)
    email = EmailMessage(subject="Confirm your email for e-ride signup", to=[to], body=message)
    email.content_subtype = 'html'
    thread = EmailThread(email)
    thread.start()