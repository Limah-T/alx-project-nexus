from ..models import CustomUser, CartItem, Cart, Product, BankAccount, TransactionSplit
from .calculation import vendor_payout_sale, vendor_payout
from datetime import timedelta
from django.utils import timezone
from collections import defaultdict
from .calculation import update_product_in_cart
import os

def check_email_id_exist_in_token(email, id):
    try:
        user = CustomUser.objects.get(email=email, is_active=True)
    except CustomUser.DoesNotExist:
        return False
    except Exception:
            return False
    if str(user.id) != id:
        return False
    return user

def set_user_password_reset_time(user):
    if not user.email_verified:
        return False
    extra_time = timedelta(minutes=int(os.environ.get("RESET_TIME")))
    user.reset_password= True
    user.time_reset= timezone.now() + extra_time
    user.save(update_fields=['reset_password', 'time_reset'])
    return True

def check_if_admin(user):
    if not user.email_verified:
        return False
    if not user.is_active:
        return False
    if not user.is_superuser:
        return False
    return True

def request_instance(request_body):
    many = True
    if not isinstance(request_body, list):
        many = False
        return many
    else:
        return many
    
def merge_duplicate_products_id(product_data):
    merged = defaultdict(int)
    for p in product_data:
        merged[p["product"]] += p["item_quantity"]
    copied_merged = merged.copy()
    return copied_merged

def check_if_user_cart_is_active(user):
    try:
        cart = Cart.objects.get(customer=user, status="unpaid")
    except Cart.DoesNotExist:
        return False
    except Cart.MultipleObjectsReturned:
        return False
    except Exception:
        return False
    return cart

def check_if_products_exist_in_cart(cart): 
    try:
        cartItem = CartItem.objects.get(cart=cart)
    except CartItem.DoesNotExist:
        return False
    return cartItem
    
def check_if_list_of_products_exist(product_data):
    merged_data = merge_duplicate_products_id(product_data)
    for x in merged_data:
        try:
            Product.objects.get(id=str(x), category__is_active=True)
        except Product.DoesNotExist:
            return False
        except Exception:
            return False
    return True

def check_if_product_exist(product_data):
    try:
        product = Product.objects.get(id=str(product_data["product"]), category__is_active=True)
    except Product.DoesNotExist:
        return False
    except Exception:
        return False
    return product

def retrive_cartItems(cart):
    cartItem = CartItem.objects.filter(cart=cart)
    return cartItem

def retrieve_single_cartItem(cart):
    cartItem = CartItem.objects.get(cart=cart)
    return cartItem

def update_list_of_cartItems(cart, product_data):
    merged_data = merge_duplicate_products_id(product_data)  
    all_items = None
    for product in merged_data:
        total_quantity = merged_data[product]
        try:
            cartItems = CartItem.objects.get(cart=cart, product=product)
            cartItems.item_quantity = total_quantity
            cartItems.save(update_fields=["item_quantity"])
            cartItems.total_amount = cartItems.cal_total_amount
            cartItems.save(update_fields=["total_amount"])
        except CartItem.DoesNotExist:
            cartItems = update_product_in_cart(product, total_quantity, cart)
        finally:
            all_items = CartItem.objects.filter(cart=cart, product=product)          
    return all_items
    
def remove_products_from_cart(cart, product_data):
    merged_data = merge_duplicate_products_id(product_data)  
    for product in merged_data:
        try:
            cartItems = CartItem.objects.filter(cart=cart, product=product)
            for item in cartItems:
               item.delete()
        except CartItem.DoesNotExist:
            return False          
    return cartItems

def remove_a_product_from_cart(cart, product_id):
    product = Product.objects.get(id=str(product_id), category__is_active=True)
    try:
        cartItems = CartItem.objects.get(cart=cart, product=product)
    except CartItem.DoesNotExist:
        return False
    cartItems.delete()
    return True
    
def check_list_of_products_quantity(cart, product_data):
    merged_data = merge_duplicate_products_id(product_data)
    total_amount = 0
    for product_id in merged_data:
        quantity = merged_data[product_id]
        try:
            cartItems = CartItem.objects.filter(cart=cart, product=str(product_id))
            for item in cartItems:
                if item.product.stock >= quantity:
                    item.item_quantity = quantity
                    item.save(update_fields=["item_quantity"])
                    item.total_amount = item.cal_total_amount
                    item.save(update_fields=["total_amount"])
                    total_amount += item.total_amount
        except Exception as e:
            print(str(e))
            return False
    return total_amount

def check_product_quantity(cart, product_data):
    product_id = product_data["product"]
    quantity = product_data["item_quantity"]
    amount = 0
    try:
        item = CartItem.objects.get(cart=cart, product=str(product_id))       
        if item.product.stock >= quantity:
            item.item_quantity = quantity
            item.save(update_fields=["item_quantity"])
            item.total_amount = item.cal_total_amount
            item.save(update_fields=["total_amount"])
            amount += item.total_amount
    except Exception as e:
        print(str(e))
        return False
    return amount
    
def vendors_details(product_data):
    vendors_merged_data = defaultdict(int)
    merged_data = merge_duplicate_products_id(product_data)
    for product in merged_data:
        quantity = merged_data[product]
        print(quantity)
        vendor_product = Product.objects.get(id=str(product))
        vendor = BankAccount.objects.get(vendor=vendor_product.vendor)
        if vendor_product.discount_percent != 0:
            discount_amount = vendor_payout_sale(original_price=float(vendor_product.   original_price), discount_percent=vendor_product.discount_percent
                                               )
            vendor_amount = discount_amount * quantity
        else:
            vendor_amount = float(vendor_product.original_price) * quantity

        vendors_merged_data[vendor.subaccount_code] += vendor_amount
    all_vendors = vendors_merged_data.copy()  
    return all_vendors

def vendor_details(product_data):
    product = product_data["product"]
    quantity = product_data["item_quantity"]
    vendor_data = {}
    vendor_product = Product.objects.get(id=str(product))
    vendor = BankAccount.objects.get(vendor=vendor_product.vendor)
    print(vendor)
    print(vendor.subaccount_code)
    if vendor_product.discount_percent != 0:
        discount_amount = vendor_payout_sale(original_price=float(vendor_product.   original_price), discount_percent=vendor_product.discount_percent
                                            )
        vendor_amount = discount_amount * quantity
    else:
        vendor_amount = float(vendor_product.original_price) * quantity
    vendor_data.update({"subaccount": vendor.subaccount_code, 
                       "amount": vendor_amount,
                       "email": vendor.vendor.email
                       })
    return vendor_data

def deduct_product_quantity_after_payment(cart):
    products = CartItem.objects.filter(cart=cart)
    try:
        for product in products:
            quantity = Product.objects.get(id=product.product.id)
            quantity.stock -= product.item_quantity
            quantity.save(update_fields=["stock"])
    except Exception:
        return False
    return quantity



