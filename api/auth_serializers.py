from rest_framework import serializers
from django.core.validators import MinLengthValidator
from phonenumber_field.serializerfields import PhoneNumberField

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

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_email(self, value):
        email = value.lower()
        try:
            valid_email = email_validator.validate_email(email, check_deliverability=False)
            email = CustomUser.objects.get(email=valid_email.normalized)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Email does not exist.')
        return email

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        email = value.lower()
        try:
            valid_email = email_validator.validate_email(email, check_deliverability=False)
            email = CustomUser.objects.get(email=valid_email.normalized)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Email does not exist.')
        return email

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
            user = CustomUser.objects.get(email=valid_email.normalized)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Email does not exist.')
        return user
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(
                                validators=[MinLengthValidator(8)], 
                                max_length=int(os.environ.get('PASSWORD_LENGTH')), 
                                write_only=True, style={'input_type': 'password'}
    )
