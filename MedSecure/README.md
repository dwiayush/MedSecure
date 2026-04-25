# 🔐 MedSecure — Secure Medical Data Transmission System

**Production-grade desktop application for secure medical data transmission using Hybrid ECC+AES Encryption and LSB Steganography.**

---

## 📦 Project Structure

```
MedSecure/
├── main.py                        ← Application entry point
├── requirements.txt               ← Python dependencies
├── MedSecure.spec                 ← PyInstaller build config
├── README.md
└── app/
    ├── core/
    │   ├── aes_module.py          ← AES-CBC encryption (128/192/256-bit)
    │   ├── ecc_module.py          ← ECC key exchange (SECP384R1/ECDH)
    │   ├── compression.py         ← Lossless/lossy image compression
    │   └── steganography.py       ← Adaptive LSB steganography engine
    ├── controllers/
    │   └── crypto_controller.py   ← Full hybrid encryption pipeline
    └── ui/
        ├── styles.py              ← Dark/Light theme stylesheets
        ├── dashboard_page.py      ← System overview & stats
        ├── sender_page.py         ← Encrypt & embed panel
        ├── receiver_page.py       ← Extract & decrypt panel
        └── settings_page.py       ← App settings & about
```

---

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.10 or newer
- pip (Python package manager)

### 2. Install Dependencies

```bash
# Create and activate virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python main.py
```

---

## 🔒 Security Architecture

### Hybrid Encryption Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        SENDER SIDE                               │
│                                                                   │
│  Medical Data (Image/Text)                                       │
│       │                                                          │
│       ▼                                                          │
│  [Optional Compression] ──► Lossless PNG / Raw bytes            │
│       │                                                          │
│       ▼                                                          │
│  AES Key Generation ──────► Auto: os.urandom(32)                │
│       │                     Custom: PBKDF2-HMAC-SHA256           │
│       │                            (310,000 iterations)          │
│       ▼                                                          │
│  ECC Key Exchange:                                               │
│    Sender generates ephemeral key pair (SECP384R1)              │
│    ECDH(sender_priv, receiver_pub) → shared_secret             │
│    HKDF-SHA384(shared_secret, salt) → wrapping_key             │
│    XOR(aes_key, wrapping_key) → wrapped_aes_key                │
│       │                                                          │
│       ▼                                                          │
│  AES-CBC Encryption:                                             │
│    IV = os.urandom(16)                                          │
│    SHA256(plaintext) → checksum                                 │
│    AES_CBC(data, key, iv) → ciphertext                         │
│       │                                                          │
│       ▼                                                          │
│  Payload Assembly:                                               │
│    [MAGIC|mode|aes_type|key_mode|ecc_pub|salts|                │
│     wrapped_key|iv|checksum|ciphertext|receiver_priv]           │
│       │                                                          │
│       ▼                                                          │
│  LSB Steganography:                                              │
│    Embed payload bits into cover image pixel LSBs               │
│    Output: Stego PNG (imperceptible, PSNR > 50 dB)             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       RECEIVER SIDE                              │
│                                                                   │
│  Stego Image                                                     │
│       │                                                          │
│       ▼                                                          │
│  LSB Extraction → raw payload bytes                             │
│       │                                                          │
│       ▼                                                          │
│  Parse payload header → detect mode, AES type, key mode        │
│       │                                                          │
│       ▼                                                          │
│  ECC Reconstruction:                                             │
│    ECDH(receiver_priv, sender_pub) → shared_secret             │
│    HKDF-SHA384(shared_secret, salt) → wrapping_key             │
│    XOR(wrapped_key, wrapping_key) → aes_key                    │
│       │                                                          │
│  [Custom Key Mode]:                                              │
│    PBKDF2-HMAC-SHA256(passphrase, salt) → aes_key             │
│       │                                                          │
│       ▼                                                          │
│  AES-CBC Decryption → plaintext                                 │
│       │                                                          │
│       ▼                                                          │
│  SHA-256 Integrity Check → verified ✔                          │
│       │                                                          │
│       ▼                                                          │
│  Recovered: Medical Image / Report Text                          │
└─────────────────────────────────────────────────────────────────┘
```

### Binary Payload Structure

```
┌────────────────┬──────────┬─────────────────────────────────────┐
│ Field          │ Size     │ Description                         │
├────────────────┼──────────┼─────────────────────────────────────┤
│ Magic Header   │ 8 bytes  │ b'MEDSEC01' — version marker        │
│ Mode Flag      │ 1 byte   │ 0x01=Image, 0x02=Text               │
│ AES Type       │ 1 byte   │ 0=AES128, 1=AES192, 2=AES256        │
│ Key Mode       │ 1 byte   │ 0=AutoGen, 1=CustomKey              │
│ ECC Pub Len    │ 2 bytes  │ Length of ECC public key DER        │
│ ECC Public Key │ N bytes  │ Sender ephemeral ECC key (DER)      │
│ HKDF Salt      │ 32 bytes │ HKDF key derivation salt            │
│ PBKDF2 Salt    │ 32 bytes │ Passphrase KDF salt                 │
│ Wrapped Key Len│ 2 bytes  │ Length of wrapped AES key           │
│ Wrapped AES Key│ N bytes  │ AES key XOR'd with wrapping key     │
│ IV             │ 16 bytes │ AES-CBC initialization vector       │
│ Checksum       │ 32 bytes │ SHA-256 of plaintext                │
│ Ciphertext Len │ 4 bytes  │ Length of ciphertext                │
│ Ciphertext     │ N bytes  │ AES-CBC encrypted data              │
│ Recv Priv Len  │ 4 bytes  │ Receiver private key length         │
│ Recv Priv Key  │ N bytes  │ Receiver ECC private key (demo)     │
└────────────────┴──────────┴─────────────────────────────────────┘
```

---

## 🖥️ Application Features

### Dashboard
- Real-time clock and system status
- Session encryption/decryption counters
- Security info cards (ECC, LSB, Key derivation)
- Activity log with color-coded events

### Sender Panel
- **Mode toggle**: Image Mode / Text Mode
- **AES Selection**: AES-128 / AES-192 / AES-256 dropdown
- **Key Mode**: Auto-generated OR Custom passphrase
- **Image upload**: Medical image + Cover image
- **Text input**: Patient reports, medical data
- **Image previews**: Data image, Cover image, Stego output
- **Compression**: Optional lossless PNG compression
- **Progress bar** + live operation log
- **PSNR metric**: Imperceptibility measurement

### Receiver Panel
- Upload stego image → auto-detect parameters
- Optional passphrase input (if custom key used)
- Recovered image preview
- Decrypted text display + save option
- SHA-256 integrity verification result
- Full operation log

### Settings
- Dark / Light theme toggle
- Security configuration reference
- About / version info

---

## 📦 Build Executable (.exe)

### Windows

```bash
# Install PyInstaller
pip install pyinstaller

# Build using spec file (recommended)
pyinstaller MedSecure.spec

# OR quick single-file build
pyinstaller --onefile --windowed --name MedSecure main.py

# Output: dist/MedSecure/MedSecure.exe
```

### macOS

```bash
pyinstaller --onefile --windowed --name MedSecure main.py
# Output: dist/MedSecure.app
```

### Linux

```bash
pyinstaller --onefile --name MedSecure main.py
# Output: dist/MedSecure
```

---

## ⚙️ Technical Specifications

| Component        | Specification                                      |
|------------------|----------------------------------------------------|
| ECC Curve        | SECP384R1 / NIST P-384 (FIPS 186-4)              |
| ECC Security     | 192-bit equivalent security level                  |
| AES Mode         | CBC (Cipher Block Chaining) with PKCS7 padding    |
| AES Key Options  | 128-bit, 192-bit, 256-bit                          |
| IV Generation    | os.urandom(16) — cryptographically secure          |
| Key Derivation   | PBKDF2-HMAC-SHA256, 310,000 iterations (OWASP'23) |
| KDF Salt         | os.urandom(32) — 256-bit random salt              |
| ECDH KDF         | HKDF-SHA384 with 256-bit salt                     |
| Integrity        | SHA-256 with constant-time comparison (hmac)      |
| Steganography    | 1-bit LSB, RGB channels, PNG lossless output      |
| Cover Capacity   | (W × H × 3) / 8 − 4 bytes                        |
| Imperceptibility | PSNR typically > 50 dB                            |
| GUI Framework    | PyQt5 with QThread background workers             |

---

## ⚠️ Important Notes

1. **Cover image must be PNG** — JPEG compression destroys LSB data. The app always saves stego images as PNG.
2. **Cover image capacity** — A 1920×1080 cover image holds ~777 KB of payload. Use larger images for bigger medical files.
3. **Demo key mode** — In this demo, the receiver ECC private key is embedded in the stego payload. In production, the receiver's private key would be stored securely on the receiver's system only.
4. **Custom passphrase** — Minimum 8 characters. PBKDF2-HMAC-SHA256 derives the actual AES key — the raw passphrase is never used directly.

---

## 📋 Compliance Notes

- **HIPAA Technical Safeguards**: AES-256 encryption for ePHI data at rest and in transit
- **FIPS 186-4**: NIST P-384 (SECP384R1) curve for ECC operations
- **NIST SP 800-132**: PBKDF2 key derivation with approved parameters
- **OWASP 2023**: 310,000 PBKDF2-SHA256 iterations for password hashing

---

*MedSecure v1.0.0 — Production Release*
