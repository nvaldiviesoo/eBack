"""
Send email to user with token
"""

import os
from pathlib import Path

from django.core.mail import send_mail
from django.utils.html import strip_tags

def send_forgot_password_email(user_email, token):
    subject = 'Forgot Password'
    html_file = get_template_from_file('forgot_password.html')
    html_file = html_file.replace('[User]', user_email)
    send_mail(
        subject=subject,
        message=strip_tags(html_file),
        html_message=html_file,
        from_email='noreply@ecommercourse.com',
        recipient_list=[user_email],
    )

def get_template_from_file(file_name: str) -> str:
        return Path(
            os.path.join(os.path.dirname(__file__), "templates", file_name)
        ).read_text()