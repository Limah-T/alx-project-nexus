import requests, os
PAYMENT_SECRET_KEY = os.environ.get("PAYMENT_TEST_SECRET_KEY")
SUBACCOUNT_URL = os.environ.get("SUBACCOUNT_ENDPOINT")
BANK_CODE_URL = os.environ.get("BANK_CODE")

def getSubAccount(subaccount_id):
    headers = {
        "Authorization": f"Bearer {PAYMENT_SECRET_KEY}"
    }

    try:
        response = requests.get(url=f"{SUBACCOUNT_URL}/{subaccount_id}", headers=headers)
        data = response.json()["data"]
    except Exception as e:
        print(str(e))
        return False
    return data

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
    except Exception as e:
        print(str(e))
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
        "percentage_charge": 10
    }

    try:
        response = requests.post(url=SUBACCOUNT_URL, headers=headers, json=payload)
        data = response.json()["data"]
    except Exception as e:
        print(str(e))
        return False
    return data