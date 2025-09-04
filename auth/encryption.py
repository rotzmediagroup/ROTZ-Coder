"""
Encryption utilities for securing API keys
"""

from cryptography.fernet import Fernet
import streamlit as st
import os
import base64
from typing import Optional


def get_or_create_encryption_key() -> bytes:
    """
    Get or create an encryption key for API key storage
    
    Returns:
        Encryption key as bytes
    """
    # Try to get key from Streamlit secrets first
    if hasattr(st, 'secrets') and 'encryption_key' in st.secrets:
        key = st.secrets['encryption_key']
        if isinstance(key, str):
            # If it's a string, encode it properly
            if len(key) == 44:  # Fernet key length when base64 encoded
                return key.encode()
            else:
                # Generate a proper key from the secret
                return base64.urlsafe_b64encode(key.encode().ljust(32)[:32])
    
    # Try environment variable
    env_key = os.environ.get('DEEPCODE_ENCRYPTION_KEY')
    if env_key:
        if len(env_key) == 44:
            return env_key.encode()
        else:
            return base64.urlsafe_b64encode(env_key.encode().ljust(32)[:32])
    
    # For development, use a default key (NOT FOR PRODUCTION!)
    # In production, always set the encryption key in secrets or environment
    default_key = Fernet.generate_key()
    print("⚠️  WARNING: Using generated encryption key. Set DEEPCODE_ENCRYPTION_KEY in production!")
    return default_key


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for storage
    
    Args:
        api_key: Plain text API key
        
    Returns:
        Encrypted API key as string
    """
    key = get_or_create_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> Optional[str]:
    """
    Decrypt an API key from storage
    
    Args:
        encrypted_key: Encrypted API key string
        
    Returns:
        Decrypted API key or None if decryption fails
    """
    try:
        key = get_or_create_encryption_key()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"Error decrypting API key: {e}")
        return None


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for display purposes
    
    Args:
        api_key: API key to mask
        visible_chars: Number of characters to show at start and end
        
    Returns:
        Masked API key string
    """
    if not api_key or len(api_key) < (visible_chars * 2 + 4):
        return "********"
    
    return f"{api_key[:visible_chars]}{'*' * (len(api_key) - visible_chars * 2)}{api_key[-visible_chars:]}"


def validate_api_key_format(api_key: str, provider: str) -> bool:
    """
    Validate API key format for different providers
    
    Args:
        api_key: API key to validate
        provider: Provider name (openai, anthropic, etc.)
        
    Returns:
        True if format appears valid, False otherwise
    """
    if not api_key or len(api_key) < 10:
        return False
    
    # Provider-specific validation
    validations = {
        "openai": lambda k: k.startswith("sk-") and len(k) > 20,
        "anthropic": lambda k: k.startswith("sk-ant-") and len(k) > 20,
        "brave": lambda k: len(k) > 20,
        "deepseek": lambda k: len(k) > 20,
        "gemini": lambda k: len(k) > 20,
        "openrouter": lambda k: len(k) > 20,
        "qwen": lambda k: len(k) > 20,
        "grok": lambda k: len(k) > 20,
    }
    
    validator = validations.get(provider.lower())
    if validator:
        return validator(api_key)
    
    # Default validation
    return len(api_key) > 10


def store_user_api_key(session, user_id: int, provider: str, api_key: str) -> bool:
    """
    Store an encrypted API key for a user
    
    Args:
        session: Database session
        user_id: User's ID
        provider: Provider name
        api_key: Plain text API key
        
    Returns:
        True if stored successfully, False otherwise
    """
    from database.models import UserApiKey
    
    try:
        # Validate API key format
        if not validate_api_key_format(api_key, provider):
            return False
        
        # Encrypt the API key
        encrypted_key = encrypt_api_key(api_key)
        
        # Check if user already has a key for this provider
        existing_key = session.query(UserApiKey).filter_by(
            user_id=user_id,
            provider=provider
        ).first()
        
        if existing_key:
            # Update existing key
            existing_key.api_key_encrypted = encrypted_key
            existing_key.is_active = True
        else:
            # Create new key entry
            new_key = UserApiKey(
                user_id=user_id,
                provider=provider,
                api_key_encrypted=encrypted_key,
                is_active=True
            )
            session.add(new_key)
        
        session.commit()
        return True
    
    except Exception as e:
        print(f"Error storing API key: {e}")
        session.rollback()
        return False


def get_user_api_key(session, user_id: int, provider: str) -> Optional[str]:
    """
    Get a decrypted API key for a user
    
    Args:
        session: Database session
        user_id: User's ID
        provider: Provider name
        
    Returns:
        Decrypted API key or None if not found
    """
    from database.models import UserApiKey
    
    try:
        api_key_entry = session.query(UserApiKey).filter_by(
            user_id=user_id,
            provider=provider,
            is_active=True
        ).first()
        
        if not api_key_entry:
            return None
        
        return decrypt_api_key(api_key_entry.api_key_encrypted)
    
    except Exception as e:
        print(f"Error retrieving API key: {e}")
        return None


def delete_user_api_key(session, user_id: int, provider: str) -> bool:
    """
    Delete a user's API key for a provider
    
    Args:
        session: Database session
        user_id: User's ID
        provider: Provider name
        
    Returns:
        True if deleted successfully, False otherwise
    """
    from database.models import UserApiKey
    
    try:
        api_key_entry = session.query(UserApiKey).filter_by(
            user_id=user_id,
            provider=provider
        ).first()
        
        if api_key_entry:
            session.delete(api_key_entry)
            session.commit()
            return True
        
        return False
    
    except Exception as e:
        print(f"Error deleting API key: {e}")
        session.rollback()
        return False