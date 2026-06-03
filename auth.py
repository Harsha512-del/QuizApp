import streamlit as st
import bcrypt
from db import fetch_one, execute_query
from components.ui import hero
from utils.email_service import generate_otp, send_verification_email
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta


def hash_password(plain: str):
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt())


def verify_password(plain: str, hashed):
    try:
        return bcrypt.checkpw(plain.encode(), hashed)
    except:
        return False


def authenticate(conn, username, password):
    row = fetch_one(
        conn,
        """
        SELECT id, username, password, role, is_verified
        FROM users
        WHERE username = %s
        """,
        (username,)
    )

    if not row:
        return None

    if not row["is_verified"]:
        st.error("Please verify your email first.")
        return None

    stored_hash = row["password"]

    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode()

    if not verify_password(password, stored_hash):
        return None

    return {
        "id": row["id"],
        "username": row["username"],
        "role": row["role"],
    }


def register_page(conn):
    hero("🚀 Create Account", "Secure signup with email verification")

    if "otp_sent" not in st.session_state:
        st.session_state["otp_sent"] = False

    if not st.session_state["otp_sent"]:
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Send OTP", use_container_width=True):
            try:
                validate_email(email)
            except EmailNotValidError as e:
                st.error(str(e))
                return

            if password != confirm:
                st.error("Passwords do not match")
                return

            existing = fetch_one(
                conn,
                "SELECT id FROM users WHERE username=%s OR email=%s",
                (username, email)
            )

            if existing:
                st.error("Username or email already exists")
                return

            otp = generate_otp()

            expiry = datetime.now() + timedelta(minutes=5)

            st.session_state["pending_user"] = {
                "username": username,
                "email": email,
                "password": password,
                "otp": otp,
                "expiry": expiry
            }

            send_verification_email(email, otp)

            st.session_state["otp_sent"] = True
            st.success("OTP sent to your email")
            st.rerun()

    else:
        otp_input = st.text_input("Enter OTP")

        if st.button("Verify OTP", use_container_width=True):
            pending = st.session_state["pending_user"]

            if datetime.now() > pending["expiry"]:
                st.error("OTP expired")
                st.session_state["otp_sent"] = False
                return

            if otp_input != pending["otp"]:
                st.error("Invalid OTP")
                return

            hashed = hash_password(pending["password"])

            execute_query(
                conn,
                """
                INSERT INTO users
                (username, email, password, role, is_verified)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    pending["username"],
                    pending["email"],
                    hashed,
                    "user",
                    True
                )
            )

            user = fetch_one(
                conn,
                "SELECT id, username, role FROM users WHERE username=%s",
                (pending["username"],)
            )

            st.session_state["user"] = user
            st.session_state["otp_sent"] = False
            st.success("Account verified successfully!")
            st.rerun()


def login_page(conn):
    hero("🔐 Welcome Back", "Login securely")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        user = authenticate(conn, username, password)

        if user:
            st.session_state["user"] = user
            st.rerun()


def logout():
    st.session_state.clear()
    st.rerun()


def current_user():
    return st.session_state.get("user")


def is_admin():
    user = current_user()
    return user and user["role"] == "admin"


def require_login():
    if not current_user():
        st.warning("Login required")
        st.stop()


def require_admin():
    require_login()

    if not is_admin():
        st.error("Admin only")
        st.stop()