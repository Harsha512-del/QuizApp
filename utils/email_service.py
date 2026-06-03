import smtplib
import secrets
import streamlit as st
from email.mime.text import MIMEText


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


def send_verification_email(receiver_email, otp):
    sender_email = st.secrets["email"]["address"]
    app_password = st.secrets["email"]["app_password"]

    subject = "Quiz Platform Email Verification"

    body = f"""
Hello,

Your OTP for Quiz Intelligence Platform is:

{otp}

This code expires in 5 minutes.

If you did not request this, ignore this email.

Regards,
Quiz Platform Team
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(
            sender_email,
            receiver_email,
            msg.as_string()
        )