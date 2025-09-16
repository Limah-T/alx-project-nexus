def discount_from_vendor(original_price, discount_percent):
    discounted_percentage = discount_percent / 100 # e.g 5/100
    discount_price = original_price * discounted_percentage # 50,000 * 0.05
    return discount_price # 2,500

def customer_payout_sale(original_price, discount_percent):
    customer_payout = original_price - discount_from_vendor(original_price, discount_percent) # 50,00 - 2,500
    return customer_payout 

def platform_payout_sale(original_price):
    platform_percentage = 10 / 100  # e.g 10/100
    discount = original_price * platform_percentage # 50,000 * 0.1
    return discount # 5,000

def vendor_payout_sale(original_price, discount_percent):
    vendor_discount = discount_from_vendor(original_price, discount_percent)
    vendor_price = original_price - vendor_discount # 50,000 - 2,000
    amount = vendor_price - platform_payout_sale(original_price) # 47,500 - 5,000
    return amount #42,500