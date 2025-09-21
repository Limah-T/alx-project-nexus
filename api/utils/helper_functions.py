from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import AccessToken
from api.models import CustomUser, BlaskListAccessToken
from datetime import timedelta
from django.utils import timezone
import os

def check_email_id_exist_in_token(email, id):
    try:
        user = CustomUser.objects.get(email=email, is_active=True)
    except CustomUser.DoesNotExist:
        return False
    if str(user.id) != id:
        return False
    return user

def set_user_password_reset_time(user):
    if not user.email_verified:
        return False
    extra_time = timedelta(minutes=int(os.environ.get("RESET_TIME")))
    user.reset_password= True
    user.time_reset= timezone.now() + extra_time
    user.save(update_fields=['reset_password', 'time_reset'])
    return True

def check_if_admin(user):
    if not user.email_verified:
        return False
    if not user.is_active:
        return False
    if not user.is_superuser:
        return False
    return True

def request_instance(request_body):
    many = True
    if not isinstance(request_body.data, list):
        many = False
        return many
    else:
        return many