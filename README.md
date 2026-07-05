# 📦 Inventory Management System

A desktop Inventory Management System built with **Python (Tkinter)** and **MySQL**. It provides a full RDBMS-backed workflow for managing employees, suppliers, categories, products, and sales — designed for small businesses and warehouses.

---

## 📌 About The Project

This is a GUI desktop application built with **Tkinter** on top of a **MySQL** database, providing secure login/registration, a live dashboard, and full CRUD management for the core entities of an inventory operation: employees, suppliers, product categories, products, and sales (with receipt preview).

---

## ✨ Features

- 🔐 **Secure authentication** — salted PBKDF2-HMAC-SHA256 password hashing, account registration, and security-question-based password reset
- 📊 **Live dashboard** — at-a-glance stat cards for total employees, suppliers, categories, products, and sales
- 👥 **Employee management** — add, update, delete, and search employees by field
- 🚚 **Supplier management** — add, update, delete, and search suppliers
- 🏷️ **Category management** — full CRUD for product categories
- 🛒 **Product management** — full CRUD with category/supplier linkage and stock status/payment method tracking
- 💰 **Sales module** — record sales against product stock, view a bill/receipt preview before confirming, and browse sales history by date range
- 🖼️ Custom Tkinter UI with rotating login banner and iconography

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application language |
| Tkinter | Desktop GUI framework |
| MySQL | Relational database |
| PyMySQL | Python ↔ MySQL connectivity |
| tkcalendar | Date-picker widgets |
| Pillow | Image handling |

---

## 🏗️ Project Structure

```
Inventory-Managment-System/
├── main.py               # Application entry point (launches login window)
├── login.py              # Login, registration, password reset, banner UI
├── dashboard.py          # Main dashboard with live stats and navigation
├── employees.py          # Employee CRUD + DB connection helper
├── suppliers.py          # Supplier CRUD + search
├── categories.py         # Category CRUD
├── products.py           # Product CRUD, linked to categories & suppliers
├── sales.py              # Sales entry, bill preview, sales history
├── schema.sql            # Full MySQL schema (users, employees, suppliers,
│                          #   categories, products, sales)
├── requirements.txt      # Python dependencies
└── *.png                 # UI icons, logos, and dashboard imagery
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A running MySQL server
- pip

### 1. Clone the repository

```bash
git clone https://github.com/zaeemmughal/Inventory-Managment-System.git
cd Inventory-Managment-System
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up the database

Run the schema against your MySQL server to create the `inventory` database and its tables:

```bash
mysql -u root -p < schema.sql
```

> The app also creates the `users` table automatically on first launch if it doesn't already exist.

### 4. Configure the database connection

By default, the app connects using:

```python
host='localhost'
user='root'
password=''
database='inventory'
```

Update these values in `employees.py` (`connectDataBase()`) if your MySQL setup uses different credentials.

### 5. Run the application

```bash
python main.py
```

This opens the login window. Use **Create Account** to register a new user, then log in to reach the dashboard.

---

## 🗄️ Database Schema

The system uses five core tables, defined in [`schema.sql`](./schema.sql):

- **users** — login accounts with salted/hashed passwords and a security question for password recovery
- **employees** — staff records (role, shift, salary, contact info, etc.)
- **suppliers** — supplier contact and invoice info
- **categories** — product categories
- **products** — inventory items, linked to a category and supplier
- **sales** — sale transactions, linked to a product

---

## 👨‍💻 Developer

**Muhammad Zaeem Mughal**
GitHub: [zaeemmughal](https://github.com/zaeemmughal)

---

## 📜 License

No license has been specified for this project yet. Consider adding one (e.g. MIT) if you plan to accept contributions or reuse.
