# alx-project-nexus
Project Nexus is the ALX ProDev BE capstone project.

# 🛒 E-Commerce Backend API

This project is part of the **ALX ProDev Backend Program – Project Nexus Week**.  
It simulates a **real-world e-commerce backend system**, focusing on scalability, security, and performance.  
The backend supports **product catalog management, user authentication, and API endpoints for filtering, sorting, and pagination**.

---

## 📌 Overview
The e-commerce backend provides the foundation for an online store.  
It enables:
- **Product and category management**
- **User authentication and authorization**
- **Robust APIs** for frontend integration  
- **Optimized database queries** for scalability and performance  

---

## 🎯 Project Goals
- **CRUD APIs** for products, categories, and user authentication.  
- **Filtering, Sorting, and Pagination** for efficient product discovery.  
- **Database Optimization** using relational schema design and indexing.  
- **API Documentation** with Swagger/OpenAPI for easy frontend consumption.  

---

## ⚙️ Technologies Used
- **Django** – Scalable backend framework.  
- **PostgreSQL** – Relational database with indexing for performance.  
- **JWT** – Secure user authentication.  
- **Swagger/OpenAPI** – API documentation and testing.  

---

## 🔑 Key Features
### 1. CRUD Operations
- Create, Read, Update, Delete operations for **Products** and **Categories**.  
- Secure **User Authentication & Management** using JWT.  

### 2. API Features
- **Filtering & Sorting** – filter products by category and sort by price.  
- **Pagination** – handle large datasets efficiently with paginated responses.  

### 3. API Documentation
- Swagger/OpenAPI integrated for live API testing and documentation.  

---

## 🚀 Implementation Process
### Git Commit Workflow
- `feat:` set up Django project with PostgreSQL  
- `feat:` implement user authentication with JWT  
- `feat:` add product APIs with filtering and pagination  
- `feat:` integrate Swagger documentation for API endpoints  
- `perf:` optimize database queries with indexing  
- `docs:` add API usage instructions in Swagger  

---

## 📤 Deployment
- API is hosted with live documentation available via **Swagger/Postman**.  
- Example: `https://your-deployment-url.com/api/docs/`  

---

## ✅ Evaluation Criteria
1. **Functionality**  
   - CRUD APIs for products, categories, and authentication.  
   - Filtering, sorting, and pagination implemented correctly.  

2. **Code Quality**  
   - Clean, maintainable, and well-structured code.  
   - Proper indexing and optimized database queries.  

3. **User Experience**  
   - Comprehensive and user-friendly API documentation.  
   - Secure authentication.  

4. **Version Control**  
   - Frequent, descriptive Git commit messages.  
   - Well-organized repository structure.  

---

## 📖 How to Run Locally
```bash
# 1. Clone repository
git clone https://github.com/your-username/ecommerce-backend.git
cd ecommerce-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # for Linux/Mac
venv\Scripts\activate      # for Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up PostgreSQL database
# update DATABASES in settings.py with your credentials

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run server
python manage.py runserver

## 🗄️ Database Schema

The relational database schema is designed for performance, scalability, and normalization.  

### Tables
1. **Users**
   - id (PK)
   - username
   - email
   - password (hashed)
   - is_vendor (boolean, default=False)
   - is_active
   - created_at, updated_at

2. **Categories**
   - id (PK)
   - name
   - description
   - created_at, updated_at

3. **Products**
   - id (PK)
   - name
   - description
   - price
   - stock_quantity
   - category_id (FK → Categories.id)
   - created_by (FK → Users.id)
   - created_at, updated_at

ER Diagram
   +-----------+        +-------------+        +-----------+
   |   Users   |        |  Categories |        | Products  |
   +-----------+        +-------------+        +-----------+
   | id (PK)   |<----+  | id (PK)     |<----+  | id (PK)   |
   | username  |     |  | name        |     |  | name      |
   | email     |     |  | description |     |  | price     |
   | password  |     |  | created_at  |     |  | stock_qty |
   | is_vendor |     |  | updated_at  |     |  | category_id (FK) 
   | created_at|     |                  |   |  | created_by (FK) 
   +-----------+     |                  |   |  | created_at|
                     |                  |   |  | updated_at|
                     +------------------+   +--------------+

# This schema allows:
Users → can be customers or vendors.

Categories → organize products.

Products → linked to both categories and vendors (users who created them).

👩‍💻 Author
Halimah Temitope
Backend Engineer | ALX ProDev Backend Program