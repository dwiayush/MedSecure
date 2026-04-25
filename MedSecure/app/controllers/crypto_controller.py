"""
crypto_controller.py — Hybrid Encryption Pipeline Orchestrator
==============================================================
Full Payload Structure (binary blob embedded in stego image):
┌────────────────────────────────────────────────────────────────────────────┐
│ FIELD               │ SIZE        │ DESCRIPTION                            │
├────────────────────────────────────────────────────────────────────────────┤
│ Magic Header        │ 8 bytes     │ b'MEDSEC01' — version marker           │
│ Mode Flag           │ 1 byte      │ 0x01=Image, 0x02=Text                  │
│ AES Type            │ 1 byte      │ 0=AES128, 1=AES192, 2=AES256           │
│ Key Mode            │ 1 byte      │ 0=AutoGen, 1=CustomKey                 │
│ ECC Public Key Len  │ 2 bytes     │ Length of ephemeral ECC public key DER  │
│ ECC Public Key      │ N bytes     │ Sender's ephemeral ECC public key (DER) │
│ HKDF Salt           │ 32 bytes    │ Salt used in HKDF key derivation        │
│ PBKDF2 Salt         │ 32 bytes    │ Salt for passphrase KDF (if custom key) │
│ Wrapped AES Key Len │ 2 bytes     │ Length of wrapped AES key               │
│ Wrapped AES Key     │ N bytes     │ AES key XOR'd with HKDF wrapping key   │
│ IV                  │ 16 bytes    │ AES CBC initialization vector           │
│ Checksum            │ 32 bytes    │ SHA-256 of plaintext (integrity check)  │
│ Ciphertext Len      │ 4 bytes     │ Length of encrypted payload             │
│ Ciphertext          │ N bytes     │ AES-CBC encrypted data                  │
└────────────────────────────────────────────────────────────────────────────┘
"""

import struct
import io
from typing import Callable

from app.core.aes_module import (
    generate_aes_key, derive_key_from_passphrase, encrypt_data,
    decrypt_data, compute_sha256_checksum, verify_checksum,
    validate_custom_key, AES_KEY_SIZES,
)
from app.core.ecc_module import (
    generate_ecc_key_pair, perform_ecdh, derive_wrapping_key,
    wrap_aes_key, unwrap_aes_key, serialize_public_key,
    deserialize_public_key,
)
from app.core.compression import compress_image, load_image_bytes
from app.core.steganography import embed_data, extract_data, compute_psnr


MAGIC_HEADER = b"MEDSEC01"
MODE_IMAGE = 0x01
MODE_TEXT  = 0x02
AES_TYPE_MAP = {"AES-128": 0, "AES-192": 1, "AES-256": 2}
AES_TYPE_RMAP = {0: "AES-128", 1: "AES-192", 2: "AES-256"}


# ─────────────────────────────────────────────────────────────────────────────
# SENDER SIDE
# ─────────────────────────────────────────────────────────────────────────────

def encrypt_and_embed_image(
    data_image_path: str,
    cover_image_path: str,
    output_stego_path: str,
    aes_type: str = "AES-256",
    use_custom_key: bool = False,
    passphrase: str = "",
    compress: bool = True,
    progress_cb: Callable[[int, str], None] = None,
) -> dict:
    """
    Full sender pipeline for IMAGE mode.

    Steps:
      1. Load & optionally compress the medical image.
      2. Generate/derive AES key.
      3. Generate ephemeral ECC key pair.
      4. Derive wrapping key via ECDH + HKDF.
      5. Wrap the AES key.
      6. Encrypt image bytes with AES-CBC.
      7. Assemble binary payload.
      8. Embed payload into cover image via LSB steganography.

    Returns dict with metadata (keys, sizes, PSNR, etc.)
    """
    def _progress(pct, msg):
        if progress_cb:
            progress_cb(pct, msg)

    _progress(5, "Loading medical image...")

    # Step 1: Load + compress
    if compress:
        raw_data = compress_image(data_image_path, lossless=True)
        _progress(15, f"Image compressed (lossless PNG).")
    else:
        raw_data = load_image_bytes(data_image_path)
        _progress(15, "Image loaded without compression.")

    return _run_encryption_pipeline(
        raw_data=raw_data,
        mode_flag=MODE_IMAGE,
        cover_image_path=cover_image_path,
        output_stego_path=output_stego_path,
        aes_type=aes_type,
        use_custom_key=use_custom_key,
        passphrase=passphrase,
        progress_cb=progress_cb,
    )


def encrypt_and_embed_text(
    text: str,
    cover_image_path: str,
    output_stego_path: str,
    aes_type: str = "AES-256",
    use_custom_key: bool = False,
    passphrase: str = "",
    progress_cb: Callable[[int, str], None] = None,
) -> dict:
    """
    Full sender pipeline for TEXT mode.

    Text is UTF-8 encoded before encryption.
    """
    def _progress(pct, msg):
        if progress_cb:
            progress_cb(pct, msg)

    _progress(5, "Encoding text to UTF-8...")
    raw_data = text.encode("utf-8")
    _progress(15, f"Text encoded: {len(raw_data)} bytes.")

    return _run_encryption_pipeline(
        raw_data=raw_data,
        mode_flag=MODE_TEXT,
        cover_image_path=cover_image_path,
        output_stego_path=output_stego_path,
        aes_type=aes_type,
        use_custom_key=use_custom_key,
        passphrase=passphrase,
        progress_cb=progress_cb,
    )


def _run_encryption_pipeline(
    raw_data: bytes,
    mode_flag: int,
    cover_image_path: str,
    output_stego_path: str,
    aes_type: str,
    use_custom_key: bool,
    passphrase: str,
    progress_cb: Callable,
) -> dict:
    """Internal shared encryption + embedding pipeline."""

    def _progress(pct, msg):
        if progress_cb:
            progress_cb(pct, msg)

    pbkdf2_salt = b"\x00" * 32  # Default empty salt for auto-key mode

    # Step 2: AES key generation / derivation
    _progress(20, "Generating AES key...")
    if use_custom_key:
        valid, msg = validate_custom_key(passphrase, aes_type)
        if not valid:
            raise ValueError(f"Key validation failed: {msg}")
        aes_key, pbkdf2_salt = derive_key_from_passphrase(passphrase, aes_type)
        _progress(28, f"[✔] Custom key derived via PBKDF2-HMAC-SHA256.")
    else:
        aes_key = generate_aes_key(aes_type)
        _progress(28, f"[✔] Auto-generated {aes_type} key ({len(aes_key)*8}-bit).")

    # Step 3: ECC ephemeral key pair
    _progress(32, "Generating ECC key pair (SECP384R1)...")
    sender_priv, sender_pub = generate_ecc_key_pair()
    receiver_priv, receiver_pub = generate_ecc_key_pair()  # Simulated receiver keypair
    _progress(40, "[✔] ECC key pair generated.")

    # Step 4: ECDH shared secret + HKDF wrapping key
    _progress(42, "Performing ECDH key agreement...")
    shared_secret = perform_ecdh(sender_priv, receiver_pub)
    import os
    hkdf_salt = os.urandom(32)
    wrapping_key = derive_wrapping_key(shared_secret, hkdf_salt)
    _progress(50, "[✔] ECDH shared secret established. HKDF wrapping key derived.")

    # Step 5: Wrap AES key
    _progress(52, "Wrapping AES key with ECC-derived wrapping key...")
    wrapped_aes_key = wrap_aes_key(aes_key, wrapping_key)
    _progress(57, "[✔] AES key wrapped.")

    # Step 6: AES encryption
    _progress(60, f"Encrypting data with {aes_type}-CBC...")
    checksum = compute_sha256_checksum(raw_data)
    ciphertext, iv = encrypt_data(raw_data, aes_key)
    _progress(72, f"[✔] {aes_type} encryption complete. Ciphertext: {len(ciphertext)} bytes.")

    # Step 7: Serialize ECC sender public key (receiver needs this for ECDH)
    sender_pub_der = serialize_public_key(sender_pub)
    receiver_priv_pem = None  # In real deployment, receiver holds their own private key

    # ── Assemble binary payload ───────────────────────────────────────────────
    _progress(75, "Assembling encrypted payload...")
    key_mode_byte = 0x01 if use_custom_key else 0x00
    aes_type_byte = AES_TYPE_MAP.get(aes_type, 2)
    ecc_pub_len = len(sender_pub_der)
    wrapped_len = len(wrapped_aes_key)
    ct_len = len(ciphertext)

    # Also store receiver private key DER so they can decrypt (demo mode)
    # In production: receiver has their own key stored securely
    from app.core.ecc_module import serialize_private_key
    receiver_priv_der = serialize_private_key(receiver_priv)
    recv_priv_len = len(receiver_priv_der)

    payload = struct.pack(
        f">8sBBBH{ecc_pub_len}s32s32sH{wrapped_len}s16s32sI{ct_len}sI{recv_priv_len}s",
        MAGIC_HEADER,          # 8 bytes
        mode_flag,             # 1 byte
        aes_type_byte,         # 1 byte
        key_mode_byte,         # 1 byte
        ecc_pub_len,           # 2 bytes
        sender_pub_der,        # N bytes
        hkdf_salt,             # 32 bytes
        pbkdf2_salt,           # 32 bytes
        wrapped_len,           # 2 bytes
        wrapped_aes_key,       # N bytes
        iv,                    # 16 bytes
        checksum,              # 32 bytes
        ct_len,                # 4 bytes
        ciphertext,            # N bytes
        recv_priv_len,         # 4 bytes — receiver private key (demo)
        receiver_priv_der,     # N bytes
    )
    _progress(80, f"[✔] Payload assembled: {len(payload)} bytes.")

    # Step 8: LSB steganography
    _progress(83, "Embedding payload into cover image (LSB steganography)...")
    embed_result = embed_data(cover_image_path, payload, output_stego_path)
    _progress(95, f"[✔] Data embedded. Cover utilization: {embed_result['utilization_pct']}%")

    # PSNR quality metric
    psnr = compute_psnr(cover_image_path, embed_result["output_path"])
    _progress(100, f"[✔] Stego image saved. PSNR: {psnr} dB")

    return {
        "status": "success",
        "mode": "Image" if mode_flag == MODE_IMAGE else "Text",
        "aes_type": aes_type,
        "key_mode": "Custom (PBKDF2-derived)" if use_custom_key else "Auto-generated",
        "plaintext_size": len(raw_data),
        "ciphertext_size": len(ciphertext),
        "payload_size": len(payload),
        "cover_capacity": embed_result["capacity_bytes"],
        "utilization_pct": embed_result["utilization_pct"],
        "cover_dimensions": embed_result["cover_dimensions"],
        "psnr_db": psnr,
        "stego_path": embed_result["output_path"],
        "aes_key_b64": __import__("base64").urlsafe_b64encode(aes_key).decode(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# RECEIVER SIDE
# ─────────────────────────────────────────────────────────────────────────────

def extract_and_decrypt(
    stego_image_path: str,
    output_path: str = None,
    passphrase: str = "",
    progress_cb: Callable[[int, str], None] = None,
) -> dict:
    """
    Full receiver pipeline: extract hidden payload, decrypt, and recover data.

    Args:
        stego_image_path: Path to the stego image.
        output_path:      Where to save recovered image (if image mode).
        passphrase:       User passphrase if custom key was used.
        progress_cb:      UI progress callback.

    Returns:
        Dictionary with: mode, decrypted data, text (if text mode), paths, etc.
    """
    def _progress(pct, msg):
        if progress_cb:
            progress_cb(pct, msg)

    _progress(5, "Loading stego image...")

    # Step 1: Extract raw payload from LSB
    _progress(10, "Extracting hidden payload from LSB channels...")
    try:
        payload = extract_data(stego_image_path)
    except Exception as e:
        raise ValueError(f"Extraction failed: {e}")
    _progress(30, f"[✔] Payload extracted: {len(payload)} bytes.")

    # Step 2: Parse payload structure
    _progress(35, "Parsing payload structure...")
    try:
        parsed = _parse_payload(payload)
    except Exception as e:
        raise ValueError(f"Payload parsing failed — image may not be a valid MedSecure stego image: {e}")
    _progress(45, "[✔] Payload structure validated.")

    # Step 3: Reconstruct wrapping key via ECDH
    _progress(50, "Reconstructing ECC shared secret...")
    try:
        sender_pub = deserialize_public_key(parsed["sender_pub_der"])
        from app.core.ecc_module import deserialize_private_key
        receiver_priv = deserialize_private_key(parsed["receiver_priv_der"])
        shared_secret = perform_ecdh(receiver_priv, sender_pub)
        wrapping_key = derive_wrapping_key(shared_secret, parsed["hkdf_salt"])
    except Exception as e:
        raise ValueError(f"ECC key reconstruction failed: {e}")
    _progress(60, "[✔] ECC shared secret reconstructed.")

    # Step 4: Unwrap AES key
    _progress(62, "Unwrapping AES session key...")
    aes_key_raw = unwrap_aes_key(parsed["wrapped_aes_key"], wrapping_key)

    # If custom key was used, re-derive and verify
    if parsed["key_mode"] == "custom":
        if not passphrase:
            raise ValueError("This payload was encrypted with a custom key. Please provide the passphrase.")
        _progress(65, "Deriving AES key from passphrase...")
        aes_key_raw, _ = derive_key_from_passphrase(
            passphrase, parsed["aes_type"], salt=parsed["pbkdf2_salt"]
        )
        _progress(68, "[✔] Custom key re-derived from passphrase.")
    else:
        _progress(68, "[✔] AES session key unwrapped.")

    # Step 5: AES decryption
    _progress(72, f"Decrypting with {parsed['aes_type']}-CBC...")
    try:
        plaintext = decrypt_data(parsed["ciphertext"], aes_key_raw, parsed["iv"])
    except ValueError as e:
        raise ValueError(f"Decryption failed — wrong key or corrupted data: {e}")
    _progress(85, f"[✔] {parsed['aes_type']} decryption complete.")

    # Step 6: Integrity verification
    _progress(88, "Verifying SHA-256 integrity checksum...")
    if not verify_checksum(plaintext, parsed["checksum"]):
        raise ValueError(
            "Integrity check FAILED — data may have been tampered with or key is incorrect."
        )
    _progress(92, "[✔] Integrity checksum verified.")

    # Step 7: Return result based on mode
    result = {
        "status": "success",
        "mode": parsed["mode"],
        "aes_type": parsed["aes_type"],
        "key_mode": parsed["key_mode"],
        "plaintext_size": len(plaintext),
    }

    if parsed["mode"] == "Text":
        _progress(98, "Decoding recovered text...")
        try:
            recovered_text = plaintext.decode("utf-8")
        except UnicodeDecodeError:
            recovered_text = plaintext.decode("latin-1")
        result["text"] = recovered_text
        _progress(100, "[✔] Text successfully recovered and decrypted.")

    else:  # Image mode
        _progress(95, "Saving recovered image...")
        if output_path:
            # Try to detect format from bytes magic
            if plaintext[:8] == b"\x89PNG\r\n\x1a\n":
                ext = ".png"
            elif plaintext[:2] == b"\xff\xd8":
                ext = ".jpg"
            else:
                ext = ".png"
            if not output_path.endswith(ext):
                output_path = output_path.rsplit(".", 1)[0] + ext
            with open(output_path, "wb") as f:
                f.write(plaintext)
            result["recovered_image_path"] = output_path
        result["image_bytes"] = plaintext
        _progress(100, "[✔] Medical image successfully recovered and decrypted.")

    return result


def _parse_payload(payload: bytes) -> dict:
    """
    Parse the binary payload structure assembled during encryption.

    Args:
        payload: Raw extracted payload bytes.

    Returns:
        Dictionary of parsed fields.

    Raises:
        ValueError: On malformed payload.
    """
    offset = 0

    def read(n):
        nonlocal offset
        data = payload[offset:offset + n]
        if len(data) < n:
            raise ValueError(f"Payload truncated at offset {offset} (need {n}, got {len(data)}).")
        offset += n
        return data

    magic = read(8)
    if magic != MAGIC_HEADER:
        raise ValueError(f"Invalid magic header: {magic!r}. Not a MedSecure payload.")

    mode_byte = struct.unpack(">B", read(1))[0]
    aes_type_byte = struct.unpack(">B", read(1))[0]
    key_mode_byte = struct.unpack(">B", read(1))[0]

    ecc_pub_len = struct.unpack(">H", read(2))[0]
    sender_pub_der = read(ecc_pub_len)
    hkdf_salt = read(32)
    pbkdf2_salt = read(32)

    wrapped_len = struct.unpack(">H", read(2))[0]
    wrapped_aes_key = read(wrapped_len)

    iv = read(16)
    checksum = read(32)

    ct_len = struct.unpack(">I", read(4))[0]
    ciphertext = read(ct_len)

    recv_priv_len = struct.unpack(">I", read(4))[0]
    receiver_priv_der = read(recv_priv_len)

    mode_str = "Image" if mode_byte == MODE_IMAGE else "Text"
    aes_type_str = AES_TYPE_RMAP.get(aes_type_byte, "AES-256")
    key_mode_str = "custom" if key_mode_byte == 0x01 else "auto"

    return {
        "mode": mode_str,
        "aes_type": aes_type_str,
        "key_mode": key_mode_str,
        "sender_pub_der": sender_pub_der,
        "hkdf_salt": hkdf_salt,
        "pbkdf2_salt": pbkdf2_salt,
        "wrapped_aes_key": wrapped_aes_key,
        "iv": iv,
        "checksum": checksum,
        "ciphertext": ciphertext,
        "receiver_priv_der": receiver_priv_der,
    }
