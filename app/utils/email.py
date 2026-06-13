from flask import current_app, url_for
from threading import Thread
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_async_email(app, msg, to_email):
    with app.app_context():
        try:
            server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
            server.starttls()
            server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Email error: {e}")

def send_email(to_email, subject, html_body):
    if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
        print("Gmail credentials not configured. Set MAIL_USERNAME and MAIL_PASSWORD environment variables.")
        return
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = current_app.config['MAIL_USERNAME']
    msg['To'] = to_email
    msg.attach(MIMEText(html_body, 'html'))
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg, to_email)
    ).start()

def send_password_reset_email(user, token):
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    subject = 'Reset Your Password - Online Food Ordering'
    html = f'''
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2d3748;">Password Reset Request</h2>
            <p>Hello {user.name},</p>
            <p>You requested a password reset. Click the link below to reset your password:</p>
            <p><a href="{reset_url}" style="background: #3182ce; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>This link expires in 30 minutes.</p>
            <p>If you did not request this, please ignore this email.</p>
            <hr style="margin: 20px 0;">
            <p style="color: #718096; font-size: 12px;">Online Food Ordering</p>
        </div>
    </body>
    </html>
    '''
    send_email(user.email, subject, html)

def send_order_confirmation_email(user, order):
    if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
        return
    subject = f'Order Confirmation #{order.id} - Online Food Ordering'
    items_html = ''.join([f'<tr><td>{item.product.name}</td><td>{item.quantity}</td><td>Rs.{item.price:.2f}</td></tr>' for item in order.items])
    html = f'''
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2d3748;">Order Confirmation</h2>
            <p>Hello {user.name},</p>
            <p>Thank you for your order! Here are the details:</p>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #e2e8f0;"><th style="padding: 10px; text-align: left;">Item</th><th>Qty</th><th>Price</th></tr>
                {items_html}
            </table>
            <p><strong>Total: Rs.{order.total:.2f}</strong></p>
            <p><strong>Shipping to:</strong> {order.shipping_name}, {order.shipping_address}</p>
            <hr style="margin: 20px 0;">
            <p style="color: #718096; font-size: 12px;">Online Food Ordering</p>
        </div>
    </body>
    </html>
    '''
    send_email(user.email, subject, html)
