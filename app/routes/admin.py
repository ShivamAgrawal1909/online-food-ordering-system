from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from app.models import User, Product, Order, OrderItem, Review, Payment, CartItem, Wishlist
from app.routes.forms import ProductForm
from app.utils.email import send_order_confirmation_email

bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

@bp.route('/')
@login_required
@admin_required
def index():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    pending_orders = Order.query.filter_by(status='pending').count()
    return render_template('admin/dashboard.html',
                         total_users=total_users, total_products=total_products,
                         total_orders=total_orders, total_revenue=total_revenue,
                         recent_orders=recent_orders, pending_orders=pending_orders)

@bp.route('/orders')
@login_required
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    query = Order.query
    if status_filter:
        query = query.filter(Order.status == status_filter)
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/orders.html', orders=orders)

@bp.route('/orders/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def update_order_status(id):
    order = Order.query.get_or_404(id)
    status = request.form.get('status')
    if status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        order.status = status
        db.session.commit()
        flash(f'Order #{id} status updated to {status}.', 'success')
    return redirect(url_for('admin.orders'))

@bp.route('/orders/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_order(id):
    order = Order.query.get_or_404(id)
    if order.payment:
        db.session.delete(order.payment)
    for item in order.items:
        product = Product.query.get(item.product_id)
        if product and product.stock is not None:
            product.stock += item.quantity
    db.session.delete(order)
    db.session.commit()
    flash(f'Order #{id} deleted.', 'success')
    return redirect(url_for('admin.orders'))

@bp.route('/products')
@login_required
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/products.html', products=products)

@bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            image_url=form.image_url.data or None,
            stock=form.stock.data
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{product.name}" added.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', form=form)

@bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category = form.category.data
        product.image_url = form.image_url.data or None
        product.stock = form.stock.data
        db.session.commit()
        flash(f'Product "{product.name}" updated.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', form=form, product=product)

@bp.route('/products/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{name}" deleted.', 'success')
    return redirect(url_for('admin.products'))

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/users.html', users=users)

@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        user.phone = request.form.get('phone') or None
        user.address = request.form.get('address') or None
        user.role = request.form.get('role', user.role)
        db.session.commit()
        flash(f'User {user.name} updated.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_edit.html', user=user)

@bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    user = User.query.get_or_404(id)
    name = user.name
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{name}" deleted.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/reviews')
@login_required
@admin_required
def reviews():
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.order_by(Review.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/reviews.html', reviews=reviews)

@bp.route('/reviews/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_review(id):
    review = Review.query.get_or_404(id)
    product = Product.query.get(review.product_id)
    if product and product.rating_count > 0:
        total = product.rating * product.rating_count - review.rating
        product.rating_count -= 1
        product.rating = total / product.rating_count if product.rating_count > 0 else 0
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'success')
    return redirect(url_for('admin.reviews'))

@bp.route('/payments')
@login_required
@admin_required
def payments():
    page = request.args.get('page', 1, type=int)
    payments = Payment.query.order_by(Payment.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/payments.html', payments=payments)

@bp.route('/payments/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def update_payment_status(id):
    payment = Payment.query.get_or_404(id)
    status = request.form.get('status')
    if status in ['pending', 'completed', 'failed', 'refunded']:
        payment.status = status
        db.session.commit()
        flash('Payment status updated.', 'success')
    return redirect(url_for('admin.payments'))
