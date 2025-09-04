"""
Authentication system for DeepCode with email/password and TOTP support
"""

import bcrypt
import pyotp
import qrcode
import io
import base64
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st
from sqlalchemy.orm import Session


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password
        hashed: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def generate_totp_secret() -> str:
    """
    Generate a new TOTP secret
    
    Returns:
        Base32 encoded secret
    """
    return pyotp.random_base32()


def generate_totp_qr_code(email: str, secret: str) -> str:
    """
    Generate a QR code for TOTP setup
    
    Args:
        email: User's email address
        secret: TOTP secret
        
    Returns:
        Base64 encoded QR code image
    """
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name='DeepCode AI'
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return img_base64


def verify_totp(secret: str, token: str) -> bool:
    """
    Verify a TOTP token
    
    Args:
        secret: User's TOTP secret
        token: 6-digit TOTP token
        
    Returns:
        True if token is valid, False otherwise
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)  # Allow 30 second window


def generate_jwt_token(user_id: int, email: str, is_admin: bool = False, is_super_admin: bool = False) -> str:
    """
    Generate a JWT token for a user
    
    Args:
        user_id: User's database ID
        email: User's email
        is_admin: Whether user is an admin
        is_super_admin: Whether user is a super admin
        
    Returns:
        JWT token string
    """
    secret_key = st.secrets.get("jwt_secret", "your-secret-key-change-in-production")
    
    payload = {
        'user_id': user_id,
        'email': email,
        'is_admin': is_admin,
        'is_super_admin': is_super_admin,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    secret_key = st.secrets.get("jwt_secret", "your-secret-key-change-in-production")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def authenticate_user(session: Session, email: str, password: str, totp_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user with email, password, and optional TOTP
    
    Args:
        session: Database session
        email: User's email
        password: User's password
        totp_code: Optional TOTP code
        
    Returns:
        User data dict if authentication successful, None otherwise
    """
    from database.models import User
    
    # Find user by email
    user = session.query(User).filter_by(email=email).first()
    
    if not user:
        return None
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return None
    
    # Verify TOTP if user has it enabled
    if user.totp_secret:
        if not totp_code:
            return {"requires_totp": True, "user_id": user.id}
        
        if not verify_totp(user.totp_secret, totp_code):
            return None
    
    # Generate JWT token
    token = generate_jwt_token(user.id, user.email, user.is_admin, user.is_super_admin)
    
    return {
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_admin": user.is_admin,
        "is_super_admin": user.is_super_admin,
        "token": token
    }


def register_user(session: Session, email: str, password: str, full_name: str) -> Optional[Dict[str, Any]]:
    """
    Register a new user
    
    Args:
        session: Database session
        email: User's email
        password: User's password
        full_name: User's full name
        
    Returns:
        User data dict if registration successful, None otherwise
    """
    from database.models import User
    
    # Check if user already exists
    existing_user = session.query(User).filter_by(email=email).first()
    if existing_user:
        return None
    
    # Create new user
    hashed_password = hash_password(password)
    new_user = User(
        email=email,
        password_hash=hashed_password,
        full_name=full_name,
        is_admin=False,
        is_super_admin=False
    )
    
    # Special case: jerome@rotz.host is always super admin
    if email == "jerome@rotz.host":
        new_user.is_admin = True
        new_user.is_super_admin = True
    
    session.add(new_user)
    session.commit()
    
    return {
        "user_id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "requires_totp_setup": True
    }


def setup_user_totp(session: Session, user_id: int, totp_code: str, secret: str) -> bool:
    """
    Set up TOTP for a user
    
    Args:
        session: Database session
        user_id: User's ID
        totp_code: TOTP code to verify
        secret: TOTP secret
        
    Returns:
        True if setup successful, False otherwise
    """
    from database.models import User
    
    # Verify the TOTP code first
    if not verify_totp(secret, totp_code):
        return False
    
    # Update user with TOTP secret
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return False
    
    user.totp_secret = secret
    session.commit()
    
    return True


def check_authentication() -> Optional[Dict[str, Any]]:
    """
    Check if user is authenticated in Streamlit session
    
    Returns:
        User data if authenticated, None otherwise
    """
    if 'user' not in st.session_state:
        return None
    
    user_data = st.session_state.user
    
    # Verify token is still valid
    if 'token' in user_data:
        decoded = decode_jwt_token(user_data['token'])
        if not decoded:
            # Token expired or invalid
            del st.session_state.user
            return None
    
    return user_data


def require_authentication():
    """
    Decorator/function to require authentication for a Streamlit page
    """
    user = check_authentication()
    if not user:
        st.error("🔒 Please log in to access this page")
        st.stop()
    return user


def require_admin():
    """
    Decorator/function to require admin privileges for a Streamlit page
    """
    user = check_authentication()
    if not user or not user.get('is_admin', False):
        st.error("🔒 Admin privileges required to access this page")
        st.stop()
    return user


def require_super_admin():
    """
    Decorator/function to require super admin privileges for a Streamlit page
    """
    user = check_authentication()
    if not user or not user.get('is_super_admin', False):
        st.error("🔒 Super admin privileges required to access this page")
        st.stop()
    return user


def logout():
    """
    Log out the current user
    """
    if 'user' in st.session_state:
        del st.session_state.user
    
    # Clear any other session data
    for key in list(st.session_state.keys()):
        if key.startswith('auth_'):
            del st.session_state[key]