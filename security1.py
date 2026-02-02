import os
import base64
import secrets
import string
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

def derive_key(password: str, salt: bytes) -> bytes:
    """Deriva una chiave di crittografia dalla password e dal salt"""
    kdf = PBKDF2HMAC(hashes.SHA256(), 32, salt, 480000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def hash_master_password(password: str) -> bytes:
    """Crea un hash sicuro della master password per la verifica"""
    salt = os.urandom(32)
    kdf = PBKDF2HMAC(hashes.SHA256(), 64, salt, 480000)
    hash_bytes = kdf.derive(password.encode())
    # Salviamo salt + hash insieme
    return salt + hash_bytes

def verify_master_password(password: str, stored_hash: bytes) -> bool:
    """Verifica se la password corrisponde all'hash salvato"""
    salt = stored_hash[:32]  # Primi 32 bytes sono il salt
    stored_key = stored_hash[32:]  # Resto è l'hash
    
    kdf = PBKDF2HMAC(hashes.SHA256(), 64, salt, 480000)
    try:
        computed_key = kdf.derive(password.encode())
        return computed_key == stored_key
    except:
        return False

def encrypt_password(password: str, key: bytes) -> bytes:
    """Cripta una password usando la chiave derivata"""
    fernet = Fernet(key)
    return fernet.encrypt(password.encode())

def decrypt_password(encrypted_password: bytes, key: bytes) -> str:
    """Decripta una password usando la chiave derivata"""
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password).decode()

def generate_strong_password(length: int = 16) -> str:
    """Genera una password casuale forte"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))