"""
Authentication package for DeepCode
"""

from .authentication import (
    hash_password, verify_password, generate_totp_secret, generate_totp_qr_code,
    verify_totp, authenticate_user, register_user, setup_user_totp,
    check_authentication, require_authentication, require_admin, require_super_admin,
    logout
)
from .encryption import (
    encrypt_api_key, decrypt_api_key, mask_api_key, validate_api_key_format,
    store_user_api_key, get_user_api_key, delete_user_api_key
)

__all__ = [
    'hash_password', 'verify_password', 'generate_totp_secret', 'generate_totp_qr_code',
    'verify_totp', 'authenticate_user', 'register_user', 'setup_user_totp',
    'check_authentication', 'require_authentication', 'require_admin', 'require_super_admin',
    'logout', 'encrypt_api_key', 'decrypt_api_key', 'mask_api_key', 'validate_api_key_format',
    'store_user_api_key', 'get_user_api_key', 'delete_user_api_key'
]