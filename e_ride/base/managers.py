from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, email, password, username, **kwargs):
        user= self.model(email=email, username=username, **kwargs)
        user.set_password(password)
        user.save()
        return user
    
    def create_user(self, email, password, username, **kwargs):
        if not username:
            raise ValueError('Users must have a username')
        
        if not email:
            raise ValueError('Email must be set for users')
        
        
        kwargs.setdefault('is_superuser', False)
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_active', False)
        email = self.normalize_email(email)
        return self._create(email, password, username, **kwargs)

    def create_superuser(self, email, password, username, **kwargs):
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_active', True) 

        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must be set for superuser accounts')

        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must be set for staff accounts')
        
        email = self.normalize_email(email)

        return self._create(email, password, username, **kwargs)  