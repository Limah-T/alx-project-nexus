from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import AccessToken
from api.models import BlaskListAccessToken
from datetime import datetime, timedelta
import jwt, os

algorithm = os.environ.get("ALGORITHM")

def encode_token(id, email):
    now = datetime.now()
    expiry_at = now + timedelta(minutes=int(os.environ.get("EXPIRY_AT")))    
    payload = {
        "iss": str(id), "sub": email,
        "iat": int(now.timestamp()), "exp": int(expiry_at.timestamp())
    }

    with open("private_key.pem", "rb") as file:
        key = file.read()
    token = jwt.encode(payload, key, algorithm)
    return token

def decode_token(token):
    with open("public_key.pem", "rb") as file:
        key = file.read()

    try:
        payload = jwt.decode(token, key, [algorithm])
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidSignatureError:
        return False
    except jwt.InvalidIssuerError:
        return False
    except jwt.InvalidAudienceError:
        return False
    except jwt.DecodeError:
        return False
    except jwt.InvalidTokenError:
        return False
    return payload

def black_list_user_tokens(user):
    user_tokens = OutstandingToken.objects.filter(user=user)
    for token in user_tokens:
        BlacklistedToken.objects.get_or_create(token=token)

def valid_access_token(auth_token):
    try:  # parse JWT
        if not BlaskListAccessToken.objects.filter(jti=auth_token).exists():
            return True   # token is valid and not blacklisted
    except Exception:
        return False      # token missing, invalid, or expired