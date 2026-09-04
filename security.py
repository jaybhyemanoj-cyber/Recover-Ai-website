"""
Healthnest Security & Cryptography Module
------------------------------------------
- HMAC-SHA256 (PBKDF2 with 100,000 iterations) for Password Hashing & Authentication
- Hybrid Cryptography (AES-256 + RSA-2048) for Patient Data Encryption & Decryption
"""

import os
import hmac
import hashlib
import base64
import logging
from typing import Dict, Tuple, Optional, Any
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

logger = logging.getLogger("healthnest.security")

# Secret key for HMAC computation
HMAC_SECRET_KEY = os.getenv("HMAC_SECRET_KEY", "healthnest-super-secret-hmac-key-2026").encode('utf-8')

# Persistent RSA Key Pair for Hybrid Cryptography (Generated in-memory for session)
RSA_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
RSA_PUBLIC_KEY = RSA_PRIVATE_KEY.public_key()


# ==============================================================================
# 1. HMAC PASSWORD HASHING & AUTHENTICATION (PBKDF2-HMAC-SHA256)
# ==============================================================================

def hash_password_hmac(password: str) -> str:
    """
    Hash a user password using HMAC-SHA256 with PBKDF2 (100,000 iterations) & 16-byte random salt.
    Returns format: pbkdf2_hmac_sha256$<salt_b64>$<hash_b64>
    """
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),
        salt=salt + HMAC_SECRET_KEY,
        iterations=100000
    )
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    key_b64 = base64.b64encode(derived_key).decode('utf-8')
    return f"pbkdf2_hmac_sha256${salt_b64}${key_b64}"


def verify_password_hmac(password: str, stored_hash: str) -> bool:
    """
    Verify user input password against stored HMAC-PBKDF2 hash using constant-time comparison.
    """
    try:
        parts = stored_hash.split('$')
        if len(parts) != 3 or parts[0] != "pbkdf2_hmac_sha256":
            return False
        
        salt = base64.b64decode(parts[1])
        original_key = base64.b64decode(parts[2])
        
        derived_key = hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=password.encode('utf-8'),
            salt=salt + HMAC_SECRET_KEY,
            iterations=100000
        )
        return hmac.compare_digest(original_key, derived_key)
    except Exception as e:
        logger.error(f"HMAC password verification failed: {e}")
        return False


# ==============================================================================
# 2. HYBRID ENCRYPTION MODEL (AES-256 + RSA-2048) FOR PATIENT DATA
# ==============================================================================

def hybrid_encrypt_patient_data(plain_text: str) -> Dict[str, str]:
    """
    Encrypt sensitive patient data using Hybrid Cryptography:
    - Step 1: Encrypt plain text using a fresh random AES-256 (Fernet) key.
    - Step 2: Encrypt the AES key using RSA-2048 Public Key.
    Returns dict containing 'encrypted_data' and 'encrypted_key' (Base64 strings).
    """
    if not plain_text:
        return {"encrypted_data": "", "encrypted_key": ""}
    
    try:
        # Step 1: Generate fresh AES key & encrypt payload
        aes_key = Fernet.generate_key()
        fernet = Fernet(aes_key)
        encrypted_payload = fernet.encrypt(plain_text.encode('utf-8'))
        
        # Step 2: Encrypt AES key using RSA Public Key
        encrypted_aes_key = RSA_PUBLIC_KEY.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            "encrypted_data": base64.b64encode(encrypted_payload).decode('utf-8'),
            "encrypted_key": base64.b64encode(encrypted_aes_key).decode('utf-8')
        }
    except Exception as e:
        logger.error(f"Hybrid Encryption error: {e}")
        return {"encrypted_data": plain_text, "encrypted_key": ""}


def hybrid_decrypt_patient_data(encrypted_data_b64: str, encrypted_key_b64: str) -> str:
    """
    Decrypt sensitive patient data using RSA Private Key & AES Key.
    """
    if not encrypted_data_b64 or not encrypted_key_b64:
        return encrypted_data_b64 or ""
    
    try:
        encrypted_payload = base64.b64decode(encrypted_data_b64)
        encrypted_aes_key = base64.b64decode(encrypted_key_b64)
        
        # Step 1: Decrypt AES key using RSA Private Key
        aes_key = RSA_PRIVATE_KEY.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Step 2: Decrypt payload using AES key
        fernet = Fernet(aes_key)
        return fernet.decrypt(encrypted_payload).decode('utf-8')
    except Exception as e:
        # Fallback if text was not encrypted or legacy plain text
        return encrypted_data_b64


# ==============================================================================
# 3. GOOGLE RECAPTCHA V3 BOT DEFENSE
# ==============================================================================

def verify_recaptcha_v3(token: str, action: str = "submit", threshold: float = 0.5) -> Dict[str, Any]:
    """
    Verifies Google reCAPTCHA v3 token against Google verification API.
    Returns dict with 'valid' (bool), 'score' (float), and 'message' (str).
    """
    import requests
    
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY", "").strip()
    use_recaptcha = os.getenv("USE_RECAPTCHA", "True").lower() in ("true", "1", "yes")
    
    if not use_recaptcha or not secret_key:
        return {"valid": True, "score": 1.0, "message": "reCAPTCHA disabled or unconfigured"}

    if not token:
        # Development fallback when token is not provided in local dev
        logger.info("reCAPTCHA token missing in request body, using dev mode allowance.")
        return {"valid": True, "score": 0.9, "message": "Dev mode fallback allowed"}

    try:
        url = "https://www.google.com/recaptcha/api/siteverify"
        response = requests.post(
            url,
            data={"secret": secret_key, "response": token},
            timeout=4
        )
        result = response.json()
        success = result.get("success", False)
        score = float(result.get("score", 0.0))
        
        is_valid = success and (score >= threshold)
        msg = f"reCAPTCHA Verified (Score: {score})" if is_valid else f"Bot activity detected (Score: {score})"
        
        return {
            "valid": is_valid,
            "score": score,
            "success": success,
            "message": msg
        }
    except Exception as e:
        logger.warning(f"Google reCAPTCHA verification request error: {e}")
        return {"valid": True, "score": 1.0, "message": f"Connection error fallback: {e}"}


# ==============================================================================
# 4. GOOGLE OAUTH 2.0 TOKEN VERIFICATION
# ==============================================================================

def verify_google_oauth_token(id_token_jwt: str) -> Dict[str, Any]:
    """
    Verifies Google OAuth 2.0 JWT ID token using google-auth library.
    Extracts verified user profile data (email, name, picture, user_id).
    """
    if not id_token_jwt:
        return {"valid": False, "message": "Missing Google ID Token"}
        
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    
    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
        
        # Verify OAuth token against Google servers
        id_info = google_id_token.verify_oauth2_token(
            id_token_jwt,
            google_requests.Request(),
            client_id if client_id else None
        )

        return {
            "valid": True,
            "user_id": id_info.get("sub"),
            "email": id_info.get("email"),
            "name": id_info.get("name"),
            "picture": id_info.get("picture"),
            "email_verified": id_info.get("email_verified", False),
            "message": "Google Authentication Successful"
        }
    except Exception as e:
        logger.error(f"Google OAuth Token verification error: {e}")
        return {"valid": False, "message": f"Invalid Google Token: {e}"}

if __name__ == "__main__":
    print("Testing Security Module...")
    # Test HMAC Password
    pw = "CaregiverPass2026"
    pw_hash = hash_password_hmac(pw)
    is_valid = verify_password_hmac(pw, pw_hash)
    print(f"HMAC Password Test: {is_valid} | Hash: {pw_hash[:45]}...")

    # Test Hybrid Encryption
    data = "Patient Rahul Sharma: Critical Fall Incident at Bedroom Doorway"
    enc = hybrid_encrypt_patient_data(data)
    dec = hybrid_decrypt_patient_data(enc["encrypted_data"], enc["encrypted_key"])
    print(f"Hybrid Encrypt Test: Match={data == dec}")
    print(f"Encrypted Data Payload: {enc['encrypted_data'][:45]}...")
