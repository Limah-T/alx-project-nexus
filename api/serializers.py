from rest_framework import serializers
from django.core.validators import MinLengthValidator, MaxValueValidator
from .models import Category, Color, BankAccount
from .cloudinary import updateImage, uploadImage
from .payments import getBankCode, createSubAccount

class CategorySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    name = serializers.CharField(validators=[MinLengthValidator(2)],
                                max_length=200)

    def validate_name(self, value):
        if Category.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(f"Category name: {value} already exist.")
        return value

    def create(self, validated_data):
        # Handle bulk create
        if isinstance(validated_data, list):
            categories = [Category(**item) for item in validated_data]
            return Category.objects.bulk_create(categories)
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):       
        name = validated_data["name"]       
        instance.name = name
        # saves the name before the slug field.
        instance.save()
        instance.slug = instance.create_slug_for_category
        instance.save()
        return instance

class ColorSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(validators=[MinLengthValidator(2)],
                                max_length=200)
    
    def validate_name(self, value):
        if Color.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Color name already exist.")
        return value

    def create(self, validated_data):
        if isinstance(validated_data, list):
            colors = [Color(**item) for item in validated_data]
            return Color.objects.bulk_create(colors) 
        return Color.objects.create(**validated_data)
    
    def update(self, instance, validated_data):       
        name = validated_data["name"]       
        instance.name = name
        instance.save()
        return instance
    
class ProductSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    category = serializers.UUIDField()
    name = serializers.CharField(validators=[MinLengthValidator(2)],
                                max_length=200)
    # color = serializers.SerializerMethodField()
    image = serializers.ImageField()
    public_id = serializers.CharField(read_only=True)
    srcURL = serializers.URLField(read_only=True)
    description = serializers.CharField(validators=[MinLengthValidator(2)],
                                max_length=255)
    stock = serializers.IntegerField()
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = serializers.IntegerField(
                        validators=[MinLengthValidator(0), MaxValueValidator(70)],
                        help_text="Discount percentage (0–70).", required=False)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2,
                                               required=False)
    date_added = serializers.DateTimeField(read_only=True)

class ModifyProductSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, validators=[MinLengthValidator(2)],
                                max_length=200)
    image = serializers.ImageField(required=False)
    description = serializers.CharField(required=False, validators=[MinLengthValidator(2)],
                                max_length=200)
    stock = serializers.IntegerField(required=False)
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    discount_percent = serializers.IntegerField(
                        validators=[MinLengthValidator(0), MaxValueValidator(70)],
                        help_text="Discount percentage (0–70).", required=False)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2,
                                               required=False)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field == "image":
                continue
            if getattr(instance, field) != value:
                setattr(instance, field, value)

        image = validated_data.get("image")
        if image is not None:        
            srcURL = uploadImage(image)
            if not isinstance(srcURL, dict):
                raise serializers.ValidationError("Only image in these format (png. jpeg) are allowed.")                
            public_id = srcURL['public_id']
            response = updateImage(public_id)
            if not isinstance(response, dict):
                raise serializers.ValidationError("Please try again later")
            instance.image = image
            instance.public_id = public_id
            instance.srcURL = response['secure_url']
        instance.save()
        return instance

class CheckoutSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.UUIDField(read_only=True)
    shipping_address = serializers.CharField(validators=[MinLengthValidator(2)], 
                        max_length=200)
    billing_address = serializers.CharField(validators=[MinLengthValidator(2)], 
                        max_length=200, required=False)
    payment_method = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

class CartItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    customer = serializers.UUIDField(read_only=True)
    product = serializers.UUIDField()
    item_quantity = serializers.IntegerField()

    def validate_item_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Item quantity cannot be less than 0.")
        return value

class PaymentSerializer(serializers.Serializer):
    cart = serializers.UUIDField(read_only=True)
    amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    method = serializers.CharField(read_only=True, required=False)
    status = serializers.CharField(read_only=True, required=False)
    transaction_id = serializers.CharField(read_only=True, required=False)
    date = serializers.DateTimeField(read_only=True)

class BankAccountSerializer(serializers.Serializer):
    vendor = serializers.UUIDField(read_only=True)
    number = serializers.CharField(max_length=10, trim_whitespace=True)
    bank_name = serializers.CharField(max_length=255, trim_whitespace=True)
            
    def validate(self, attrs):
        if BankAccount.objects.filter(number=attrs["number"]).exists():
            raise serializers.ValidationError("Account number already exist!")
        
        bank_code = getBankCode(attrs["bank_name"])
        if not bank_code:
            raise serializers.ValidationError("Enter the correct bank name.")
        
        subaccount = createSubAccount(
            business_name='default',
            bank_code=bank_code,
            account_no=attrs["number"]
        )
        if not subaccount:
            raise 
        attrs.update({
            "bank_code": bank_code,
            "subaccount_code": subaccount["subaccount_code"],
            "account_name": subaccount["account_name"]
        })
        return attrs










    
