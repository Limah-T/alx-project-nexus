# Nest – Multi-Vendor E-Commerce API

Nest is a production-ready multi-vendor e-commerce API.
It allows vendors to upload products, customers to purchase and pay seamlessly, and automatically splits payment between the platform and vendors.

---

## 🚀 Tech Stack

* **Backend**: Python, Django, Django REST Framework (DRF)
* **Task Queue**: Celery + RabbitMQ + Redis
* **Database**: PostgreSQL
* **Media Storage**: Cloudinary
* **Containerization**: Docker

---

## 🔑 Main Features

* **User Authentication & JWT** (Customer & Vendor roles)
* **Email Verification & Password Reset**
* **Product, Cart & Checkout Management**
* **Payment Handling with Split Transactions**
* **Task Scheduling (async emails, background jobs)**
* **Filtering, Sorting & Pagination**
* **Rate Limiting & Custom Error Handling**

---

## 📌 Endpoints Overview (with Examples)

### **Authentication**

#### Register Customer

`POST /customer/register/`

**Request**

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "address": "Surulere, Lagos",
  "phone_number": "+2349184270428",
  "email": "jane@example.com",
  "password": "SecurePass123",

}
```

**Response**

```json
{
  "message": "Registration successful. Please verify your email."
}
```

---

#### Register Vendor

`POST /customer/register/`

**Request**

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "business_address": "Surulere, Lagos",
  "business_name": "Baby palm ventures",
  "phone_number": "+2349184270428",
  "email": "jane@example.com",
  "password": "SecurePass123",

}
```

**Response**

```json
{
  "message": "Registration successful. Please verify your email."
}
```

---


#### Login

`POST /login/`

**Request**

```json
{
  "email": "jane@example.com",
  "password": "SecurePass123"
}
```

**Response**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJh...",
  "refresh": "eyJhbGciOiJIUzI1..."
}
```

---

#### Password Reset (Request Link)

`POST /password/reset/`

**Request**

```json
{
  "email": "jane@example.com"
}
```

**Response**

```json
{
  "message": "Password reset link sent to your email."
}
```

---

### **Profiles**

#### Get Vendor Profile

`GET /vendor/profile/`

**Response**

```json
{
  "id": 1,
  "email": "vendor@example.com",
  "store_name": "Best Electronics",
  "created_at": "2025-09-01T10:00:00Z"
}
```

---

### **Catalog**

#### Create Product (Vendor)

`POST /product/` # Only Vendors with Bank account details

**Request**

```json
{
  "name": "Wireless Mouse",
  "price": 25.50,
  "category": "category-UUID",
  "color": 1, # Optional
  "stock": 50,
  "description": "Ergonomic wireless mouse with USB receiver.",
  "image": "product-image",
  "original_price": 135000.00,
  "discount_percent": 20, #Optional
}
```

**Response**

```json
{
  "id": 101,
  "name": "Wireless Mouse",
  "price": 25.50,
  "category": 2,
  "color": 1,
  "stock": 50,
  "description": "Ergonomic wireless mouse with USB receiver.",
  "image": "https-url-for-the-product-image",
  "original_price": 135000.00,
  "discount_percent": 20, #Optional
  "created_at": "2025-09-27T15:00:00Z"
}
```

---

### **Cart & Checkout**

#### Add to Cart

`POST /cart/`

**Request**

```json
{
  "product": "product-UUID",
  "item_quantity": 2
} OR
[
   {
      "product": "product-UUID",
      "item_quantity": 2
   },
   {
      "product": "product2-UUID",
      "item_quantity": 5
   },
   "checkout": {
      "billing_address": "your billing address",
      "shipping_address": "your shipping address"
   }
]
```

**Response**

```json
{
  "success": "Cart has been created successfully",
}
```

---

### **Payment**

#### Initialize Payment

`POST /payment/`

**Request**

```json
]
    {
        "product": "1f850fbb-f589-4dc1-be43-dc7a4783b8fb",
        "item_quantity": 2
    }
    {
        "product": "1f850fbb-f589-4dc1-be43-dc7a4783b8fb",
        "item_quantity": 1
    }

]
```

**Response**

```json
{
  "url": "authorization-url-for-payment",
  "payment_id": "payment-UUID"
}

```

---

#### Verify Payment

`POST /verify/payment/payment-UUID`

**Response**

```json
{
  "status": "success",
  "order": "order-UUID"
}
```

---

## 🛠️ Setup (Development)

```bash
# Clone the repo
git clone <repo_url>
cd nest

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start services
redis-server
rabbitmq-server
celery -A ecommerce_backend worker -l info
python manage.py runserver
```

---

## 📖 Notes

* Ensure `.env` contains valid configs (DB, Redis, RabbitMQ, Cloudinary, Email).
* Celery must be running for async tasks (email sending, etc).
* Docker can be used for containerized setup.

---

## ✅ Status

This project is **production-ready** and can serve as a base for e-commerce platforms.

## Author
Halimah Temitope
