# Online Food Ordering System

A complete Python Flask-based food ordering web application with user and admin features.

## Features

### User Features
- **Login/Signup** - Secure authentication
- **Profile Management** - Update profile and password
- **Password Reset** - Via Gmail (requires app password)
- **Shopping Cart** - Add, remove, update quantities
- **Saved For Later** - Move items for future purchase
- **Wishlist** - Save products for later
- **Product Browsing** - Pagination, search, filters (category, rating, price)
- **Shipping Information** - Stored in session for checkout
- **Order History** - View with status filters
- **Order Confirmation** - Email notification on placement
- **Product Reviews** - Review purchased products only

### Admin Features
- **Dashboard** - Stats, revenue, recent orders
- **Order Management** - Update status, delete orders
- **Product Management** - Add, edit, delete products
- **User Management** - Edit and delete users
- **Review Management** - View and delete reviews
- **Payment Management** - Update payment status

## Setup

1. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Configure environment** (optional, for email)
   - Copy `.env.example` to `.env`
   - For Gmail password reset:
     - Enable 2FA on your Google account
     - Generate an App Password: Google Account → Security → App passwords
     - Set `MAIL_USERNAME` and `MAIL_PASSWORD` in `.env` or environment

3. **Seed the database**
   ```
   python seed.py
   ```
   Creates: 8 products, admin (admin@foodorder.com / admin123), user (user@example.com / user123)

4. **Run the app**
   ```
   python run.py
   ```
   Open http://localhost:5000

## Project Structure

```
├── app/
│   ├── __init__.py      # App factory
│   ├── models.py        # Database models
│   ├── routes/          # Blueprints (auth, main, admin)
│   ├── templates/       # Jinja2 templates
│   └── utils/           # Email utilities
├── config.py
├── run.py
├── seed.py
└── requirements.txt
```
