from .models import TransactionSplit, BankAccount
from .utils.helper_functions import vendors_details, vendor_details
import requests, os

PAYMENT_SECRET_KEY = os.environ.get("PAYMENT_SECRET_KEY")
SUBACCOUNT_URL = os.environ.get("SUBACCOUNT_ENDPOINT")
BANK_CODE_URL = os.environ.get("BANK_CODE")
TRANSACTION_SPLIT = os.environ.get("TRANSACTION_SPLIT")
TRANSACTION_INITIALIZATION = os.environ.get("TRANSACTION_INITIALIZATION")
PAYMENT_VERIFY = os.environ.get("PAYMENT_VERIFY")

def getSubAccount(subaccount_id):
    headers = {
        "Authorization": f"Bearer {PAYMENT_SECRET_KEY}"
    }

    try:
        response = requests.get(url=f"{SUBACCOUNT_URL}/{subaccount_id}", headers=headers)
        if response.status_code != 200:
            return False
    except Exception:
        return False
    return response.json()

def getBankCode(bank_name):
    headers = {
        "Authorization": f"Bearer {PAYMENT_SECRET_KEY}"
    }
    try:
        response = requests.get(url=BANK_CODE_URL, headers=headers)
        banks = response.json()["data"]
        for b in banks:
            if b["name"] == bank_name:
                code = b["code"]
                break
    except Exception:
        return False
    return code

def createSubAccount(business_name, bank_code, account_no):
    headers = {
        "Authorization": f"Bearer {PAYMENT_SECRET_KEY}",
        "Content_type": "application/json"
    }

    payload = {
        "business_name": business_name,
        "settlement_bank": bank_code,
        "account_number": account_no,
        "percentage_charge": int(os.environ.get("PLATFORM_PERCENTAGE"))
    }

    try:
        response = requests.post(url=SUBACCOUNT_URL, headers=headers, json=payload)
        data = response.json()
    except Exception:
        return False
    return data

def createTransactionSplit(name, subaccount_code):
    headers = {
        "Authorization": f"Bearer {PAYMENT_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": name,
        "type": "percentage",
        "currency": "NGN",
        "subaccounts": [
            {
                "subaccount": subaccount_code,
                "share": int(os.environ.get("VENDOR_PERCENTAGE"))
            }
        ]
    }

    try:
        response = requests.post(url=TRANSACTION_SPLIT, headers=headers, json=payload)
        if response.status_code != 200:
            return False
    except Exception:
        return False
    return response.json()

def transactionSplit(name, vendor, subaccount_code):
    response = createTransactionSplit(name, subaccount_code)
    if not response:
        return False
    split_code = response["data"]["split_code"]
    TransactionSplit.objects.create(
        vendor=vendor, split_code=split_code,
    )
    return True

def initializeTransactionVendors(product_data, many):
    headers = {
        "Authorization": f"Bearer {PAYMENT_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    all_vendors = vendors_details(product_data)
    for transaction in all_vendors:
        amount = all_vendors[transaction]
        vendor = BankAccount.objects.get(subaccount_code=transaction)
        payload = {
            "amount": amount * 100,
            "email": vendor.vendor.email,
            "subaccount": str(vendor.subaccount_code)
        }

        try:
            response = requests.post(url=TRANSACTION_INITIALIZATION, headers=headers, json=payload)
            if response.status_code != 200:
                return False
        except Exception:
            return False
    return response.json()

def initializeTransaction(product_data):
    headers = {
        "Authorization": f"Bearer {PAYMENT_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    vendor = vendor_details(product_data)
    vendor_bank_data = BankAccount.objects.get(subaccount_code=vendor["subaccount"])

    payload = {
            "amount": vendor["amount"] * 100,
            "email": vendor_bank_data.vendor.email,
            "subaccount": str(vendor["subaccount"])
        }

    try:
        response = requests.post(url=TRANSACTION_INITIALIZATION, headers=headers, json=payload)
        if response.status_code != 200:
            return False
    except Exception as e:
        return False
    return response.json()

def paymentVerify(reference):
    headers = {
        "Authorization": f"Bearer {PAYMENT_SECRET_KEY}"
    }

    try:
        response = requests.get(url=f"{PAYMENT_VERIFY}/{reference}", headers=headers)
        if response.status_code != 200:
            return False
    except Exception as e:
        return False
    return response.json()

