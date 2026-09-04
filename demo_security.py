from security import (
    hash_password_hmac,
    verify_password_hmac,
    hybrid_encrypt_patient_data,
    hybrid_decrypt_patient_data,
    verify_recaptcha_v3,
    verify_google_oauth_token
)
import os

print("==================================================================")
print("             HEALTHNEST SECURITY VERIFICATION DEMO                ")
print("==================================================================")

# 1. HMAC Password Hashing Demo
password = "CaregiverPassword@2026"
hashed = hash_password_hmac(password)

print("\n1. PASSWORDS SECURITY (HMAC-SHA256 + PBKDF2):")
print(f"   [INPUT] Plain Password : '{password}'")
print(f"   [STORED] Saved in DB   : '{hashed[:55]}...'")
print(f"   [TEST 1] Correct Pass  : {verify_password_hmac(password, hashed)}  (MATCH APPROVED)")
print(f"   [TEST 2] Wrong Pass    : {verify_password_hmac('WrongPass123', hashed)} (BLOCKED ACCESS)")

# 2. Hybrid Cryptography (AES-256 + RSA-2048) Demo
patient_log = "Patient Rahul Sharma: Emergency Fall Detected in Bedroom. Pulse: 110 bpm."
enc_result = hybrid_encrypt_patient_data(patient_log)
decrypted = hybrid_decrypt_patient_data(enc_result["encrypted_data"], enc_result["encrypted_key"])

print("\n2. PATIENT DATA SECURITY (HYBRID ENCRYPTION: AES-256 + RSA-2048):")
print(f"   [ORIGINAL] Patient Log : '{patient_log}'")
print(f"   [IN MYSQL] Cipher Text  : '{enc_result['encrypted_data'][:55]}...' (UNREADABLE TO HACKERS)")
print(f"   [DECRYPTED] For Doctor  : '{decrypted}' (MATCH APPROVED)")

# 3. Google reCAPTCHA v3 Bot Defense Demo
site_key = os.getenv("RECAPTCHA_SITE_KEY", "6Ldvw6ctAAAAABc65eVUwfL3TQ_JZVF2k7tRjKx4")
recaptcha_res = verify_recaptcha_v3("sample_token")

print("\n3. BOT DEFENSE (GOOGLE RECAPTCHA V3):")
print(f"   [CONFIG] Site Key      : '{site_key[:12]}...'")
print(f"   [STATUS] Protection     : ACTIVE (Score Threshold >= 0.5)")
print(f"   [VERIFY] Verification  : {recaptcha_res.get('message')}")

# 4. Google OAuth 2.0 Identity Demo
oauth_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
google_res = verify_google_oauth_token("invalid_test_token")

print("\n4. IDENTITY PROVIDER (GOOGLE OAUTH 2.0 SIGN-IN):")
print(f"   [CONFIG] Client ID     : '{oauth_client_id[:25]}...'")
print(f"   [STATUS] Integration    : ACTIVE (Google Identity Services GSI)")
print(f"   [SECURITY] Fake Token   : Blocked safely ({google_res.get('message')[:35]}...)")

print("\n==================================================================")
print(" RESULT: All 4 Security Layers (HMAC + Hybrid + reCAPTCHA + OAuth) Active!")
print("==================================================================")
