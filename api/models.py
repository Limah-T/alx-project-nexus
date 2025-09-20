from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from .calculation import customer_payout_sale

import uuid

class CustomManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, phone_number, address, business_address, business_name,  password=None, **extra_kwargs):
        if not all([first_name, last_name, email, phone_number]):
            raise ValueError("This field may not be blank")
        email = self.normalize_email(email=email)
        user = self.model(
                    first_name=first_name, last_name=last_name, email=email,
                    phone_number=phone_number, address=address, business_address=business_address, 
                    business_name=business_name, **extra_kwargs
                    )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, email, phone_number, address, business_address, business_name,  password=None, **extra_kwargs):
        extra_kwargs.setdefault("is_staff", True)
        extra_kwargs.setdefault("is_superuser", True)
        extra_kwargs.setdefault("role", "admin")

        if not extra_kwargs.get("is_staff"):
            raise ValueError("Superuser must have is_staff set to True")
        if not extra_kwargs.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser set to True")
        
        return self.create(
                    first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, address=address, business_address=business_address, business_name=business_name, password=password, **extra_kwargs
                    )
    
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True)
    address = models.TextField(null=True, blank=True)
    business_address = models.TextField(null=True, blank=True)
    business_name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=8, default="customer")
    email_verified = models.BooleanField(default=False)
    otp_verified = models.BooleanField(default=False)
    pending_email = models.EmailField(null=True, blank=True)
    time_pending_email = models.DateTimeField(default=None, null=True, blank=True)
    reset_password = models.BooleanField(default=False)
    time_reset = models.DateTimeField(default=None, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.title().strip()
        if self.last_name:
            self.last_name = self.last_name.title().strip()
        if self.email:
            self.email = self.email.lower().strip()
        if self.phone_number:
            self.phone_number = self.phone_number
        if self.address:
            self.address = self.address.strip()
        if self.business_address:
            self.business_address = self.business_address.strip()
        if self.business_name:
            self.business_name = self.business_name.capitalize().strip()
        super().save(*args, **kwargs)

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) #Better to hide than delete

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.title()
        if not self.slug:
            self.slug = self.create_slug_for_category
        super().save(*args, **kwargs)

    @property
    def create_slug_for_category(self):
        baseURL = slugify(self.name)
        slug = baseURL
        counter = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f"{baseURL}-{counter}"
            counter += 1
        return slug

class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.title()
        super().save(*args, **kwargs)

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=50, unique=True, db_index=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    color = models.ManyToManyField(Color, related_name='products', blank=True)
    image = models.ImageField(upload_to='images/', blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    stock = models.PositiveIntegerField(default=0)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(
                    validators=[MinValueValidator(0), MaxValueValidator(70)],
                    default=0, help_text="Discount percentage (0–70)."
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True, blank=True
    )
    date_added = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.title().strip()
        if self.discount_percent != 0:
            self.discount_amount = customer_payout_sale(self.original_price, self.discount_percent)
        if not self.slug:
            self.slug = self.create_slug_for_product
        super().save(*args, **kwargs)

    @property
    def create_slug_for_product(self):
        baseURL = slugify(self.name)
        slug = baseURL
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{baseURL}-{counter}"
            counter += 1
        return slug

class BankAccount(models.Model):
   id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   vendor = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='bank_details')
   number = models.CharField(max_length=20)
   name = models.CharField(max_length=200, help_text="Provide the exact bank name")
   bank_name = models.CharField(max_length=200)
   updated_at = models.DateTimeField(auto_now=True)

   def save(self, *args, **kwargs):
        if self.name:
           self.name = self.name.title().strip()
        super().save(*args, **kwargs)

class CartItem(models.Model):
   id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_items')
   product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
   item_quantity = models.PositiveIntegerField(default=1)
   updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=8, default="card")
    status = models.CharField(max_length=10, default="pending")
    transaction_id = models.CharField(max_length=30, unique=True)
    date = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
   id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
   payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
   payment_status = models.CharField(max_length=10, default="pending")
   status = models.CharField(max_length=8, default="hold")
   date = models.DateTimeField(auto_now_add=True)

"""*********************BlackListToken to save blacklisted tokens*********************"""

class BlaskListAccessToken(models.Model):
    jti = models.CharField(max_length=255, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.jti