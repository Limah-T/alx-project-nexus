from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .serializers import CategorySerializer, ColorSerializer, ProductSerializer, BankAccountSerializer, ModifyProductSerializer, CartItemSerializer
from .models import Category, Color, Product, BankAccount
from .utils.helper_functions import check_if_admin, request_instance
from .utils.token import valid_access_token
from .cloudinary import uploadImage, getImage
from .utils.calculation import total_amount_of_cartItems, amount_of_cartItem, checkOut
from .payments import getSubAccount, getBankCode, createSubAccount
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
            return Response({"error": "Category ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        # all_products = Product.objects.filter(category=category)
        # serializer = ProductSerializer(all_products, many=True)
        serializer = self.serializer_class(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
                
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            category = Category.objects.get(id=id, is_active=True)
        except Category.DoesNotExist:
            return Response({"error": "Category ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data, instance=category, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Updated successfully."}, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
        
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            category = Category.objects.get(id=id, is_active=True)
        except Category.DoesNotExist:
            return Response({"error": "Category ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        category.is_active = False
        category.save(update_fields=["is_active"])
        return Response({"success": "Category has been hidden."}, status=status.HTTP_200_OK)

"""*****************************************ColorView*******************************************"""
class ColorView(ModelViewSet):
    serializer_class = ColorSerializer
    lookup_field = "id"

    def get_queryset(self):
        query = Color.objects.all()
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
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
         
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
        
        id = kwargs.get("id")
        if not id:
            return Response({"error": "ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            color = Color.objects.get(id=id)
        except Color.DoesNotExist:
            return Response({"error": "Color ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(color)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)

        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
               
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            color = Color.objects.get(id=id)
        except Color.DoesNotExist:
            return Response({"error": "Color ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data, instance=color, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Updated successfully."}, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=status.HTTP_400_BAD_REQUEST)
        
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            color = Color.objects.get(id=id)
        except Color.DoesNotExist:
            return Response({"error": "Color ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        color.delete()
        return Response({"success": "Color has been deleted."}, status=status.HTTP_200_OK)


"""******************************************ProductView*****************************************"""
class ProductView(ModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = "id"

    def get_queryset(self):
        query = Product.objects.filter(stock__gte=1, category__is_active=True).order_by("-date_added")
        return query

    def create(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.role != "vendor":
            return Response({"error": "Permission denied, not a vendor account."}, status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(BankAccount, vendor=request.user)
        serializer = self.serializer_class(data=request.data, many=request_instance(request))
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        srcURL = uploadImage(data['image'])
        if not isinstance(srcURL, dict):
            return Response({"error": "Only image in these format (png. jpeg) are allowed."}, status=status.HTTP_400_BAD_REQUEST)
        
        public_id = f"product/{srcURL['public_id']}"
        category_id = serializer.validated_data['category']
        category = get_object_or_404(Category, id=str(category_id))
        product = Product.objects.create(
            category=category, vendor=request.user, image=data['image'],
            public_id=public_id, srcURL=srcURL['secure_url'],
            name=data['name'], description=data['description'], stock=data['stock'], original_price=data['original_price'], discount_percent=data.get('discount_percent', 0), discount_amount=data.get('discount_amount', 0))
        product.create_slug_for_product
        product.save(update_fields=['slug'])    
        return Response({"success": "Product(s) saved successfully"})
    
    def list(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "Product ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=id)
        public_id = str(product.image).split("/")[-1]
        response = getImage(public_id)
        if not isinstance(response, dict):
            return Response({"error": "Please try again later"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "Product ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=id)
        if product.vendor != request.user:
            return Response({"error": "Permission denied."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ModifyProductSerializer(data=request.data, instance=product, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Product has been updated successfully."}, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "Product ID is missing."}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=id)
        if product.vendor != request.user:
            return Response({"error": "Permission denied."}, status=status.HTTP_400_BAD_REQUEST)
        product.delete()
        return Response({"success": "Product has been deleted successfully."}, status=status.HTTP_200_OK)


"""****************************************CartItem************************************************"""
class CartItemView(ModelViewSet):
    serializer_class = CartItemSerializer

    def create(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        
        many = request_instance(request)
        serializer = self.serializer_class(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if isinstance(data, list):
            total_amount = total_amount_of_cartItems(data, request.user)
            if not total_amount:
                return Response({"error": "One of the product's quantity is greater than the stock quantity."}, status=status.HTTP_400_BAD_REQUEST)            
        else:
            total_amount = amount_of_cartItem(data, request.user)
            if not total_amount:
                return Response({"error": "Product's quantity is greater than the stock quantity."}, status=status.HTTP_400_BAD_REQUEST)
        print(total_amount)
        # check_out = data.get("checkout")
        # checkout = checkOut(check_out, request.user)
        return Response({"success": "Cart created successfully."}, status=status.HTTP_200_OK)

class BankAccountView(ModelViewSet):
    serializer_class = BankAccountSerializer

    def create(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.role != "vendor":
            return Response({"error": "Permission denied, not a vendor account."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        print(serializer.validated_data)
        BankAccount.objects.create(
            vendor=request.user, number=data["number"], name=data["account_name"],
            bank_name=data["bank_name"], bank_code=data["bank_code"], 
            subaccount_code=data["subaccount_code"]
        )
        print(BankAccount.objects.values())
        return Response({"message": f"Please confirm name -- {data['account_name']}"}, status=status.HTTP_200_OK)

@api_view(http_method_names=["GET"])
def confirmBankNameView(request):
    if not valid_access_token(request.auth):
        return Response({"error": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
    if request.user.role != "vendor":
       return Response({"error": "Permission denied, not a vendor account."}, status=status.HTTP_400_BAD_REQUEST)
    bank_account = get_object_or_404(BankAccount, vendor=request.user)
    if bank_account.verified:
        return Response({"success": "Account has been verified already."}, status=status.HTTP_200_OK)
    confirmation = request.query_params.get("confirmation")
    if confirmation is None:
        return Response({"error": "Confirmation is missing."}, status=status.HTTP_400_BAD_REQUEST) 
    if confirmation.lower() in ["false", "no", "0"]:
        bank_account.delete()
        return Response({"success": "Please enter the right account number."}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if confirmation.lower() in ["true", "yes", "1"]:
        bank_account.verified = True
        bank_account.save(update_fields=["verified"])
        return Response({"success": "Bank account has been added successfully."}, status=status.HTTP_200_OK)

