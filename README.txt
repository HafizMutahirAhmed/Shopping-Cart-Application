# 🛒 Shopping Cart Application

This is a **Flask-based Shopping Cart Web Application** that simulates a real-world online shopping experience. It allows users to browse products, manage their cart, and place orders. The system includes both customer and admin functionality, backed by an SQLite database.

---

## ⚙️ Features

- 🔐 **User Authentication**
  - Admin and Customer login
  - Pre-created test accounts for demonstration

- 🛍️ **Product Management**
  - Admin can add, update, and delete products
  - Product inventory is displayed dynamically

- 🛒 **Shopping Cart**
  - Customers can add/remove items to/from their cart
  - Quantity-based cart management

- 🧾 **Order History**
  - Orders are tracked and stored in the database
  - Customers can view their past purchases

- 📦 **SQLite Database Integration**
  - All records are maintained in `CEP.sqlite`
  - Easy to inspect with DB Browser for SQLite

---

## 👥 Test Credentials

Use these accounts for testing the system:

### 🔐 Admin Account
- **Username:** `asra@gmail.com`  
- **Password:** `123`

### 🧑‍💼 Customer Account
- **Username:** `mutahir@gmail.com`  
- **Password:** `123`

---

## Project Setup Instructions

1. Install Python:
   Ensure Python is installed on your local system.

2. Open Project Directory:
   Open the project directory using the console, PowerShell, or VS Code terminal.

** Note: It is better to create and use a virtual environment. If you prefer not to, you can skip this step. 

3. (Optional)Install Virtual Environment Library:
   Install the library with:
   pip install virtualenv
   

4. (Optional)Create a Virtual Environment:
   Create the virtual environment by running:
   python -m venv venv-env
   

5. (Optional)Activate the Virtual Environment:
   Activate the virtual environment using the following command:
   venv-env/Scripts/Activate.ps1
   

6. Install Required Libraries:
   Install the necessary libraries with:
   pip install Flask


7. Run the Project:
   Finally, to execute the code, run:
   python app.py
 

**Checking the Database:
If you want to check the database, you can install DB Browser for SQLite. This tool allows you to view and edit the database contents easily.
