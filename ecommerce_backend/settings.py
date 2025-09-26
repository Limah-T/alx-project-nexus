from pathlib import Path
import environ, os
from datetime import timedelta

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env( os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG')

ALLOWED_HOSTS = [env('ALLOWED_HOSTS')]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary',
    'django.contrib.staticfiles',
    'api',
    
    # Third part apps
    'rest_framework_simplejwt.token_blacklist',
    'phonenumber_field', 
    'django_filters',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce_backend.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': env('ENGINE'),
        'NAME': env('NAME'),
        'USER': env('USER'),
        'PASSWORD': env('PASSWORD'),
        'HOST': env('HOST'),
        'PORT': env('PORT')
    }
}

# Email configuration
EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_SSL = bool(env("EMAIL_USE_SSL"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'api.CustomUser'

# Rest framework authentication and permission configurations
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':[ 
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

with open("private_key.pem", "rb") as file:
    private_key = file.read()

with open("public_key.pem", "rb") as file:
    public_key = file.read()

# SimpleJWT configuration 
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(env("ACCESS_TOKEN_LIFETIME"))),  
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(env("REFRESH_TOKEN_LIFETIME"))),    
    "ROTATE_REFRESH_TOKENS": bool(env("ROTATE_REFRESH_TOKENS")),      
    "BLACKLIST_AFTER_ROTATION": bool(env("BLACKLIST_AFTER_ROTATION")),  
    "UPDATE_LAST_LOGIN": bool(env("UPDATE_LAST_LOGIN")),      

    "ALGORITHM": env("HASH_KEY"),
    "SIGNING_KEY": private_key,
    "VERIFYING_KEY": public_key,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": env("USER_ID_FIELD"),
    "USER_ID_CLAIM": env("USER_ID_CLAIM"),
    "TOKEN_OBTAIN_SERIALIZER": "api.auth_serializers.LoginSerializer",
}

# Cloudinary configuration

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env("CLOUDINARY_NAME"),
    "API_KEY": env("CLOUDINARY_API_KEY"),
    "API_SECRET": env("CLOUDINARY_API_SECRET")
}

MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Redis for caching
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis",
#         "LOCATION": env("REDIS_URL"),
#     }
# }