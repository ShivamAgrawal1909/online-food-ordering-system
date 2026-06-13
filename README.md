# Online Food Ordering System

A complete Python Flask-based food ordering web application with user and admin features.

---

## 🔗 Live Demo

👉 [Add your live link here]

**Admin Login:**
- Email: `admin@foodorder.com`
- Password: `admin123`

**Demo User Login:**
- Email: `user@example.com`
- Password: `user123`

---

## Screenshots

> Add 2-3 screenshots here of Home, Cart, and Admin Dashboard.

---

## Tech Stack

| Layer | Technology |
|--------|------------|
| Framework | Flask |
| ORM | Flask-SQLAlchemy |
| Database | SQLite |
| Frontend | Jinja2, Bootstrap |
| Email | Gmail SMTP |
| Auth | Session-based |

---

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   ├── templates/
│   └── utils/
├── config.py
├── run.py
├── seed.py
└── requirements.txt
```

---

## User Features

- Secure Login / Signup
- Profile & Password Management
- Password Reset via Gmail
- Shopping Cart — add, remove, update quantities
- Saved For Later — move items for future purchase
- Wishlist
- Product Browsing — pagination, search, filters (category, rating, price)
- Order History with status filters
- Order Confirmation email notification
- Product Reviews (purchased products only)

---

## Admin Features

- Dashboard with stats and revenue
- Order Management — update status, delete
- Product Management — add, edit, delete
- User Management — edit, delete
- Review Management — view, delete
- Payment Management — update status

---

## Local Setup

```bash
# Clone the repo
git clone https://github.com/ShivamAgrawal1909/online-food-ordering-system.git
cd online-food-ordering-system

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional for email)
# Copy .env.example to .env
# Set MAIL_USERNAME and MAIL_PASSWORD for Gmail password reset

# Seed demo data
python seed.py

# Run the app
python run.py
```

Visit: http://localhost:5000

---

## Email Setup (Optional)

For Gmail password reset:
- Enable 2FA on your Google account
- Generate App Password: Google Account → Security → App Passwords
- Set `MAIL_USERNAME` and `MAIL_PASSWORD` in `.env`

---

## License
This project is for educational and portfolio purposes only.
