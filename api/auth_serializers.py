from rest_framework import serializers
from rest_framework_simplejwt import serializers as JWT_SERIALIZER
from django.core.validators import MinLengthValidator
from django.contrib.auth import authenticate

from phonenumber_field.serializerfields import PhoneNumberField

from django.utils import timezone
from datetime import datetime
from .models import CustomUser
import email_validator, os

class CustomerRegSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(
                            validators=[MinLengthValidator(2)], max_length=50, 
                            trim_whitespace=True)
    last_name = serializers.CharField(
                            validators=[MinLengthValidator(2)], max_length=50, 
                            trim_whitespace=True)
    email = serializers.EmailField(trim_whitespace=True)
    phone_number = PhoneNumberField(region=None, trim_whitespace=True,
                                     help_text="Provide phone number in this format starting with + (e.g., +234, +233), else it will default to +234")
    address = serializers.CharField(validators=[MinLengthValidator(5)], max_length=255, trim_whitespace=True)
    password = serializers.CharField(
                                validators=[MinLengthValidator(8)],
                                max_length=int(os.environ.get('PASSWORD_LENGTH')),
                                write_only=True, style={'input_type': 'password'}
    )

    def validate_email(self, value):
        email = value.lower()
        try:
            valid_email = email_validator.validate_email(email, check_deliverability=True)
        except email_validator.EmailNotValidError as e:
            raise serializers.ValidationError({"error": str(e)})
        if CustomUser.objects.filter(email=valid_email.normalized).exists():
            raise serializers.ValidationError("Email already exist.")
        return valid_email.normalized
    
    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exist.")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        nothing_to_update = True
        email =  validated_data.get("email", instance.email)
        phone_number = validated_data.get("phone_number", instance.phone_number)
        for field, value in validated_data.items():
            if field in ["email", "phone_number", "password"]:
                continue
            if value != getattr(instance, field):
                setattr(instance, field, value) 
                nothing_to_update = False
        
        if email != instance.email:        
            if CustomUser.objects.exclude(id=instance.id).filter(email=email).exists():
                raise serializers.ValidationError({"error": "Email already exist."})
            instance.pending_email = email
            nothing_to_update = False  
        if phone_number != instance.phone_number: 
            if CustomUser.objects.exclude(id=instance.id).filter(phone_number=phone_number).exists():
                raise serializers.ValidationError({"error": "Phone number already exist."})
            instance.phone_number = phone_number
            nothing_to_update = False 
        if nothing_to_update:
            raise serializers.ValidationError({"error": "Nothing to update."})
        instance.save()
        return instance
    
class VendorRegSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(
                            validators=[MinLengthValidator(2)], max_length=50, 
                            trim_whitespace=True)
    last_name = serializers.CharField(
                            validators=[MinLengthValidator(2)], max_length=50, 
                            trim_whitespace=True)
    email = serializers.EmailField(trim_whitespace=True)
    phone_number = PhoneNumberField(region=None, trim_whitespace=True,
                                     help_text="Provide phone number in this format starting with +country code (e.g., +234, +233")
    business_address = serializers.CharField(validators=[MinLengthValidator(5)], max_length=255, trim_whitespace=True)
    business_name = serializers.CharField(validators=[MinLengthValidator(5)], max_length=255, trim_whitespace=True)
    password = serializers.CharField(
                            validators=[MinLengthValidator(8)], 
                            max_length=int(os.environ.get('PASSWORD_LENGTH')),
                            write_only=True, style={'input_type': 'password'}
    )

    def validate_email(self, value):
        email = value.lower()
        try:
            valid_email = email_validator.validate_email(email, check_deliverability=True)
        except email_validator.EmailNotValidError as e:
            raise serializers.ValidationError(str(e))
        if CustomUser.objects.filter(email=valid_email.normalized).exists():
            raise serializers.ValidationError("Email already exist.")
        return valid_email.normalized
    
    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exist.")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.role = "vendor"
        user.save()
        return user
    
    def update(self, instance, validated_data):
        nothing_to_update = True
        email =  validated_data.get("email", instance.email)
        phone_number = validated_data.get("phone_number", instance.phone_number)
        for field, value in validated_data.items():
            if field in ["email", "phone_number", "password"]:
                continue
            if value != getattr(instance, field):
                setattr(instance, field, value) 
                nothing_to_update = False
        
        if email != instance.email:        
            if CustomUser.objects.exclude(id=instance.id).filter(email=email).exists():
                raise serializers.ValidationError({"error": "Email already exist."})
            instance.pending_email = email
            nothing_to_update = False  
        if phone_number != instance.phone_number: 
            if CustomUser.objects.exclude(id=instance.id).filter(phone_number=phone_number).exists():
                raise serializers.ValidationError({"error": "Phone number already exist."})
            instance.phone_number = phone_number
            nothing_to_update = False 
        if nothing_to_update:
            raise serializers.ValidationError({"error": "Nothing to update."})
        instance.save()
        return instance

class LoginSerializer(JWT_SERIALIZER.TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
        
    def validate(self, attrs):
        data = super().validate(attrs)
        email = attrs['email'].lower()
        try:
            valid_email = email_validator.validate_email(email, check_deliverability=False)
            email = CustomUser.objects.get(email=valid_email.normalized, is_active=True)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Email does not exist.')
        user = authenticate(email=email, password=attrs['password'])
        if not user:
            raise serializers.ValidationError({"error": "Could not log in with the provided credentials"})
        if not user.email_verified:
            raise serializers.ValidationError({"error": "Email has not been verified"})
        if not user.is_active:
            raise serializers.ValidationError({"error": "User's account has been deactivated."})
        self.user = user
        data.update({'user': self.user})
        return data

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        email = value.lower()
        try:
            valid_email = email_validator.validate_email(email, check_deliverability=False)
            user = CustomUser.objects.get(email=valid_email.normalized, is_active=True)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Email does not exist.')
        return user

class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(
                                validators=[MinLengthValidator(8)], 
                                max_length=int(os.environ.get('PASSWORD_LENGTH')), 
                                write_only=True, style={'input_type': 'password'}
    )  

    def validate_email(self, value):
        email = value.lower()
        try:
            valid_email = email_validator.validate_email(email, check_deliverability=False)
            user = CustomUser.objects.get(email=valid_email.normalized, is_active=True)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Email does not exist.')
        if not user.reset_password:
            raise serializers.ValidationError("Please request for email to reset your password")
        if timezone.now() > user.time_reset:
            user.time_reset = None
            user.reset_password = False
            user.save(update_fields=["time_reset", "reset_password"])
            raise serializers.ValidationError("Reset time has expired")
        return user
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(
                                validators=[MinLengthValidator(8)], 
                                max_length=int(os.environ.get('PASSWORD_LENGTH')), 
                                write_only=True, style={'input_type': 'password'}
    )


"""**********************************Profile Section******************************************"""
class CustomerProfileSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(
                            validators=[MinLengthValidator(2)], max_length=50, 
                            trim_whitespace=True, required=False)
    last_name = serializers.CharField(
                            validators=[MinLengthValidator(2)], max_length=50, 
                            trim_whitespace=True, required=False)
    email = serializers.EmailField(trim_whitespace=True, required=False)
    phone_number = PhoneNumberField(region=None, trim_whitespace=True, required=False,
                                     help_text="Provide phone number in this format starting with + (e.g., +234, +233), else it will default to +234")
    address = serializers.CharField(validators=[MinLengthValidator(5)], max_length=255, required=False,
                                    trim_whitespace=True)

    def validate_email(self, value):
        email = value.lower()
        try:
            valid_email = email_validator.validate_email(email, check_deliverability=True)
        except email_validator.EmailNotValidError as e:
            raise serializers.ValidationError({"error": str(e)})
        return valid_email.normalized
       
    def update(self, instance, validated_data):
        nothing_to_update = True
        email =  validated_data.get("email", instance.email)
        phone_number = validated_data.get("phone_number", instance.phone_number)
        for field, value in validated_data.items():
            if field in ["email", "phone_number"]:            
                continue
            if field in ["first_name", "last_name"]:
                value = value.title()
            if value != getattr(instance, field):
                setattr(instance, field, value) 
                nothing_to_update = False
        
        if email != instance.email:        
            if CustomUser.objects.exclude(id=instance.id).filter(email=email).exists():
                raise serializers.ValidationError({"error": "Email already exist."})
            instance.pending_email = email
            nothing_to_update = False  
        if phone_number != instance.phone_number: 
            if CustomUser.objects.exclude(id=instance.id).filter(phone_number=phone_number).exists():
                raise serializers.ValidationError({"error": "Phone number already exist."})
            instance.phone_number = phone_number
            nothing_to_update = False 
        if nothing_to_update:
            raise serializers.ValidationError({"error": "Nothing to update."})
        instance.save()
        return instance