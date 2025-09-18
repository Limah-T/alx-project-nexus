from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from api.models import CustomUser
from datetime import timedelta
from django.utils import timezone
import os

def check_email_id_exist_in_token(email, id):
    # This function is great for registration confirmation because email hasn't been verified yet
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

def black_list_user_tokens(user):
    user_tokens = OutstandingToken.objects.filter(user=user)
    for token in user_tokens:
        BlacklistedToken.objects.get_or_create(token=token)
        token.delete()

