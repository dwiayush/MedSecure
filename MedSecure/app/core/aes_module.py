"""
aes_module.py — AES Encryption/Decryption Core
================================================
Hybrid Encryption Flow:
  1. User data (image bytes or text) is encrypted with AES (CBC mode).
  2. A random IV (Initialization Vector) is generated per session.
  3. The AES key is either:
       a. Auto-generated securely using os.urandom()
       b. Derived from a user-provided passphrase via SHA-256 (PBKDF2-based approach)
  4. The AES key itself is secured via ECC key exchange (see ecc_module.py).

Key Handling:
  - Raw user keys are NEVER used directly.
  - All user keys pass through PBKDF2-HMAC-SHA256 with a random salt.
  - Key sizes: AES-128=16 bytes, AES-192=24 bytes, AES-256=32 bytes.
"""

import os
import hashlib
import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import struct


# ── Key Size Mapping ──────────────────────────────────────────────────────────
AES_KEY_SIZES = {
    "AES-128": 16,
    "AES-192": 24,
    "AES-256": 32,
}


def generate_aes_key(aes_type: str) -> bytes:
    """
    Auto-generate a cryptographically secure AES key.

    Args:
        aes_type: One of "AES-128", "AES-192", "AES-256"

    Returns:
        Raw key bytes of appropriate length.
    """
    key_size = AES_KEY_SIZES.get(aes_type, 32)
    return os.urandom(key_size)


def derive_key_from_passphrase(passphrase: str, aes_type: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Securely derive an AES key from a user-provided passphrase.

    Uses PBKDF2-HMAC-SHA256 — industry standard for key derivation.
    Never uses the raw passphrase as the key.

    Args:
        passphrase: User-entered key string.
        aes_type:   "AES-128", "AES-192", or "AES-256".
        salt:       Optional existing salt (for decryption). If None, generates new.

    Returns:
        (derived_key_bytes, salt_bytes)
    """
    key_size = AES_KEY_SIZES.get(aes_type, 32)
    if salt is None:
        salt = os.urandom(32)  # Fresh 256-bit salt for each encryption

    # PBKDF2-HMAC-SHA256: 310,000 iterations per OWASP 2023 recommendations
    derived_key = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=passphrase.encode("utf-8"),
        salt=salt,
        iterations=310_000,
        dklen=key_size,
    )
    return derived_key, salt


def validate_custom_key(passphrase: str, aes_type: str) -> tuple[bool, str]:
    """
    Validate that a user-provided passphrase meets minimum security requirements.

    Args:
        passphrase: The raw passphrase string.
        aes_type:   Target AES mode for context messaging.

    Returns:
        (is_valid: bool, message: str)
    """
    if not passphrase:
        return False, "Passphrase cannot be empty."
    if len(passphrase) < 8:
        return False, "Passphrase must be at least 8 characters."
    if len(passphrase) > 1024:
        return False, "Passphrase exceeds maximum allowed length (1024 chars)."
    return True, f"Key validated for {aes_type} derivation."


def encrypt_data(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
    """
    Encrypt arbitrary bytes using AES-CBC with PKCS7 padding.

    Args:
        plaintext: Raw data to encrypt (image bytes or encoded text).
        key:       AES key (16, 24, or 32 bytes).

    Returns:
        (ciphertext: bytes, iv: bytes)
    """
    iv = os.urandom(16)  # AES block size = 128 bits

    # PKCS7 padding to align plaintext to AES block boundaries
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    cipher = Cipher(
        algorithm=algorithms.AES(key),
        mode=modes.CBC(iv),
        backend=default_backend(),
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return ciphertext, iv


def decrypt_data(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Decrypt AES-CBC encrypted data and remove PKCS7 padding.

    Args:
        ciphertext: Encrypted bytes.
        key:        AES key used during encryption.
        iv:         Initialization vector used during encryption.

    Returns:
        Original plaintext bytes.

    Raises:
        ValueError: On decryption failure (wrong key / corrupted data).
    """
    try:
        cipher = Cipher(
            algorithm=algorithms.AES(key),
            mode=modes.CBC(iv),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext

    except Exception as e:
        raise ValueError(f"Decryption failed — likely wrong key or corrupted data: {e}")


def compute_sha256_checksum(data: bytes) -> bytes:
    """
    Compute SHA-256 hash for integrity verification.

    Embedded alongside encrypted payload so the receiver can
    verify data integrity before attempting decryption.

    Args:
        data: Bytes to hash.

    Returns:
        32-byte SHA-256 digest.
    """
    return hashlib.sha256(data).digest()


def verify_checksum(data: bytes, expected_checksum: bytes) -> bool:
    """
    Constant-time comparison of SHA-256 checksums to prevent timing attacks.

    Args:
        data:              Data to verify.
        expected_checksum: Known-good checksum (32 bytes).

    Returns:
        True if checksum matches, False otherwise.
    """
    actual = compute_sha256_checksum(data)
    return hmac.compare_digest(actual, expected_checksum)


def key_to_base64(key: bytes) -> str:
    """Encode a raw key to a displayable/storable Base64 string."""
    return base64.urlsafe_b64encode(key).decode("ascii")


def key_from_base64(b64_key: str) -> bytes:
    """Decode a Base64 string back to raw key bytes."""
    return base64.urlsafe_b64decode(b64_key.encode("ascii"))
