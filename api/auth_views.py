from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .auth_serializers import CustomerRegSerializer, VendorRegSerializer, LoginSerializer, ResetPasswordSerializer, SetPasswordSerializer, ChangePasswordSerializer

class CustomerRegView(APIView):
    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = []
    serializer_class = CustomerRegSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': serializer.data}, status=status.HTTP_200_OK)
        # return Response({'message': 'please check your email for verification'}, status=status.HTTP_200_OK)

class VendorRegView(APIView):
    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = []
    serializer_class = VendorRegSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': serializer.data}, status=status.HTTP_200_OK)
        # return Response({'message': 'please check your email for verification', status=status.HTTP_200_OK})
    
class LoginView(APIView):
    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': 'logged in'}, status=status.HTTP_200_OK)
    
class ResetPasswordView(APIView):
    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []    
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Please check your email for verification'}, status=status.HTTP_200_OK)

class SetPasswordView(APIView):
    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []    
    serializer_class = SetPasswordSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['email']
        if not user.reset_password:
            return Response({'error': 'Please verify your email to reset your password.'}, status=status.HTTP_400_BAD_REQUEST)
        # password = serializer.validated_data['new_password']
        # user.set_password(password)
        # user.reset_password=False
        # user.time_reset=None
        # user.save()
        return Response({'message': 'Password have been reset successfully.'}, status=status.HTTP_200_OK)
    
class ChangePasswordView(APIView):
    http_method_names = ["post"]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
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
    
