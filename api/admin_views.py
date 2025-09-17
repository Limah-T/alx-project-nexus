from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .auth_serializers import CustomerRegSerializer
from .models import CustomUser

class ModifyUserView(ModelViewSet):
    serializer_class = CustomerRegSerializer
    lookup_field = 'id'

    def get_queryset(self):
        query_set = CustomUser.objects.all() 
        return query_set
    
    def list(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        admin_user = request.user
        if not admin_user.is_superuser:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        id = kwargs.get('id')
        if id is None:
            return Response({'error': 'User ID is missing'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        admin_user = request.user
        if not admin_user.is_superuser:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        id = kwargs.get('id')
        if id is None:
            return Response({'error': 'User ID is missing'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({'error': 'User\' account have been deactivated already'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({'success': 'User\'s account have been deactivated successfully.'}, status=status.HTTP_200_OK)
    

