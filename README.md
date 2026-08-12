# 📦 Inventory & Vending System (IVS)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3.1.1-red.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

Welcome to the **Inventory & Vending System (IVS)**! A comprehensive, full-stack marketplace and inventory management web application built with Python and Flask. IVS provides dedicated dashboards for buyers, sellers, and employees to seamlessly manage products, orders, and storefronts.

## ✨ Features

### 🛍️ For Buyers
*   **Intuitive Marketplace**: Browse products across various categories with detailed descriptions and variations.
*   **Shopping Cart**: Easily add, update, and manage items in your cart.
*   **Order Tracking**: Monitor the delivery status of your purchases in real-time.
*   **Address Management**: Save multiple shipping addresses for faster checkout.
*   **Google OAuth Integration**: Quick and secure login/signup using Google.

### 🏪 For Sellers & Employees
*   **Dashboard & Analytics**: Track pending orders and monitor overall store activity.
*   **Inventory Management**: Add new products, manage stock levels, and set product variations (images and names).
*   **Order Fulfillment**: Update delivery statuses and upload delivery evidence.
*   **Employee Roles**: Delegate store management to employees with tracked activity logs.

## 🛠️ Technology Stack

*   **Backend**: [Flask](https://flask.palletsprojects.com/) (Python)
*   **Database**: SQLite (Development) / PostgreSQL (Production ready with `pg8000`)
*   **ORM**: Flask-SQLAlchemy
*   **Authentication**: Flask-Login & Authlib (Google OAuth 2.0)
*   **Security**: Flask-Talisman (Security Headers) & Flask-WTF (CSRF Protection)
*   **Deployment**: Vercel & Gunicorn

## 🚀 Getting Started

### Prerequisites

*   Python 3.8+
*   pip (Python package manager)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/ivs.git
    cd ivs
    ```

2.  **Set up a Virtual Environment**
    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables**
    Create a `.env` file in the root directory and configure the following variables:
    ```env
    SECRET_KEY=your_super_secret_key
    DATABASE_URL=sqlite:///ivs.db
    
    # Google OAuth
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    
    # Email Configuration for Password Resets
    MAIL_USERNAME=your_email@gmail.com
    MAIL_PASSWORD=your_app_password
    ```

5.  **Initialize the Database**
    The database will automatically initialize and seed default accounts when you run the app for the first time.

6.  **Run the Application**
    ```bash
    python app.py
    ```
    Visit `http://localhost:5000` in your browser.

## 📦 Deployment

This application is ready to be deployed on platforms like **Vercel** or **Render**. 
*   It includes a `vercel.json` for Vercel deployment using `@vercel/python`.
*   Includes `ProxyFix` middleware to ensure Google OAuth `_external=True` redirects work perfectly over HTTPS behind reverse proxies.

---

Made with ❤️ by the IVS Team.
