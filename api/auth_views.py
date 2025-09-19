from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.hashers import check_password

from .auth_serializers import CustomerRegSerializer, VendorRegSerializer, LoginSerializer, ResetPasswordSerializer, SetPasswordSerializer, ChangePasswordSerializer, CustomerProfileSerializer
from .utils.token import encode_token, decode_token, black_list_user_tokens, reject_invalid_access_token
from .utils.helper_functions import check_email_id_exist_in_token, set_user_password_reset_time
from .models import CustomUser, BlaskListAccessToken
from .tasks import send_email
from .cloudinary import createmain
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
        token = encode_token(user.id, user.email)
        verification_link = f"{os.environ.get("APP_DOMAIN")}/verify_email/register?token={token}"
        send_email(
            subject="Verify your email",
            txt_template="api/text_mails/signup_verification.txt",
            html_template="api/signup_verification.html",
            context={"verification_link": verification_link},
            email=user.email
        )
        return Response({'message': 'please check your email for verification'}, 
                        status=status.HTTP_200_OK)

class VendorRegView(APIView):
    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = []
    serializer_class = VendorRegSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = encode_token(user.id, user.email)
        verification_link = f"{os.environ.get("APP_DOMAIN")}/verify_email/register?{token}"
        send_email(
            subject="Verify your email",
            txt_template="api/text_mails/signup_verification.txt",
            html_template="api/signup_verification.html",
            context={"verification_link": verification_link},
            email=user.email
        )
        return Response({'message': 'please check your email for verification'}, 
                        status=status.HTTP_200_OK)

@api_view(http_method_names=["GET"])
@authentication_classes([])
@permission_classes([])
@renderer_classes([JSONRenderer, TemplateHTMLRenderer])
def verifyRegEmail(request):
    token = request.GET.get("token") or request.query_params.get("token")
    if token is None:
        return Response({"error": "Token is missing."}, status=status.HTTP_400_BAD_REQUEST, 
                        template_name="api/invalid_token.html")
    payload = decode_token(token)
    if not payload:
        return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST, 
                        template_name="api/invalid_token.html")
    email, id= payload.get("sub") , payload.get("iss")
    if not email or not id:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST, 
                        template_name="api/invalid_token.html")
    user = check_email_id_exist_in_token(email, id)
    if not user:
        return Response({"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST, 
                        template_name="api/invalid_token.html")
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
        token = encode_token(user.id, user.email)
        verification_link = f"{os.environ.get("APP_DOMAIN")}/verify/password_reset?token={token}"
        send_email(
            subject="Verify your email",
            txt_template="api/text_mails/reset_password.txt",
            html_template="api/reset_password.html",
            context={"verification_link": verification_link, "name": f"{user.first_name}"}, 
            email=user.email)
        return Response({'message': 'Please check your email for verification'}, 
                        status=status.HTTP_200_OK
        )

@api_view(http_method_names=["GET"])
@authentication_classes([])
@permission_classes([])
@renderer_classes([JSONRenderer, TemplateHTMLRenderer])
def verifyPasswordResetEmail(request):
    token = request.GET.get("token") or request.query_params.get("token")
    if token is None:
        return Response({"error": "Token is missing"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    payload = decode_token(token)
    if not payload:
        return Response({"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST, 
                        template_name="api/invalid_token.html")
    email, id = payload.get("sub"), payload.get("iss")
    if not email or not id:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST, 
                        template_name="api/invalid_token.html")
    user = check_email_id_exist_in_token(email, id)
    if not user:
        return Response({"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST, 
                        template_name="api/invalid_token.html")
    can_reset = set_user_password_reset_time(user)
    if not can_reset:
        return Response({"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST,
                        template_name="api/invalid_token.html")
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
        return Response({'message': 'Password have been reset successfully.'}, 
                        status=status.HTTP_200_OK
        )
 
class ChangePasswordView(APIView):   
    http_method_names = ["post"]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        if not reject_invalid_access_token(request.auth):
            return Response({"error": "Inavid token."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        if not check_password(old_password, request.user.password):
            return Response({"error": "Old password is incorrect."}, 
                            status=status.HTTP_400_BAD_REQUEST
        )
        if old_password == new_password:
            return Response({'error': 'Old and New password cannot be thesame.'}, 
                            status=status.HTTP_400_BAD_REQUEST
        )
        return Response({'success': 'Password has been changed successfully.'}, 
                        status=status.HTTP_200_OK
        )

class LogoutView(APIView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            # Invalidates the current access token to avoid re-validation before expiration time is up.
            token = AccessToken(request.auth) 
            jti = token['jti']
            BlaskListAccessToken.objects.create(jti=jti)
        except Exception:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'success': 'Logged out.'}, status=status.HTTP_200_OK)
    
    
"""****************************Profile Section******************************************"""

class CustomerProfileView(ModelViewSet):
    serializer_class = CustomerProfileSerializer
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        createmain()
        if not reject_invalid_access_token(request):
            return Response({"error": "Inavid token."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        if not reject_invalid_access_token(request):
            return Response({"error": "Inavid token."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data, instance=self.get_object(), partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user.pending_email:
            token = encode_token(user.id, user.pending_email)
            verification_link = f"{os.environ.get("APP_DOMAIN")}/verify/email_update?token={token}"
            token = encode_token(user.id, user.pending_email)
            send_email(
                    subject="Update your email", txt_template="api/text_mails/update_email.txt",
                    html_template="api/update_email.html", 
                    context={"verification_link": verification_link, "name": user.first_name},
                    email=user.pending_email
            )
            return Response({"message": "Please check your email to verify."}, 
                            status=status.HTTP_200_OK
            )
        return Response({"success": "Profile updated successfully."}, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        if not reject_invalid_access_token(request):
            return Response({"error": "Inavid token."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        token = encode_token(user.id, user.email)
        verification_link = f"{os.environ.get("APP_DOMAIN")}/verify/acct_deactivation?token={token}"   
        send_email(
                subject="Deactivate your account?", txt_template="api/text_mails/deactivate_acct_alert.txt",
                html_template="api/deactivate_acct_alert.html", 
                context={"verification_link": verification_link, "name": user.first_name},
                email=user.email
            )
        return Response({"message": "Please check your email to verify account deactivation."}, 
                        status=status.HTTP_200_OK
        )

class VendorProfileView(ModelViewSet):
    serializer_class = CustomerRegSerializer

    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        if not reject_invalid_access_token(request):
            return Response({"error": "Inavid token."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        if not reject_invalid_access_token(request):
            return Response({"error": "Inavid token."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data, instance=self.get_object(), partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user.pending_email:
            token = encode_token(user.id, user.email)
            verification_link = f"{os.environ.get("APP_DOMAIN")}/verify_email_update?token={token}"
            token = encode_token(user.id, user.pending_email)
            send_email(
                    subject="Update your email", txt_template="api/text_mails/update_email.txt",
                    html_template="api/update_email.html", 
                    context={"verification_link": verification_link, "name": user.first_name},
                    email=user.pending_email
            )
            return Response({"message": "Please check your email to verify."}, 
                            status=status.HTTP_200_OK
            )
        return Response({"success": "Profile updated successfully."}, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        if not reject_invalid_access_token(request):
            return Response({"error": "Inavid token."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        token = encode_token(user.id, user.email)
        verification_link = f"{os.environ.get("APP_DOMAIN")}/verify/acct_deactivation?token={token}"   
        send_email(
                subject="Deactivate your account?", txt_template="api/text_mails/deactivate_acct_alert.txt", html_template="api/deactivate_acct_alert.html", 
                context={"verification_link": verification_link, "name": user.first_name},
                email=user.email
            )
        return Response({"message": "Please check your email to verify account deactivation."}, 
                        status=status.HTTP_200_OK
        )

@api_view(http_method_names=["GET"])
@authentication_classes([])
@permission_classes([])
@renderer_classes([JSONRenderer, TemplateHTMLRenderer])
def verifyEmailUpdate(request):
    token = request.query_params.get("token") or request.GET.get("token")
    if token is None:
        return Response({"error": "Token is missing."}, status=status.HTTP_400_BAD_REQUEST)
    payload = decode_token(token)
    if not payload:
        return Response({"error": "Inavlid token"}, status=status.HTTP_400_BAD_REQUEST)
    pending_email, id = payload.get("sub"), payload.get("iss")
    if not pending_email or not id:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST, 
                        template_name="api/invalid_token.html")
    try:
        user = CustomUser.objects.get(pending_email=pending_email, is_active=True, email_verified=True)
    except CustomUser.DoesNotExist:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST,
                        template_name="api/invalid_token.html")
    if str(user.id) != id:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST, 
                        template_name="api/invalid_token.html")
    if not user:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST,
                        template_name="api/invalid_token.html")
    user.email, user.pending_email = pending_email, None
    user.save(update_fields=["email", "pending_email"])
    return Response({"success": "Email updated successfully."}, status=status.HTTP_200_OK,
                    template_name="api/email_verified.html")

@api_view(http_method_names=["GET"])
@authentication_classes([])
@permission_classes([])
@renderer_classes([JSONRenderer, TemplateHTMLRenderer])
def verifyAcctDeactivation(request):
    token = request.query_params.get("token") or request.GET.get("token")
    if token is None:
        return Response({"error": "Token is missing."}, status=status.HTTP_400_BAD_REQUEST,
                            template_name="api/invalid_token.html")
    payload = decode_token(token)
    if not payload:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    email, id = payload.get("sub"), payload.get("iss")
    if not email or not id:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    user = check_email_id_exist_in_token(email, id)
    if not user:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    if not user.email_verified:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST, template_name="api/invalid_token.html")
    user.is_active = False
    user.save(update_fields=["is_active"])
    return Response({"success": "Account has been deactivated successfully"}, status=status.HTTP_200_OK, template_name="api/deactivate_acct_verified.html")