# myapp/backends.py
from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import License

class MstcnlBackend(BaseBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # Use 'using' to specify the database
            user = License.objects.using('mstcnl').get(username=username)
            if check_password(password, user.password):
                return user
        except License.DoesNotExist:
            return None

    # def get_user(self, user_id):
    #     try:
    #         return License.objects.using('mstcnl').get(pk=user_id)
    #     except License.DoesNotExist:
    #         return None
