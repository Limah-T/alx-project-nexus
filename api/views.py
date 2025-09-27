from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404

from .serializers import (CategorySerializer, ColorSerializer, 
                          ProductSerializer, BankAccountSerializer, 
                          ModifyProductSerializer, CartItemSerializer
                          )
from .models import (Category, Color, Product, BankAccount, 
                     CartItem, Payment, Cart, Order
                    )
from .custom_classes import CustomPageNumberPagination
from .utils.helper_functions import (check_if_admin, 
                                     request_instance,check_if_list_of_products_exist, check_if_user_cart_is_active, check_if_products_exist_in_cart, update_list_of_cartItems, check_if_product_exist, retrive_cartItems, retrieve_single_cartItem, remove_products_from_cart, remove_a_product_from_cart, check_list_of_products_quantity, deduct_product_quantity_after_payment, check_product_quantity
                                    )
from .utils.token import valid_access_token
from .cloudinary import uploadImage, getImage
from .utils.calculation import (total_amount_of_cartItems, 
                                amount_of_cartItem, 
                                update_product_in_cart, 
                                checkOut
                            )
from .payments import (transactionSplit, initializeTransaction, 
                       paymentVerify, initializeTransactionVendors
                    )

class CategoryView(ModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = "id"
    filter_backends = [
                        DjangoFilterBackend, 
                        SearchFilter,
                        OrderingFilter
                    ]
    filterset_fields = ["name"]
    search_fields = ["name"]
    pagination_class = CustomPageNumberPagination
    ordering = ["name"]

    def get_queryset(self):
        query = Category.objects.filter(is_active=True)
        return query
    
    def create(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=400)
        
        many = True
        if not isinstance(request.data, list):
            many = False
    
        serializer = self.serializer_class(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Created successfully."}, status=200)
    
    def list(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        queryset = self.filter_queryset(self.get_queryset())  # <-- applies filter + search + ordering

        page = self.paginate_queryset(queryset)  # <-- applies pagination
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data}, status=200)
    
    def retrieve(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        
        id = kwargs.get("id")
        if not id:
            return Response({"error": "ID is missing."}, status=400)
        try:
            category = Category.objects.get(id=id, is_active=True)
        except Category.DoesNotExist:
            return Response({"error": "Category ID does not exist."}, status=400)
        
        serializer = self.serializer_class(category)
        return Response(serializer.data, status=200)
    
    def update(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=400)
                
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "ID is missing."}, status=400)
        try:
            category = Category.objects.get(id=id, is_active=True)
        except Category.DoesNotExist:
            return Response({"error": "Category ID does not exist."}, status=400)
        serializer = self.serializer_class(data=request.data, instance=category, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Updated successfully."}, status=200)
    
    def destroy(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=400)
        
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "ID is missing."}, status=400)
        try:
            category = Category.objects.get(id=id, is_active=True)
        except Category.DoesNotExist:
            return Response({"error": "Category ID does not exist."}, status=400)
        category.is_active = False
        category.save(update_fields=["is_active"])
        return Response({"success": "Category has been hidden."}, status=200)

"""*****************************************ColorView*******************************************"""
class ColorView(ModelViewSet):
    serializer_class = ColorSerializer
    lookup_field = "id"
    filter_backends = [
                        DjangoFilterBackend, 
                        SearchFilter,
                        OrderingFilter
                    ]
    filterset_fields = ["name"]
    search_fields = ["name"]
    pagination_class = CustomPageNumberPagination
    ordering = ["name"]

    def get_queryset(self):
        query = Color.objects.all()
        return query
    
    def create(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=400)
        
        many = True
        if not isinstance(request.data, list):
            many = False
    
        serializer = self.serializer_class(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Created successfully."}, status=200)
    
    def list(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=400)
        queryset = self.filter_queryset(self.get_queryset())  # <-- applies filter + search + ordering

        page = self.paginate_queryset(queryset)  # <-- applies pagination
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)

    
    def retrieve(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=400)
        
        id = kwargs.get("id")
        if not id:
            return Response({"error": "ID is missing."}, status=400)
        try:
            color = Color.objects.get(id=id)
        except Color.DoesNotExist:
            return Response({"error": "Color ID does not exist."}, status=400)
        serializer = self.serializer_class(color)
        return Response(serializer.data, status=200)
    
    def update(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)

        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=400)
               
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "ID is missing."}, status=400)
        try:
            color = Color.objects.get(id=id)
        except Color.DoesNotExist:
            return Response({"error": "Color ID does not exist."}, status=400)
        serializer = self.serializer_class(data=request.data, instance=color, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Updated successfully."}, status=200)
    
    def destroy(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        
        if not check_if_admin(request.user):
            return Response({"error": "You do not have the pernmission to perform this action"}, status=400)
        
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "ID is missing."}, status=400)
        try:
            color = Color.objects.get(id=id)
        except Color.DoesNotExist:
            return Response({"error": "Color ID does not exist."}, status=400)
        color.delete()
        return Response({"success": "Color has been deleted."}, status=200)


"""******************************************ProductView*****************************************"""
class ProductView(ModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = "id"
    filter_backends = [
                        DjangoFilterBackend, 
                        SearchFilter,
                        OrderingFilter
                    ]
    fiterset_fields = ["name", "description", "original_price", "discount_amount"]
    search_fields = ["name", "description", "original_price", "discount_amount"]
    pagination_class = CustomPageNumberPagination
    ordering = ["original_price"]

    def get_queryset(self):
        query = Product.objects.filter(stock__gte=1, category__is_active=True)
        return query

    def create(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        if request.user.role != "vendor":
            return Response({"error": "Permission denied, not a vendor account."}, status=400)
        get_object_or_404(BankAccount, vendor=request.user)
        serializer = self.serializer_class(data=request.data, many=request_instance(request))
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        srcURL = uploadImage(data['image'])
        if not isinstance(srcURL, dict):
            return Response({"error": "Only image in these format (png. jpeg) are allowed."}, status=400)
        
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
            return Response({"error": "Invalid Token."}, status=400)
        queryset = self.filter_queryset(self.get_queryset())  # <-- applies filter + search + ordering

        page = self.paginate_queryset(queryset)  # <-- applies pagination
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)
    
    def retrieve(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "Product ID is missing."}, status=400)
        product = get_object_or_404(Product, id=id)
        public_id = str(product.image).split("/")[-1]
        response = getImage(public_id)
        if not isinstance(response, dict):
            return Response({"error": "Please try again later"}, status=400)
        serializer = self.serializer_class(product)
        return Response(serializer.data, status=200)
    
    def update(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "Product ID is missing."}, status=400)
        product = get_object_or_404(Product, id=id)
        if product.vendor != request.user:
            return Response({"error": "Permission denied."}, status=400)
        serializer = ModifyProductSerializer(data=request.data, instance=product, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Product has been updated successfully."}, status=200)
    
    def destroy(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        id = kwargs.get("id")
        if id is None:
            return Response({"error": "Product ID is missing."}, status=400)
        product = get_object_or_404(Product, id=id)
        if product.vendor != request.user:
            return Response({"error": "Permission denied."}, status=400)
        product.delete()
        return Response({"success": "Product has been deleted successfully."}, status=200)


"""****************************************CartItem************************************************"""
class CartItemView(ModelViewSet):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.all()

    def create(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        
        many = request_instance(request.data)
        serializer = self.serializer_class(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if isinstance(data, list):
            total_amount = total_amount_of_cartItems(data, request.user)
            if not total_amount:
                return Response({"error": "One of the product's quantity is greater than the stock quantity."}, status=400)            
        else:
            total_amount = amount_of_cartItem(data, request.user)
            if not total_amount:
                return Response({"error": "Product's quantity is greater than the stock quantity."}, status=400)
        # check_out = data.get("checkout")
        # checkout = checkOut(check_out, request.user)
        return Response({"success": "Cart created successfully."}, status=200)
    
    def retrieve(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        cart = check_if_user_cart_is_active(user=request.user)
        if not cart:
            return Response({"error": "Cart is empty!."}, status=400)
        if not check_if_products_exist_in_cart(cart):
            return Response({"error": "Please add products to cart."}, status=400)
        cartItems = retrive_cartItems(cart)
        if len(cartItems) > 1:
            serializer = self.serializer_class(cartItems, many=True)
        else:
            cartItems =  retrieve_single_cartItem(cart)
            serializer = self.serializer_class(cartItems)
        return Response({"status": "success", "data": serializer.data}, status=200)
    
    def update(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        many = request_instance(request)       
        cart = check_if_user_cart_is_active(user=request.user)
        if not cart:
            return Response({"error": "Cart is empty!."}, status=400)
        if not check_if_products_exist_in_cart(cart):
            return Response({"error": "Please add products to cart."}, status=400)
        if many:
            if not check_if_list_of_products_exist(request.data):
                return Response({"error": "Some or all of the provided product IDs do not exist."},status=400)                            
            cartItem = update_list_of_cartItems(cart, request.data)
        else:
            product = check_if_product_exist(request.data)
            if not product:
                return Response({"error": "Provided product ID do not exist."}, status=400)
            cartItem = update_product_in_cart(product.id, request.data["item_quantity"], cart)
        serializer = self.serializer_class(data=request.data, instance=cartItem,
                                            many=many, partial=True)
        serializer.is_valid(raise_exception=True) 
        return Response({"success": "updated successfully."}, status=200)
    
    def destroy(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)      
        cart = check_if_user_cart_is_active(user=request.user)
        if not cart:
            return Response({"error": "Cart is empty!."}, status=400)
        if not check_if_products_exist_in_cart(cart):
            return Response({"error": "Please add products to cart."}, status=400)
        many = request_instance(request) 
        if many:
            if not remove_products_from_cart(cart, request.data):
                return Response({"error": "Some or all of the provided product IDs do not exist in the cart!"}, status=400)
        else:
            if not remove_a_product_from_cart(cart, request.data['product']):
                return Response({"error": "Cannot remove a product that does not exist in a cart!"}, status=400)
        return Response({"success": "Cart deleted successfully."}, status=200)

class BankAccountView(ModelViewSet):
    serializer_class = BankAccountSerializer

    def create(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        if request.user.role != "vendor":
            return Response({"error": "Permission denied, not a vendor account."}, status=400)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        BankAccount.objects.create(
            vendor=request.user, number=data["number"], name=data["account_name"],
            bank_name=data["bank_name"], bank_code=data["bank_code"], 
            subaccount_code=data["subaccount_code"]
        )
        return Response({"message": f"Please confirm name -- {data['account_name']}"}, status=200)

@api_view(http_method_names=["GET"])
def confirmBankNameView(request):
    if not valid_access_token(request.auth):
        return Response({"error": "Invalid Token."}, status=400)
    if request.user.role != "vendor":
       return Response({"error": "Permission denied, not a vendor account."}, status=400)
    bank_account = get_object_or_404(BankAccount, vendor=request.user)
    if bank_account.vendor.role != "vendor":
        return Response({"error": "Permission denied, not a vendor account"}, status=400)
    if bank_account.verified:
        return Response({"success": "Account has been verified already."}, status=200)
    confirmation = request.query_params.get("confirmation")
    if confirmation.lower() not in ['false', 'no', '0', 'true', '1', 'yes']:
        return Response({"error": "Confirmation is missing."}, status=400) 
    if confirmation.lower() in ["false", "no", "0"]:
        bank_account.delete()
        return Response({"success": "Please enter the right account number."}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if confirmation.lower() in ["true", "yes", "1"]:
        bank_account.verified = True
        bank_account.save(update_fields=["verified"])
        transaction_split = transactionSplit(name=str(bank_account.vendor.business_name),
                                vendor=bank_account.vendor,
                                subaccount_code=bank_account.subaccount_code
                                )
        if not transaction_split:
            return Response({"error": "Can't create a transaction split"}, status=400)
        return Response({"success": "Bank account has been added successfully."}, status=200)
 
class PaymentView(APIView):
    http_method_names = ["post"]
    serializer_class = CartItemSerializer

    def post(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)
        cart = check_if_user_cart_is_active(user=request.user)
        if not cart:
            return Response({"error": "Cart is empty!."}, status=400)
        if not check_if_products_exist_in_cart(cart):
            return Response({"error": "Please add products to cart."}, status=400)
        many = request_instance(request.data)
        if many:
            if not check_if_list_of_products_exist(request.data):
                return Response({"error": "Some or all of the provided product IDs do not exist."},status=400)
            if not check_list_of_products_quantity(cart, request.data):
                return Response({"error": "Few or some of the products quantity is higher than the stock quantity"})
            payment_transaction = initializeTransactionVendors(product_data=request.data, many=many)
            if not payment_transaction:
                return Response({"error": "error"}, status=400)
        else:
            product = check_if_product_exist(request.data)
            if not product:
                return Response({"error": "Provided product ID do not exist."}, status=400)
            if not check_product_quantity(cart, request.data):
                return Response({"error": "Product quantity is higher than stock quantity"}, status=400)
            payment_transaction = initializeTransaction(product_data=request.data)
            reference = payment_transaction["data"]["reference"]
            print(reference)
            payment, created = Payment.objects.get_or_create(
                                    cart=check_if_products_exist_in_cart(cart), 
                                    defaults={"reference": reference}
                                    )    
        return Response({"success": payment.id}, status=200)

class VerifyPaymentReference(APIView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        reference = kwargs.get("reference")
        if reference is None:
            return Response({"error": "Reference ID is missing"}, status=400)
        payment = get_object_or_404(Payment, id=str(reference))
        response = paymentVerify(payment.reference)
        if not response:
            return Response({"error": "Payment has not been verified"}, status=400)        
        cart = Cart.objects.get(id=payment.cart.cart.id)
        cart.status = "paid"
        cart.save(update_fields=["status"])
        print(payment.status)
        if payment.status == "verified":
            order_id = Order.objects.get(payment=payment)
            return Response({"order": order_id.id}, status=200)
        amount = response['data']['amount']
        payment.method = response['data']['channel']
        payment.amount = amount / 100
        payment.status = "verified"
        payment.save()
        item_quantity_deduction = deduct_product_quantity_after_payment(cart)
        if not item_quantity_deduction:
            return Response({"error": "While trying to deduct product quantity."}, status=400)
        print(item_quantity_deduction)
        order = Order.objects.create(payment=payment, payment_status = payment.status) 
        return Response({"success": order.id}, status=200)
    
class CustomerDashboard(APIView):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        if not valid_access_token(request.auth):
            return Response({"error": "Invalid Token."}, status=400)    
            

print(CartItem.objects.values())   
print("***********************************")
print(Payment.objects.values())