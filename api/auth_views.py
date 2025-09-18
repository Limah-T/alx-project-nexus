from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import check_password

from .auth_serializers import CustomerRegSerializer, VendorRegSerializer, LoginSerializer, ResetPasswordSerializer, SetPasswordSerializer, ChangePasswordSerializer
from .utils.token import encode_token, decode_token
from .utils.helper_functions import check_email_id_exist_in_token, set_user_password_reset_time, black_list_user_tokens
from .models import CustomUser
from .tasks import send_email
from datetime import datetime, timedelta
import os

class CustomerRegView(APIView):
    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = []
    serializer_class = CustomerRegSerializer

    def post(self, request, *args, **kwargs):    
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = encode_token(user)
        verification_link = f"{os.environ.get("APP_DOMAIN")}/verify_email/register?token={token}"
        send_email(
            subject="Verify your email",
            txt_template="api/text_mails/signup_verification.txt",
            html_template="api/signup_verification.html",
            context={"verification_link": verification_link},
            user=user
        )
        return Response({'message': 'please check your email for verification'}, status=status.HTTP_200_OK)

class VendorRegView(APIView):
    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = []
    serializer_class = VendorRegSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = encode_token(user)
        verification_link = f"{os.environ.get("APP_DOMAIN")}/verify_email/register?{token}"
        send_email(
            subject="Verify your email",
            txt_template="api/text_mails/signup_verification.txt",
            html_template="api/signup_verification.html",
            context={"verification_link": verification_link},
            user=user
        )
        return Response({'message': 'please check your email for verification'}, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@renderer_classes([JSONRenderer, TemplateHTMLRenderer])
def VerifyRegEmail(request):
    token = request.GET.get("token") or request.query_params.get("token")
    if token is None:
        return Response({"error": "Token is missing"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    payload = decode_token(token)
    if not payload:
        return Response({"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    email = payload.get("sub")
    id = payload.get("iss")
    user = check_email_id_exist_in_token(email, id)
    if not user:
        return Response({"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    user.email_verified = True
    user.save(update_fields=["email_verified"])
    return Response({"success": "Email verified successfully."}, status=status.HTTP_200_OK, template_name="api/email_verified.html")
  
class LoginView(APIView):
    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        print(OutstandingToken.objects.filter(user=data['user']))
        return Response(
                        {'access_token': data['access'],
                         'refresh_token': data['refresh']
                        }, status=status.HTTP_200_OK
        )
    
class ResetPasswordView(APIView):
    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []    
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["email"]
        token = encode_token(user)
        verification_link = f"{os.environ.get("APP_DOMAIN")}/verify/password_reset?token={token}"
        send_email(
            subject="Verify your email",
            txt_template="api/text_mails/reset_password.txt",
            html_template="api/reset_password.html",
            context={"verification_link": verification_link, "name": f"{user.first_name}"}, 
            user=user)
        return Response({'message': 'Please check your email for verification'}, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@renderer_classes([JSONRenderer, TemplateHTMLRenderer])
def VerifyPasswordResetEmail(request):
    token = request.GET.get("token") or request.query_params.get("token")
    if token is None:
        return Response({"error": "Token is missing"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    payload = decode_token(token)
    if not payload:
        return Response({"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    email, id = payload.get("sub"), payload.get("iss")
    user = check_email_id_exist_in_token(email, id)
    if not user:
        return Response({"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    # Checks if user's email has been verfifed before now
    can_reset = set_user_password_reset_time(user)
    if not can_reset:
        return Response({"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    return Response({"success": "Email verified successfully."}, status=status.HTTP_200_OK, template_name="api/email_verified.html")

class SetPasswordView(APIView):
    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []    
    serializer_class = SetPasswordSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['email']
        password = serializer.validated_data['new_password']
        user.set_password(password)
        user.reset_password=False
        user.time_reset=None
        user.save(update_fields=["password", "reset_password", "time_reset"])
        black_list_user_tokens(user)
        return Response({'message': 'Password have been reset successfully.'}, status=status.HTTP_200_OK)

print(BlacklistedToken.objects.all())
print(OutstandingToken.objects.all())   
class ChangePasswordView(APIView):   
    http_method_names = ["post"]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        print(request.user)
        # try:
        #     OutstandingToken.objects.get(user=request.user)
        # except OutstandingToken.DoesNotExist:
        #     return Response({"error": "Token has been invalidated"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        if not check_password(old_password, request.user.password):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        if old_password == new_password:
            return Response({'error': 'Old and New password cannot be thesame.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'Password has been changed successfully.'}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        user = request.user
        return Response({'success': 'Logged out.'}, status=status.HTTP_200_OK)

class DeactivateAccountView(APIView):
    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        user = request.user
        return Response({'message': 'Please check your email to confirm deactivation'}, status=status.HTTP_200_OK)
    
