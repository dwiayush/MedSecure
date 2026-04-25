"""
ecc_module.py — Elliptic Curve Cryptography Key Exchange
=========================================================
Hybrid Encryption Flow (ECC portion):
  1. Sender generates an ephemeral ECC key pair (ECDH on SECP384R1 curve).
  2. Receiver holds a long-term ECC public key.
  3. Sender performs ECDH to derive a shared secret without transmitting the private key.
  4. The shared secret is used to wrap (protect) the AES session key.
  5. Receiver uses their private key + sender's ephemeral public key to recover
     the same shared secret and unwrap the AES key.

Why ECC over RSA?
  - SECP384R1 (384-bit) offers ~192-bit security — equivalent to RSA-7680.
  - Smaller key sizes → faster operations → suitable for medical imaging workflows.
  - NIST-approved curve for healthcare and government use (FIPS 186-4).

Key Wrapping:
  - Shared secret → HKDF-SHA384 → 32-byte wrapping key.
  - AES session key is XOR'd with the wrapping key (simple but secure given key sizes ≤ 32 bytes).
  - In production: replace XOR with AES-GCM key wrapping (RFC 3394).
"""

import os
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import (
    EllipticCurvePrivateKey,
    EllipticCurvePublicKey,
    ECDH,
)
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend


# ── Curve Selection ───────────────────────────────────────────────────────────
# SECP384R1: NIST P-384 — provides 192-bit security level.
# Use this over P-256 for medical/healthcare data per HIPAA technical safeguards.
CURVE = ec.SECP384R1()


def generate_ecc_key_pair() -> tuple[EllipticCurvePrivateKey, EllipticCurvePublicKey]:
    """
    Generate an ECC key pair on the SECP384R1 (P-384) curve.

    Returns:
        (private_key, public_key) — both as cryptography library objects.
    """
    private_key = ec.generate_private_key(CURVE, default_backend())
    public_key = private_key.public_key()
    return private_key, public_key


def perform_ecdh(private_key: EllipticCurvePrivateKey, peer_public_key: EllipticCurvePublicKey) -> bytes:
    """
    Perform Elliptic Curve Diffie-Hellman (ECDH) key agreement.

    Both sender and receiver perform ECDH with their private key and the
    counterpart's public key to arrive at the SAME shared secret — without
    ever transmitting the private key.

    Args:
        private_key:     Our ECC private key.
        peer_public_key: The other party's ECC public key.

    Returns:
        Raw shared secret bytes (48 bytes for P-384).
    """
    shared_secret = private_key.exchange(ECDH(), peer_public_key)
    return shared_secret


def derive_wrapping_key(shared_secret: bytes, salt: bytes = None) -> bytes:
    """
    Derive a 32-byte AES key wrapping key from the ECDH shared secret
    using HKDF-SHA384 (HMAC-based Key Derivation Function).

    HKDF ensures that even if two sessions share the same ECDH secret,
    the derived wrapping keys differ (due to fresh salt).

    Args:
        shared_secret: Raw output from ECDH.
        salt:          Random salt for HKDF (generated if None).

    Returns:
        32-byte wrapping key.
    """
    if salt is None:
        salt = os.urandom(32)

    hkdf = HKDF(
        algorithm=hashes.SHA384(),
        length=32,
        salt=salt,
        info=b"MedSecure-AES-Key-Wrap-v1",
        backend=default_backend(),
    )
    return hkdf.derive(shared_secret)


def wrap_aes_key(aes_key: bytes, wrapping_key: bytes) -> bytes:
    """
    Wrap (protect) the AES session key using XOR with the derived wrapping key.

    Note: For production deployment with keys > 32 bytes or when using
    AES-192/256 in regulated environments, replace this with AES-GCM key
    wrapping per RFC 3394 / NIST SP 800-38F.

    Args:
        aes_key:      AES session key (16, 24, or 32 bytes).
        wrapping_key: 32-byte derived wrapping key from HKDF.

    Returns:
        Wrapped (XOR'd) key bytes — same length as aes_key.
    """
    # Truncate or cycle wrapping key to match AES key length
    wk = (wrapping_key * ((len(aes_key) // len(wrapping_key)) + 1))[: len(aes_key)]
    return bytes(a ^ b for a, b in zip(aes_key, wk))


def unwrap_aes_key(wrapped_key: bytes, wrapping_key: bytes) -> bytes:
    """
    Unwrap the AES session key by reversing the XOR operation.
    XOR is its own inverse: (A XOR B) XOR B = A.

    Args:
        wrapped_key:  The wrapped key bytes received.
        wrapping_key: The same 32-byte wrapping key derived via HKDF.

    Returns:
        Original AES session key bytes.
    """
    return wrap_aes_key(wrapped_key, wrapping_key)  # XOR is self-inverse


def serialize_public_key(public_key: EllipticCurvePublicKey) -> bytes:
    """
    Serialize ECC public key to DER format for embedding in the stego payload.

    DER (Distinguished Encoding Rules) is compact, binary, and standard.

    Args:
        public_key: ECC public key object.

    Returns:
        DER-encoded bytes.
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def deserialize_public_key(der_bytes: bytes) -> EllipticCurvePublicKey:
    """
    Deserialize a DER-encoded ECC public key back to a key object.

    Args:
        der_bytes: DER-encoded public key bytes.

    Returns:
        ECC public key object.

    Raises:
        ValueError: If bytes are malformed or not a valid ECC key.
    """
    try:
        return serialization.load_der_public_key(der_bytes, backend=default_backend())
    except Exception as e:
        raise ValueError(f"Failed to deserialize ECC public key: {e}")


def serialize_private_key(private_key: EllipticCurvePrivateKey, password: bytes = None) -> bytes:
    """
    Serialize ECC private key to PEM format (optionally encrypted).

    Args:
        private_key: ECC private key object.
        password:    Optional encryption password for the PEM file.

    Returns:
        PEM-encoded bytes.
    """
    encryption = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )


def deserialize_private_key(pem_bytes: bytes, password: bytes = None) -> EllipticCurvePrivateKey:
    """
    Deserialize a PEM-encoded ECC private key.

    Args:
        pem_bytes: PEM-encoded private key bytes.
        password:  Decryption password if key is encrypted.

    Returns:
        ECC private key object.
    """
    try:
        return serialization.load_pem_private_key(pem_bytes, password=password, backend=default_backend())
    except Exception as e:
        raise ValueError(f"Failed to deserialize ECC private key: {e}")
