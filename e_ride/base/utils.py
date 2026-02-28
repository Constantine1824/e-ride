from django.utils import timezone
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from datetime import datetime, timedelta
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
import time

class UrlSign:
    def __init__(self):
        self.signer = TimestampSigner()
    
    def url_encode(self, username, expires_in=timedelta(hours=24)):
        """
        Create a signed, time-limited token for the given username
        """
        value = f"{username}"
        signed_value = self.signer.sign(value)
        # Encode to make it URL-safe
        return urlsafe_base64_encode(force_bytes(signed_value))
    
    def url_decode(self, value, max_age=timedelta(hours=24)):
        """
        Verify and decode the signed token
        Raises SignatureExpired if token has expired
        Raises BadSignature if token is invalid
        """
        # Decode from URL-safe format
        decoded_bytes = urlsafe_base64_decode(value)
        signed_value = force_str(decoded_bytes)
        
        # Verify signature and check expiration
        try:
            unsigned_value = self.signer.unsign(signed_value, max_age=max_age.total_seconds())
            return unsigned_value
        except SignatureExpired:
            raise SignatureExpired("Token has expired")
        except BadSignature:
            raise BadSignature("Invalid token")