from flask_mail import Message
from flask import current_app
from app import mail

def send_reset_email(email):
    msg = Message(
        'Password Reset Request',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = (
        'You (or someone else) requested a password reset.\n\n'
        'Click the link below to reset your password:\n'
        'http://127.0.0.1:5000/reset-link-placeholder\n\n'
        'If you didn\'t make this request, you can ignore this email.'
    )
    mail.send(msg)