from datetime import datetime, timedelta
import jwt, os
algorithm = os.environ.get("ALGORITHM")
def encode_token(user):
    now = datetime.now()
    expiry_at = now + timedelta(minutes=int(os.environ.get("EXPIRY_AT")))    
    payload = {
        "iss": str(user.id), "sub": user.email,
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
        payload= jwt.decode(token, key, [algorithm])
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

