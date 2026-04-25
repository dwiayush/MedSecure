"""
steganography.py — Adaptive LSB Steganography Engine
=====================================================
Steganography Process:
  1. Cover image is loaded and converted to RGB.
  2. A structured binary payload is assembled:
       [4 bytes: payload length] + [payload bytes]
  3. Each byte of the payload is split into 8 bits.
  4. Each bit is embedded into the Least Significant Bit (LSB)
     of successive pixel channel values (R, G, B order).
  5. The modification is imperceptible to the human eye since
     changing the LSB of a pixel value changes it by at most 1
     (e.g., 200 → 201 or 200 → 199).

Adaptive LSB:
  - Checks available capacity before embedding.
  - Reports capacity vs payload size.
  - Uses 1-bit LSB (minimal distortion) by default.
  - Could extend to 2-bit LSB for larger payloads.

Payload Structure embedded in stego image:
  ┌─────────────────────────────────────────────────────────┐
  │ 4 bytes  │ N bytes                                      │
  │ Length   │ Encrypted Payload (from crypto_controller)   │
  └─────────────────────────────────────────────────────────┘
"""

import struct
import numpy as np
from PIL import Image
import io


def embed_data(cover_image_path: str, payload: bytes, output_path: str) -> dict:
    """
    Embed binary payload into a cover image using LSB steganography.

    Args:
        cover_image_path: Path to the carrier/cover image.
        payload:          Binary data to hide (encrypted blob).
        output_path:      Path to save the resulting stego image (PNG recommended).

    Returns:
        Dictionary with: capacity_bytes, payload_bytes, utilization_pct, output_path.

    Raises:
        ValueError: If payload exceeds image capacity.
        FileNotFoundError: If cover image not found.
    """
    # ── Load cover image ──────────────────────────────────────────────────────
    try:
        img = Image.open(cover_image_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError(f"Cover image not found: {cover_image_path}")
    except Exception as e:
        raise ValueError(f"Cannot open cover image: {e}")

    pixels = np.array(img, dtype=np.uint8)
    total_pixels = pixels.shape[0] * pixels.shape[1]
    capacity_bytes = (total_pixels * 3) // 8 - 4  # 3 channels, 1 bit each, minus header

    # ── Capacity check ────────────────────────────────────────────────────────
    payload_len = len(payload)
    if payload_len > capacity_bytes:
        raise ValueError(
            f"Payload too large: {payload_len} bytes required, "
            f"but cover image only supports {capacity_bytes} bytes. "
            f"Use a larger cover image."
        )

    # ── Build full binary stream: 4-byte length header + payload ─────────────
    length_header = struct.pack(">I", payload_len)  # Big-endian unsigned int
    full_data = length_header + payload

    # ── Convert data to bit array ─────────────────────────────────────────────
    bits = []
    for byte in full_data:
        for bit_pos in range(7, -1, -1):  # MSB first
            bits.append((byte >> bit_pos) & 1)

    # ── Flatten pixel array: shape (H, W, 3) → (H*W*3,) ─────────────────────
    flat = pixels.flatten()

    # ── Embed bits into LSBs ──────────────────────────────────────────────────
    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | bit  # Clear LSB, set to our bit

    # ── Reshape and save as PNG (lossless — JPEG would destroy LSB data) ──────
    stego_pixels = flat.reshape(pixels.shape)
    stego_img = Image.fromarray(stego_pixels, "RGB")

    # Always save as PNG to preserve exact pixel values
    if not output_path.lower().endswith(".png"):
        output_path = output_path.rsplit(".", 1)[0] + ".png"

    stego_img.save(output_path, format="PNG", optimize=False)

    utilization = (payload_len / capacity_bytes) * 100 if capacity_bytes > 0 else 0

    return {
        "capacity_bytes": capacity_bytes,
        "payload_bytes": payload_len,
        "utilization_pct": round(utilization, 2),
        "output_path": output_path,
        "cover_dimensions": f"{img.width}×{img.height}",
    }


def embed_data_from_bytes(cover_bytes: bytes, payload: bytes) -> bytes:
    """
    Embed payload into a cover image provided as bytes (in-memory).

    Args:
        cover_bytes: Raw bytes of the cover image.
        payload:     Binary payload to hide.

    Returns:
        PNG stego image as bytes.
    """
    buf_in = io.BytesIO(cover_bytes)
    img = Image.open(buf_in).convert("RGB")
    pixels = np.array(img, dtype=np.uint8)

    total_pixels = pixels.shape[0] * pixels.shape[1]
    capacity_bytes = (total_pixels * 3) // 8 - 4

    if len(payload) > capacity_bytes:
        raise ValueError(
            f"Payload ({len(payload)} bytes) exceeds image capacity ({capacity_bytes} bytes)."
        )

    length_header = struct.pack(">I", len(payload))
    full_data = length_header + payload

    bits = []
    for byte in full_data:
        for bit_pos in range(7, -1, -1):
            bits.append((byte >> bit_pos) & 1)

    flat = pixels.flatten()
    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | bit

    stego_pixels = flat.reshape(pixels.shape)
    stego_img = Image.fromarray(stego_pixels, "RGB")

    buf_out = io.BytesIO()
    stego_img.save(buf_out, format="PNG", optimize=False)
    return buf_out.getvalue()


def extract_data(stego_image_path: str) -> bytes:
    """
    Extract hidden payload from a stego image.

    Process:
      1. Read LSBs from pixel channels in the same order used during embedding.
      2. First 32 bits (4 bytes) → payload length.
      3. Read exactly that many bytes of payload.

    Args:
        stego_image_path: Path to the stego image (must be lossless PNG).

    Returns:
        Extracted payload bytes.

    Raises:
        ValueError: If image contains no valid hidden data or is corrupted.
    """
    try:
        img = Image.open(stego_image_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError(f"Stego image not found: {stego_image_path}")
    except Exception as e:
        raise ValueError(f"Cannot open stego image: {e}")

    pixels = np.array(img, dtype=np.uint8)
    flat = pixels.flatten()

    # ── Extract first 32 bits to get payload length ───────────────────────────
    if len(flat) < 32:
        raise ValueError("Image is too small to contain any hidden data.")

    length_bits = [int(flat[i] & 1) for i in range(32)]
    payload_length = 0
    for bit in length_bits:
        payload_length = (payload_length << 1) | bit

    # ── Sanity check on declared length ──────────────────────────────────────
    max_possible = (len(flat) // 8) - 4
    if payload_length <= 0 or payload_length > max_possible:
        raise ValueError(
            f"Invalid payload length detected ({payload_length} bytes). "
            "This image may not contain hidden data or may be corrupted."
        )

    # ── Extract payload bits ──────────────────────────────────────────────────
    total_bits_needed = 32 + (payload_length * 8)
    if total_bits_needed > len(flat):
        raise ValueError("Declared payload length exceeds image data — image may be corrupted.")

    payload_bits = [int(flat[i] & 1) for i in range(32, total_bits_needed)]

    # ── Reconstruct bytes from bits ───────────────────────────────────────────
    payload = bytearray()
    for byte_idx in range(payload_length):
        byte_val = 0
        for bit_pos in range(8):
            byte_val = (byte_val << 1) | payload_bits[byte_idx * 8 + bit_pos]
        payload.append(byte_val)

    return bytes(payload)


def extract_data_from_bytes(stego_bytes: bytes) -> bytes:
    """
    Extract hidden payload from a stego image provided as bytes.

    Args:
        stego_bytes: Raw bytes of the stego PNG image.

    Returns:
        Extracted payload bytes.
    """
    buf = io.BytesIO(stego_bytes)
    img = Image.open(buf).convert("RGB")
    pixels = np.array(img, dtype=np.uint8)
    flat = pixels.flatten()

    if len(flat) < 32:
        raise ValueError("Image too small to contain hidden data.")

    length_bits = [int(flat[i] & 1) for i in range(32)]
    payload_length = 0
    for bit in length_bits:
        payload_length = (payload_length << 1) | bit

    max_possible = (len(flat) // 8) - 4
    if payload_length <= 0 or payload_length > max_possible:
        raise ValueError("No valid hidden data found in this image.")

    total_bits_needed = 32 + (payload_length * 8)
    payload_bits = [int(flat[i] & 1) for i in range(32, total_bits_needed)]

    payload = bytearray()
    for byte_idx in range(payload_length):
        byte_val = 0
        for bit_pos in range(8):
            byte_val = (byte_val << 1) | payload_bits[byte_idx * 8 + bit_pos]
        payload.append(byte_val)

    return bytes(payload)


def compute_psnr(original_path: str, stego_path: str) -> float:
    """
    Compute Peak Signal-to-Noise Ratio (PSNR) between original and stego images.

    PSNR measures the imperceptibility of steganography.
    Values > 40 dB are considered excellent (imperceptible to human eye).

    Args:
        original_path: Path to the original cover image.
        stego_path:    Path to the stego image.

    Returns:
        PSNR value in dB. Returns -1.0 on error.
    """
    try:
        orig = np.array(Image.open(original_path).convert("RGB"), dtype=np.float64)
        stego = np.array(Image.open(stego_path).convert("RGB"), dtype=np.float64)

        if orig.shape != stego.shape:
            return -1.0

        mse = np.mean((orig - stego) ** 2)
        if mse == 0:
            return float("inf")

        psnr = 10 * np.log10((255.0 ** 2) / mse)
        return round(psnr, 2)
    except Exception:
        return -1.0
