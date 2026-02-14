"""
API key encryption/decryption utilities using Fernet (symmetric encryption).
"""
import os
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


def get_encryption_key() -> bytes:
    """
    Get or generate encryption key for API keys.
    In production, store this in environment variable or secrets manager.
    """
    # Check environment first
    key_str = os.getenv("ENCRYPTION_KEY")
    
    if key_str:
        return key_str.encode()
    
    # For development, generate and warn
    logger.warning("No ENCRYPTION_KEY found in environment. Generating temporary key (data will not persist across restarts)")
    return Fernet.generate_key()


# Initialize cipher
_encryption_key = get_encryption_key()
_cipher = Fernet(_encryption_key)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage"""
    encrypted = _cipher.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from storage"""
    try:
        decrypted = _cipher.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Failed to decrypt API key: {e}")
        raise ValueError("Invalid or corrupted API key")


def mask_api_key(api_key: str, show_last: int = 4) -> str:
    """
    Mask an API key for logging/display.
    Example: sk-1234567890abcdef -> sk-***cdef
    """
    if len(api_key) <= show_last:
        return "*" * len(api_key)
    
    prefix = api_key.split("-")[0] if "-" in api_key else api_key[:2]
    suffix = api_key[-show_last:]
    return f"{prefix}-***{suffix}"
