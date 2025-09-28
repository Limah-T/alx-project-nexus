from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from ..models import Product, Cart, CartItem, Checkout, BankAccount
from collections import defaultdict
import os

def discount_from_vendor(original_price, discount_percent):
    discounted_percentage = discount_percent / 100 # e.g 5/100
    discount_price = float(original_price) * discounted_percentage # 50,000 * 0.05
    return discount_price # 2,500

def customer_payout_sale(original_price, discount_percent):
    customer_payout = original_price - discount_from_vendor(original_price, discount_percent) # 50,00 - 2,500
    return customer_payout 

def platform_payout(original_price):
    platform_percentage = int(os.environ.get("PLATFORM_PERCENTAGE")) / 100  # e.g 10/100
    discount = original_price * platform_percentage # 50,000 * 0.1
    return discount # 5,000

def vendor_payout_sale(original_price, discount_percent):
    if discount_percent != 0:
        vendor_discount = discount_from_vendor(original_price, discount_percent)
    else:
        vendor_discount = 0
    vendor_price = original_price - vendor_discount # 50,000 - 2,000
    amount = vendor_price - platform_payout(original_price) # 47,500 - 5,000
    return amount #42,500

def vendor_payout(original_price):
    platform_price = platform_payout(original_price)
    vendor_amount = original_price - platform_price
    return vendor_amount

@transaction.atomic()
def check_product_quantity(item_quantity, product):
    try:
        with transaction.atomic():
            if product.stock >= item_quantity:
                return True
    except IntegrityError:
        return False

def total_amount_of_cartItems(validated_data, user):
    total_amount, merged = 0, defaultdict(int)
    try:        
        if not Cart.objects.filter(customer=user, status="unpaid").exists():
            cart = Cart.objects.create(customer=user, status="unpaid")
    except Exception:
        cart, created = Cart.objects.get_or_create(customer=user)
    for data in validated_data:  
        merged[data["product"]] +=  int(data["item_quantity"])   
    merged_copy = merged.copy()
  
    for product_id in merged_copy:
        total_quantity = merged_copy[product_id]
        product = get_object_or_404(Product, id=str(product_id), category__is_active=True)
        if not check_product_quantity(total_quantity, product):
            return False
        item_amount = total_quantity * (
            product.discount_amount if product.discount_percent != 0 else product.original_price
        )
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id,
                                            defaults={"item_quantity": 0, "total_amount": 0.00})
        cart_item.item_quantity += total_quantity
        cart_item.total_amount = cart_item.item_quantity * (
            product.discount_amount if product.discount_percent != 0 else product.original_price
        )
        cart_item.save(update_fields=["item_quantity", "total_amount"])
        total_amount += item_amount
    return total_amount

def amount_of_cartItem(validated_data, user):
    cart, created = Cart.objects.get_or_create(customer=user, status="unpaid")
    total_amount = 0
    product_id = validated_data["product"]
    item_quantity = validated_data["item_quantity"]
    product = get_object_or_404(Product, id=str(product_id), category__is_active=True)
    if not check_product_quantity(item_quantity, product):
        return False
    item_amount = item_quantity * (
        product.discount_amount if product.discount_percent != 0 else product.original_price
    )
    cart_item, created = CartItem.objects.get_or_create(
                                cart=cart, product_id=product_id, 
                                defaults={"item_quantity": 0, "total_amount": 0.00}
                        )
    cart_item.item_quantity += item_quantity
    cart_item.total_amount = cart_item.item_quantity * (
            product.discount_amount if product.discount_percent != 0 else product.original_price
    )
    cart_item.save()
    total_amount += item_amount
    return total_amount

def update_product_in_cart(product_id, total_quantity, cart): 
    total_amount = 0
    # category has been checked to be active in the caller function   
    product = Product.objects.get(id=str(product_id))
    item_amount = total_quantity * (
        product.discount_amount if product.discount_percent != 0 else product.original_price
    )
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id,
                                    defaults={"item_quantity": 0, "total_amount": 0.00})
    cart_item.item_quantity = total_quantity
    cart_item.total_amount = total_quantity * (
        product.discount_amount if product.discount_percent != 0 else product.original_price
    )
    cart_item.save(update_fields=["item_quantity", "total_amount"])
    total_amount += item_amount
    return cart_item

def checkOut(check_out, user):
    if check_out is not None:
        shipping_address = check_out.get("shipping_address")
        billing_address = check_out.get("billing_address")
        checkout = Checkout.objects.create(
            user = user, shipping_address = shipping_address,
            billing_address = billing_address,

        )
        return checkout
    return check_out


