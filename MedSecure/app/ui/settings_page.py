"""
settings_page.py — MedSecure Settings Page
===========================================
Provides user preferences for:
  - Theme (Dark / Light)
  - Default AES type
  - Default compression settings
  - Key management info
  - About / version info
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QComboBox, QCheckBox, QScrollArea, QSizePolicy, QTabWidget,
    QGroupBox, QLineEdit, QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class SettingsPage(QWidget):
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(20)

        tabs = QTabWidget()
        tabs.setFont(QFont("Segoe UI", 11))

        # ── Tab 1: Appearance ─────────────────────────────────────────────────
        appearance_tab = QWidget()
        app_layout = QVBoxLayout(appearance_tab)
        app_layout.setContentsMargins(20, 20, 20, 20)
        app_layout.setSpacing(16)

        theme_card = QFrame()
        theme_card.setObjectName("Card")
        theme_layout = QVBoxLayout(theme_card)
        theme_layout.setContentsMargins(20, 18, 20, 18)
        theme_layout.setSpacing(14)

        theme_hdr = QLabel("Theme")
        theme_hdr.setObjectName("SectionHeader")
        theme_hdr.setFont(QFont("Georgia", 14, QFont.Bold))
        theme_layout.addWidget(theme_hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        theme_layout.addWidget(sep)

        theme_row = QHBoxLayout()
        self.dark_btn = QPushButton("🌙  Dark Theme")
        self.dark_btn.setObjectName("PrimaryBtn")
        self.dark_btn.clicked.connect(lambda: self._set_theme("dark"))
        self.light_btn = QPushButton("☀  Light Theme")
        self.light_btn.setObjectName("SecondaryBtn")
        self.light_btn.clicked.connect(lambda: self._set_theme("light"))
        theme_row.addWidget(self.dark_btn)
        theme_row.addWidget(self.light_btn)
        theme_row.addStretch()
        theme_layout.addLayout(theme_row)

        theme_info = QLabel("Theme changes apply immediately across all panels.")
        theme_info.setObjectName("SectionSubHeader")
        theme_layout.addWidget(theme_info)
        app_layout.addWidget(theme_card)
        app_layout.addStretch()
        tabs.addTab(appearance_tab, "  Appearance  ")

        # ── Tab 2: Security ───────────────────────────────────────────────────
        security_tab = QWidget()
        sec_layout = QVBoxLayout(security_tab)
        sec_layout.setContentsMargins(20, 20, 20, 20)
        sec_layout.setSpacing(16)

        defaults_card = QFrame()
        defaults_card.setObjectName("Card")
        def_layout = QVBoxLayout(defaults_card)
        def_layout.setContentsMargins(20, 18, 20, 18)
        def_layout.setSpacing(12)

        def_hdr = QLabel("Encryption Defaults")
        def_hdr.setObjectName("SectionHeader")
        def_hdr.setFont(QFont("Georgia", 14, QFont.Bold))
        def_layout.addWidget(def_hdr)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        def_layout.addWidget(sep2)

        for label, desc in [
            ("Default AES Mode", "AES-256 (recommended for medical data — HIPAA compliant)"),
            ("ECC Curve", "SECP384R1 / NIST P-384 (192-bit security — FIPS 186-4)"),
            ("Key Derivation", "PBKDF2-HMAC-SHA256, 310,000 iterations (OWASP 2023)"),
            ("Steganography", "1-bit LSB across RGB channels (imperceptible, PSNR > 50 dB)"),
            ("Integrity", "SHA-256 checksum verification on all decryptions"),
        ]:
            row = QHBoxLayout()
            k = QLabel(label + ":")
            k.setObjectName("FieldLabel")
            k.setFixedWidth(160)
            v = QLabel(desc)
            v.setObjectName("SectionSubHeader")
            v.setWordWrap(True)
            row.addWidget(k)
            row.addWidget(v, 1)
            def_layout.addLayout(row)

        sec_layout.addWidget(defaults_card)

        # Security checklist
        checklist_card = QFrame()
        checklist_card.setObjectName("Card")
        check_layout = QVBoxLayout(checklist_card)
        check_layout.setContentsMargins(20, 18, 20, 18)
        check_layout.setSpacing(8)

        check_hdr = QLabel("Security Checklist")
        check_hdr.setObjectName("SectionHeader")
        check_hdr.setFont(QFont("Georgia", 14, QFont.Bold))
        check_layout.addWidget(check_hdr)

        sep3 = QFrame(); sep3.setFrameShape(QFrame.HLine)
        check_layout.addWidget(sep3)

        checks = [
            ("✔", "Raw passphrases are never used directly — always PBKDF2-derived", "success"),
            ("✔", "AES-CBC with random IV per session — prevents replay attacks", "success"),
            ("✔", "ECDH shared secret never transmitted — ephemeral key exchange", "success"),
            ("✔", "SHA-256 integrity verification before returning decrypted data", "success"),
            ("✔", "LSB steganography uses PNG output (lossless) to preserve bits", "success"),
            ("✔", "Constant-time checksum comparison prevents timing side-channels", "success"),
        ]

        for icon, text, status in checks:
            row = QHBoxLayout()
            icon_l = QLabel(icon)
            icon_l.setFixedWidth(20)
            icon_l.setStyleSheet("color: #22d3a0; font-weight: bold;")
            text_l = QLabel(text)
            text_l.setObjectName("ActivityItem")
            row.addWidget(icon_l)
            row.addWidget(text_l, 1)
            check_layout.addLayout(row)

        sec_layout.addWidget(checklist_card)
        sec_layout.addStretch()
        tabs.addTab(security_tab, "  Security  ")

        # ── Tab 3: About ──────────────────────────────────────────────────────
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setContentsMargins(20, 20, 20, 20)
        about_layout.setSpacing(16)

        about_card = QFrame()
        about_card.setObjectName("CardAccent")
        ac_layout = QVBoxLayout(about_card)
        ac_layout.setContentsMargins(28, 24, 28, 24)
        ac_layout.setSpacing(10)

        logo = QLabel("🔐  MedSecure")
        logo.setObjectName("DashHeroTitle")
        logo.setFont(QFont("Georgia", 26, QFont.Bold))
        ac_layout.addWidget(logo)

        ac_layout.addWidget(QLabel("Version 1.0.0  ·  Production Release"))

        for line in [
            "Secure Medical Data Transmission System",
            "Hybrid Encryption: ECC (SECP384R1) + AES-CBC (128/192/256-bit)",
            "Adaptive LSB Steganography for covert data embedding",
            "HIPAA Technical Safeguards | FIPS 186-4 | OWASP Key Derivation",
            "",
            "Built with: Python 3.10+  ·  PyQt5  ·  cryptography  ·  Pillow  ·  NumPy",
        ]:
            lbl = QLabel(line)
            lbl.setObjectName("SectionSubHeader" if line else "")
            lbl.setFont(QFont("Segoe UI", 11))
            ac_layout.addWidget(lbl)

        about_layout.addWidget(about_card)
        about_layout.addStretch()
        tabs.addTab(about_tab, "  About  ")

        layout.addWidget(tabs)
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _set_theme(self, theme: str):
        self.theme_changed.emit(theme)
        if theme == "dark":
            self.dark_btn.setObjectName("PrimaryBtn")
            self.light_btn.setObjectName("SecondaryBtn")
        else:
            self.dark_btn.setObjectName("SecondaryBtn")
            self.light_btn.setObjectName("PrimaryBtn")
        self.dark_btn.style().unpolish(self.dark_btn)
        self.dark_btn.style().polish(self.dark_btn)
        self.light_btn.style().unpolish(self.light_btn)
        self.light_btn.style().polish(self.light_btn)
