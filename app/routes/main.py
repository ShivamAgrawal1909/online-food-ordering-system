from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, OrderItem, CartItem, Wishlist, SavedForLater, Review, Payment
from app.routes.forms import ProfileForm, ChangePasswordForm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    products = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    return render_template('main/index.html', products=products)

@bp.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)
    
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.description.ilike(f'%{search}%'))
    if category:
        query = query.filter(Product.category.ilike(category))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if min_rating is not None:
        query = query.filter(Product.rating >= min_rating)
    
    products = query.paginate(page=page, per_page=12)
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('main/products.html', products=products, categories=categories)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    pwd_form = ChangePasswordForm()
    if form.validate_on_submit() and 'change_password_submit' not in request.form:
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('main.profile'))
    if request.method == 'POST' and 'change_password_submit' in request.form:
        pwd_form = ChangePasswordForm()
        if pwd_form.validate_on_submit():
            if current_user.check_password(pwd_form.current_password.data):
                current_user.set_password(pwd_form.new_password.data)
                db.session.commit()
                flash('Password changed.', 'success')
            else:
                flash('Current password is incorrect.', 'danger')
            return redirect(url_for('main.profile'))
    return render_template('main/profile.html', form=form, pwd_form=pwd_form)

@bp.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    reviews = Review.query.filter_by(product_id=id).order_by(Review.created_at.desc()).all()
    in_cart = False
    in_wishlist = False
    can_review = False
    if current_user.is_authenticated:
        in_cart = CartItem.query.filter_by(user_id=current_user.id, product_id=id).first() is not None
        in_wishlist = Wishlist.query.filter_by(user_id=current_user.id, product_id=id).first() is not None
        can_review = Order.query.join(OrderItem).filter(
            Order.user_id == current_user.id,
            OrderItem.product_id == id,
            Order.status.in_(['shipped', 'delivered'])
        ).first() is not None and Review.query.filter_by(user_id=current_user.id, product_id=id).first() is None
    return render_template('main/product_detail.html', product=product, reviews=reviews, 
                         in_cart=in_cart, in_wishlist=in_wishlist, can_review=can_review)

@bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = request.form.get('quantity', 1, type=int)
    product = Product.query.get_or_404(product_id)
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity = min(cart_item.quantity + quantity, product.stock or 99)
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=min(quantity, product.stock or 99))
        db.session.add(cart_item)
    db.session.commit()
    flash(f'{product.name} added to cart.', 'success')
    return redirect(request.referrer or url_for('main.products'))

@bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    quantity = request.form.get('quantity', 1, type=int)
    cart_item.quantity = max(1, min(quantity, cart_item.product.stock or 99))
    db.session.commit()
    flash('Cart updated.', 'success')
    return redirect(url_for('main.cart'))

@bp.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('main.cart'))

@bp.route('/cart/save-for-later/<int:item_id>')
@login_required
def save_for_later(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    existing = SavedForLater.query.filter_by(user_id=current_user.id, product_id=cart_item.product_id).first()
    if not existing:
        saved = SavedForLater(user_id=current_user.id, product_id=cart_item.product_id, quantity=cart_item.quantity)
        db.session.add(saved)
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item moved to Saved For Later.', 'success')
    return redirect(url_for('main.cart'))

@bp.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(i.product.price * i.quantity for i in items)
    return render_template('main/cart.html', items=items, total=total)

@bp.route('/saved-for-later')
@login_required
def saved_for_later():
    items = SavedForLater.query.filter_by(user_id=current_user.id).all()
    return render_template('main/saved_for_later.html', items=items)

@bp.route('/saved-for-later/move-to-cart/<int:item_id>')
@login_required
def move_to_cart(item_id):
    saved = SavedForLater.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=saved.product_id).first()
    if cart_item:
        cart_item.quantity += saved.quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=saved.product_id, quantity=saved.quantity)
        db.session.add(cart_item)
    db.session.delete(saved)
    db.session.commit()
    flash('Item moved to cart.', 'success')
    return redirect(url_for('main.saved_for_later'))

@bp.route('/saved-for-later/remove/<int:item_id>')
@login_required
def remove_saved(item_id):
    saved = SavedForLater.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(saved)
    db.session.commit()
    flash('Item removed.', 'info')
    return redirect(url_for('main.saved_for_later'))

@bp.route('/wishlist/add/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    Product.query.get_or_404(product_id)
    if Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first():
        flash('Already in wishlist.', 'info')
    else:
        w = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(w)
        db.session.commit()
        flash('Added to wishlist.', 'success')
    return redirect(request.referrer or url_for('main.products'))

@bp.route('/wishlist/remove/<int:product_id>')
@login_required
def remove_from_wishlist(product_id):
    w = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
    db.session.delete(w)
    db.session.commit()
    flash('Removed from wishlist.', 'info')
    return redirect(request.referrer or url_for('main.wishlist'))

@bp.route('/wishlist')
@login_required
def wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('main/wishlist.html', items=items)

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('main.cart'))
    total = sum(i.product.price * i.quantity for i in items)
    if request.method == 'POST':
        shipping_name = request.form.get('shipping_name') or current_user.name
        shipping_email = request.form.get('shipping_email') or current_user.email
        shipping_phone = request.form.get('shipping_phone') or current_user.phone
        shipping_address = request.form.get('shipping_address') or current_user.address
        if not all([shipping_name, shipping_email, shipping_address]):
            flash('Please fill in all shipping details.', 'danger')
            return render_template('main/checkout.html', items=items, total=total)
        order = Order(
            user_id=current_user.id,
            status='pending',
            total=total,
            shipping_name=shipping_name,
            shipping_email=shipping_email,
            shipping_phone=shipping_phone,
            shipping_address=shipping_address
        )
        db.session.add(order)
        db.session.flush()
        for item in items:
            oi = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
            db.session.add(oi)
            if item.product.stock is not None:
                item.product.stock -= item.quantity
        payment = Payment(order_id=order.id, amount=total, status='completed')
        db.session.add(payment)
        for item in items:
            db.session.delete(item)
        db.session.commit()
        from app.utils.email import send_order_confirmation_email
        send_order_confirmation_email(current_user, order)
        flash(f'Order #{order.id} placed successfully! Confirmation sent to your email.', 'success')
        return redirect(url_for('main.order_detail', id=order.id))
    total = sum(i.product.price * i.quantity for i in items)
    session['checkout_shipping'] = {
        'name': current_user.name,
        'email': current_user.email,
        'phone': current_user.phone or '',
        'address': current_user.address or ''
    }
    return render_template('main/checkout.html', items=items, total=total)

@bp.route('/orders')
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    query = Order.query.filter_by(user_id=current_user.id)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('main/orders.html', orders=orders)

@bp.route('/order/<int:id>')
@login_required
def order_detail(id):
    order = Order.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('main/order_detail.html', order=order)

@bp.route('/review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '')
    if not (1 <= rating <= 5):
        flash('Invalid rating.', 'danger')
        return redirect(request.referrer)
    has_ordered = Order.query.join(OrderItem).filter(
        Order.user_id == current_user.id,
        OrderItem.product_id == product_id,
        Order.status.in_(['shipped', 'delivered'])
    ).first()
    if not has_ordered:
        flash('You can only review products you have purchased.', 'danger')
        return redirect(request.referrer)
    if Review.query.filter_by(user_id=current_user.id, product_id=product_id).first():
        flash('You have already reviewed this product.', 'info')
        return redirect(request.referrer)
    review = Review(user_id=current_user.id, product_id=product_id, rating=rating, comment=comment)
    db.session.add(review)
    product = Product.query.get(product_id)
    total_rating = product.rating * product.rating_count + rating
    product.rating_count += 1
    product.rating = total_rating / product.rating_count
    db.session.commit()
    flash('Review submitted!', 'success')
    return redirect(request.referrer)
