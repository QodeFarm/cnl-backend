from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import User

class CustomUserBackend(BaseBackend):
    '''This is Custom Authentication logic We used this code beacuse
    our custom User model does not inherit from AbstractBaseUser,
    it does not have the check_password method. Instead, you need to 
    manually handle password checking.'''
    
    def authenticate(username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            if user and check_password(password, user.password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
