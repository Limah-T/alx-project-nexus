from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .serializers import CategorySerializer, ColorSerializer, ProductSerializer
from .models import Category,Color, Product, Order
from .utils.helper_functions import check_if_admin
from .utils.token import valid_access_token

class CategoryView(ModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = "id"

    def get_queryset(self):
        query = Category.objects.filter(is_active=True)
        return query.order_by("-date")
    
    def create(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
        
        many = True
        if not isinstance(request.data, list):
            many = False
    
        serializer = self.serializer_class(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Created successfully."}, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        
        id = kwargs.get("id")
        if not id:
            return Response({"error": "ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            category = Category.objects.get(id=id, is_active=True)
        except Category.DoesNotExist:
            return Response({"error": "Category does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        # all_products = Product.objects.filter(category=category)
        # serializer = ProductSerializer(all_products, many=True)
        serializer = self.serializer_class(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
                
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            category = Category.objects.get(id=id, is_active=True)
        except Category.DoesNotExist:
            return Response({"error": "Category does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data, instance=category, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Updated successfully."}, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            category = Category.objects.get(id=id, is_active=True)
        except Category.DoesNotExist:
            return Response({"error": "Category does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        category.is_active = False
        category.save(update_fields=["is_active"])
        return Response({"success": "Category has been hidden."}, status=status.HTTP_200_OK)
