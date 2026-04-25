"""
compression.py — Medical Image Compression
===========================================
Compression Strategy:
  - Uses Pillow for lossless (PNG) and lossy (JPEG/WebP) compression.
  - Before encryption, images can be compressed to reduce steganography payload size.
  - Lossless compression preferred for medical imagery (diagnostic fidelity).
  - Compression level is adaptive based on available cover image capacity.

DICOM Note:
  - In a full production system, DICOM files would be pre-processed here.
  - Current implementation handles standard raster formats: PNG, JPEG, BMP, TIFF.
"""

import io
import struct
from PIL import Image


def compress_image(image_path: str, quality: int = 85, lossless: bool = True) -> bytes:
    """
    Compress an image file and return its byte representation.

    Medical images should typically use lossless compression to preserve
    diagnostic accuracy. Lossy compression is available for non-diagnostic use.

    Args:
        image_path: Path to the source image file.
        quality:    JPEG quality (1–95). Ignored for lossless.
        lossless:   If True, use PNG (lossless). If False, use JPEG.

    Returns:
        Compressed image as bytes.

    Raises:
        FileNotFoundError: If image_path does not exist.
        ValueError:        If the file is not a supported image format.
    """
    try:
        img = Image.open(image_path)

        # Convert to RGB if needed (e.g., RGBA PNG → JPEG requires RGB)
        if img.mode in ("RGBA", "P") and not lossless:
            img = img.convert("RGB")
        elif img.mode not in ("RGB", "L", "RGBA"):
            img = img.convert("RGB")

        buf = io.BytesIO()

        if lossless:
            # PNG lossless with maximum compression level
            img.save(buf, format="PNG", optimize=True, compress_level=9)
        else:
            # JPEG lossy — suitable for photographic medical images when space is critical
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)

        compressed_bytes = buf.getvalue()
        return compressed_bytes

    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image_path}")
    except Exception as e:
        raise ValueError(f"Image compression failed: {e}")


def compress_image_from_bytes(image_bytes: bytes, quality: int = 85, lossless: bool = True) -> bytes:
    """
    Compress image from raw bytes (in-memory operation).

    Args:
        image_bytes: Raw image bytes.
        quality:     JPEG quality (ignored for lossless).
        lossless:    Use lossless PNG compression.

    Returns:
        Compressed image bytes.
    """
    try:
        buf_in = io.BytesIO(image_bytes)
        img = Image.open(buf_in)

        if img.mode not in ("RGB", "L", "RGBA"):
            img = img.convert("RGB")

        buf_out = io.BytesIO()

        if lossless:
            img.save(buf_out, format="PNG", optimize=True, compress_level=9)
        else:
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(buf_out, format="JPEG", quality=quality, optimize=True)

        return buf_out.getvalue()

    except Exception as e:
        raise ValueError(f"In-memory image compression failed: {e}")


def load_image_bytes(image_path: str) -> bytes:
    """
    Load raw image file bytes from disk.

    Args:
        image_path: Path to image file.

    Returns:
        Raw file bytes.
    """
    with open(image_path, "rb") as f:
        return f.read()


def get_image_info(image_path: str) -> dict:
    """
    Extract basic image metadata for display in the UI.

    Args:
        image_path: Path to image file.

    Returns:
        Dictionary with keys: width, height, mode, format, file_size_bytes.
    """
    try:
        img = Image.open(image_path)
        import os
        file_size = os.path.getsize(image_path)
        return {
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
            "format": img.format or "Unknown",
            "file_size_bytes": file_size,
            "megapixels": round((img.width * img.height) / 1_000_000, 2),
        }
    except Exception as e:
        raise ValueError(f"Cannot read image info: {e}")


def calculate_steganography_capacity(cover_image_path: str) -> int:
    """
    Calculate the maximum number of bytes that can be hidden in a cover image
    using 1-bit LSB steganography.

    Capacity = (total pixels * 3 color channels * 1 bit per channel) / 8 bits per byte
             minus 4 bytes for the length header.

    Args:
        cover_image_path: Path to the cover (carrier) image.

    Returns:
        Maximum hideable bytes.
    """
    try:
        img = Image.open(cover_image_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        total_pixels = img.width * img.height
        capacity_bits = total_pixels * 3  # R, G, B channels — 1 bit each
        capacity_bytes = (capacity_bits // 8) - 4  # Reserve 4 bytes for length header
        return max(0, capacity_bytes)
    except Exception:
        return 0


def estimate_compression_ratio(original_path: str, compressed_bytes: bytes) -> float:
    """
    Compute the compression ratio achieved.

    Args:
        original_path:    Path to the original image.
        compressed_bytes: Compressed byte string.

    Returns:
        Compression ratio as a float (e.g., 0.45 means 55% size reduction).
    """
    import os
    original_size = os.path.getsize(original_path)
    compressed_size = len(compressed_bytes)
    if original_size == 0:
        return 1.0
    return compressed_size / original_size
