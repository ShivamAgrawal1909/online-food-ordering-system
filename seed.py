"""Seed script to populate database with dummy data."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from config import Config
from app.models import User, Product, Order, OrderItem, Review, Payment

def seed():
    app = create_app(Config)
    with app.app_context():
        if User.query.filter_by(email='admin@foodorder.com').first():
            print('Database already seeded.')
            return

        # Admin user
        admin = User(
            email='admin@foodorder.com',
            name='Admin User',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # Regular user
        user = User(
            email='user@example.com',
            name='John Doe',
            phone='+1234567890',
            address='123 Main St, City'
        )
        user.set_password('user123')
        db.session.add(user)
        db.session.flush()

        # 8 Dummy products
        products_data = [
            {
                'name': 'Margherita Pizza',
                'description': 'Classic tomato sauce, fresh mozzarella, and basil. A timeless favorite.',
                'price': 299.00,
                'category': 'Pizza',
                'image_url': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400',
                'rating': 4.8,
                'rating_count': 45,
                'stock': 50
            },
            {
                'name': 'Grilled Chicken Burger',
                'description': 'Juicy grilled chicken breast with lettuce, tomato, and special sauce.',
                'price': 249.00,
                'category': 'Burgers',
                'image_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400',
                'rating': 4.6,
                'rating_count': 32,
                'stock': 30
            },
            {
                'name': 'Caesar Salad',
                'description': 'Crisp romaine lettuce, parmesan, croutons, and Caesar dressing.',
                'price': 199.00,
                'category': 'Salads',
                'image_url': 'https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400',
                'rating': 4.5,
                'rating_count': 28,
                'stock': 25
            },
            {
                'name': 'Beef Tacos (3 pcs)',
                'description': 'Seasoned beef, lettuce, cheese, salsa, and sour cream in soft tortillas.',
                'price': 279.00,
                'category': 'Mexican',
                'image_url': 'https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=400',
                'rating': 4.7,
                'rating_count': 41,
                'stock': 40
            },
            {
                'name': 'Chicken Biryani',
                'description': 'Fragrant basmati rice with tender chicken, spices, and caramelized onions.',
                'price': 349.00,
                'category': 'Indian',
                'image_url': 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400',
                'rating': 4.9,
                'rating_count': 67,
                'stock': 35
            },
            {
                'name': 'Salmon Sushi Roll',
                'description': 'Fresh salmon, avocado, cucumber wrapped in seaweed and rice.',
                'price': 329.00,
                'category': 'Japanese',
                'image_url': 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400',
                'rating': 4.8,
                'rating_count': 52,
                'stock': 20
            },
            {
                'name': 'Chocolate Lava Cake',
                'description': 'Warm chocolate cake with molten center, served with vanilla ice cream.',
                'price': 189.00,
                'category': 'Desserts',
                'image_url': 'https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=400',
                'rating': 4.9,
                'rating_count': 89,
                'stock': 15
            },
            {
                'name': 'Fresh Lemonade',
                'description': 'Hand-squeezed lemons with a touch of mint. Refreshing and natural.',
                'price': 99.00,
                'category': 'Beverages',
                'image_url': 'https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400',
                'rating': 4.6,
                'rating_count': 112,
                'stock': 100
            }
        ]

        for pd in products_data:
            p = Product(**pd)
            db.session.add(p)

        db.session.flush()

        # Sample order for user
        order = Order(
            user_id=user.id,
            status='delivered',
            total=548.00,
            shipping_name='John Doe',
            shipping_email='user@example.com',
            shipping_phone='+1234567890',
            shipping_address='123 Main St, City'
        )
        db.session.add(order)
        db.session.flush()

        oi1 = OrderItem(order_id=order.id, product_id=1, quantity=1, price=299.00)
        oi2 = OrderItem(order_id=order.id, product_id=2, quantity=1, price=249.00)
        db.session.add_all([oi1, oi2])

        db.session.add(Payment(order_id=order.id, amount=548.00, status='completed'))

        # Sample review
        review = Review(user_id=user.id, product_id=1, rating=5, comment='Amazing pizza! Best I have ever had.')
        db.session.add(review)

        db.session.commit()
        print('Seed completed successfully!')
        print('Admin: admin@foodorder.com / admin123')
        print('User: user@example.com / user123')

if __name__ == '__main__':
    seed()
