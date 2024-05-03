from django.utils import timezone
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from datetime import datetime

class UrlSign:
    def urlsafe_encode(self,value:str):
        value_bytes = force_bytes(value, encoding='utf-8')
        return urlsafe_base64_encode(value_bytes)
    
    def urlsafe_decode(self,value:bytes):
        decoded_bytes = urlsafe_base64_decode(value)
        return force_str(decoded_bytes)
    
    def time_to_str(self,value:datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    
    def str_to_time(self,value:str):
        return datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
    
    def url_encode(self, username):
        current_time = datetime.now()
        str_time = self.time_to_str(current_time)
        value = f'{username}!{str_time}'
        return self.urlsafe_encode(value)
    
    def url_decode(self, value):
        str_val = self.urlsafe_decode(value)
        username, time = str_val.split('!')
        return username