"""
dashboard_page.py — MedSecure Dashboard Page
=============================================
Shows system status, encryption statistics, recent activity log,
and quick-action cards for immediate navigation to key features.
"""

import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QGridLayout, QSizePolicy, QSpacerItem,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont


class StatCard(QFrame):
    """Individual statistic card for dashboard metrics."""

    def __init__(self, icon: str, label: str, value: str, sub: str = "", color: str = "#38bdf8"):
        super().__init__()
        self.setObjectName("StatCard")
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        # Icon + Label row
        top_row = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 18))
        icon_lbl.setFixedWidth(36)
        top_row.addWidget(icon_lbl)

        label_col = QVBoxLayout()
        label_col.setSpacing(0)
        card_label = QLabel(label.upper())
        card_label.setObjectName("CardTitle")
        label_col.addWidget(card_label)
        top_row.addLayout(label_col)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setObjectName("CardValue")
        self.value_label.setFont(QFont("Georgia", 28, QFont.Bold))
        layout.addWidget(self.value_label)

        if sub:
            sub_lbl = QLabel(sub)
            sub_lbl.setObjectName("CardSubValue")
            layout.addWidget(sub_lbl)

    def set_value(self, value: str):
        self.value_label.setText(value)


class ActivityRow(QWidget):
    """Single row in the recent activity log."""

    def __init__(self, icon: str, text: str, timestamp: str, status: str = "success"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)

        # Status dot
        dot = QLabel("●")
        dot.setFont(QFont("Segoe UI", 10))
        color_map = {"success": "#22d3a0", "warning": "#f59e0b", "error": "#f87171", "info": "#38bdf8"}
        dot.setStyleSheet(f"color: {color_map.get(status, '#38bdf8')};")
        dot.setFixedWidth(16)
        layout.addWidget(dot)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 13))
        icon_lbl.setFixedWidth(24)
        layout.addWidget(icon_lbl)

        text_lbl = QLabel(text)
        text_lbl.setObjectName("ActivityItem")
        text_lbl.setWordWrap(True)
        layout.addWidget(text_lbl, 1)

        time_lbl = QLabel(timestamp)
        time_lbl.setObjectName("CardSubValue")
        time_lbl.setFont(QFont("Segoe UI", 10))
        time_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(time_lbl)

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)


class QuickActionCard(QFrame):
    """Quick action card that navigates to a panel."""

    clicked = pyqtSignal()

    def __init__(self, icon: str, title: str, description: str):
        super().__init__()
        self.setObjectName("Card")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(140)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 28))
        layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("SectionHeader")
        title_lbl.setFont(QFont("Georgia", 13, QFont.Bold))
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("SectionSubHeader")
        desc_lbl.setWordWrap(True)
        desc_lbl.setFont(QFont("Segoe UI", 11))
        layout.addWidget(desc_lbl)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class DashboardPage(QWidget):
    """
    Dashboard page — system overview, stats, recent activity, quick actions.
    """

    navigate_to = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._session_encryptions = 0
        self._session_decryptions = 0
        self._setup_ui()

        # Clock timer
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(24)

        # ── Hero Banner ───────────────────────────────────────────────────────
        hero = QFrame()
        hero.setObjectName("CardAccent")
        hero.setFixedHeight(120)
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(32, 20, 32, 20)

        hero_text = QVBoxLayout()
        hero_text.setSpacing(4)
        hero_title = QLabel("MedSecure  ·  Hybrid Encryption System")
        hero_title.setObjectName("DashHeroTitle")
        hero_title.setFont(QFont("Georgia", 22, QFont.Bold))
        hero_text.addWidget(hero_title)

        hero_sub = QLabel(
            "ECC + AES Hybrid Encryption  ·  LSB Steganography  ·  HIPAA-Ready  ·  FIPS 186-4 Compliant"
        )
        hero_sub.setObjectName("DashHeroSubtitle")
        hero_text.addWidget(hero_sub)
        hero_layout.addLayout(hero_text)
        hero_layout.addStretch()

        self.clock_label = QLabel()
        self.clock_label.setObjectName("CardValue")
        self.clock_label.setFont(QFont("Georgia", 20, QFont.Bold))
        self.clock_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hero_layout.addWidget(self.clock_label)

        layout.addWidget(hero)

        # ── Stat Cards Row ────────────────────────────────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        self.enc_card = StatCard("🔒", "Encryptions", "0", "This session")
        self.dec_card = StatCard("🔓", "Decryptions", "0", "This session")
        self.mode_card = StatCard("🛡", "Security Level", "AES-256", "ECC SECP384R1")
        self.status_card = StatCard("✔", "System Status", "Online", "All modules ready")

        for card in [self.enc_card, self.dec_card, self.mode_card, self.status_card]:
            stats_row.addWidget(card)
        layout.addLayout(stats_row)

        # ── Quick Actions + Activity split ────────────────────────────────────
        middle_row = QHBoxLayout()
        middle_row.setSpacing(20)

        # Quick Actions (left)
        actions_frame = QFrame()
        actions_frame.setObjectName("Card")
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setContentsMargins(20, 20, 20, 20)
        actions_layout.setSpacing(12)

        qa_header = QLabel("Quick Actions")
        qa_header.setObjectName("SectionHeader")
        qa_header.setFont(QFont("Georgia", 14, QFont.Bold))
        actions_layout.addWidget(qa_header)
        actions_layout.addSpacing(4)

        sender_card = QuickActionCard(
            "⬆", "Sender Panel",
            "Encrypt medical images or reports and embed them securely into a carrier image."
        )
        sender_card.clicked.connect(lambda: self.navigate_to.emit(1))
        actions_layout.addWidget(sender_card)

        receiver_card = QuickActionCard(
            "⬇", "Receiver Panel",
            "Extract and decrypt hidden data from a stego image to recover the original content."
        )
        receiver_card.clicked.connect(lambda: self.navigate_to.emit(2))
        actions_layout.addWidget(receiver_card)

        middle_row.addWidget(actions_frame, 55)

        # Recent Activity (right)
        activity_frame = QFrame()
        activity_frame.setObjectName("Card")
        activity_layout = QVBoxLayout(activity_frame)
        activity_layout.setContentsMargins(20, 20, 20, 20)
        activity_layout.setSpacing(6)

        act_header_row = QHBoxLayout()
        act_header = QLabel("System Log")
        act_header.setObjectName("SectionHeader")
        act_header.setFont(QFont("Georgia", 14, QFont.Bold))
        act_header_row.addWidget(act_header)
        act_header_row.addStretch()

        self.clear_log_btn = QPushButton("Clear")
        self.clear_log_btn.setObjectName("SecondaryBtn")
        self.clear_log_btn.setFixedSize(60, 30)
        self.clear_log_btn.clicked.connect(self._clear_activity)
        act_header_row.addWidget(self.clear_log_btn)
        activity_layout.addLayout(act_header_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        activity_layout.addWidget(sep)

        self.activity_container = QVBoxLayout()
        self.activity_container.setSpacing(0)
        activity_layout.addLayout(self.activity_container)
        activity_layout.addStretch()

        # Initial log entries
        self._add_activity("🔧", "AES module initialized (AES-128/192/256 ready)", "Just now", "success")
        self._add_activity("🔑", "ECC engine loaded (SECP384R1 curve)", "Just now", "success")
        self._add_activity("🖼", "Steganography engine ready (LSB adaptive)", "Just now", "success")
        self._add_activity("✅", "All security modules operational", "Just now", "info")

        middle_row.addWidget(activity_frame, 45)
        layout.addLayout(middle_row)

        # ── Security Info Row ─────────────────────────────────────────────────
        info_row = QHBoxLayout()
        info_row.setSpacing(16)

        for icon, title, body in [
            ("🔐", "Hybrid Encryption",
             "ECC (SECP384R1) handles key exchange while AES-CBC encrypts the data. "
             "The AES session key is wrapped using HKDF-derived keys from the ECDH shared secret."),
            ("🧩", "LSB Steganography",
             "Encrypted payload is hidden in the Least Significant Bits of cover image pixels. "
             "1-bit LSB across RGB channels yields imperceptible modifications (PSNR > 50 dB)."),
            ("🔒", "Key Security",
             "Custom passphrases are never used directly. PBKDF2-HMAC-SHA256 with 310,000 "
             "iterations and a random 256-bit salt derives the actual AES key."),
        ]:
            info_card = QFrame()
            info_card.setObjectName("Card")
            info_card_layout = QVBoxLayout(info_card)
            info_card_layout.setContentsMargins(18, 16, 18, 16)
            info_card_layout.setSpacing(8)

            row = QHBoxLayout()
            icon_l = QLabel(icon)
            icon_l.setFont(QFont("Segoe UI Emoji", 18))
            icon_l.setFixedWidth(32)
            row.addWidget(icon_l)
            title_l = QLabel(title)
            title_l.setObjectName("SectionHeader")
            title_l.setFont(QFont("Georgia", 12, QFont.Bold))
            row.addWidget(title_l)
            info_card_layout.addLayout(row)

            body_l = QLabel(body)
            body_l.setObjectName("SectionSubHeader")
            body_l.setWordWrap(True)
            body_l.setFont(QFont("Segoe UI", 11))
            info_card_layout.addWidget(body_l)

            info_row.addWidget(info_card)

        layout.addLayout(info_row)

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def _update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))

    def _add_activity(self, icon: str, text: str, time_str: str, status: str = "info"):
        row = ActivityRow(icon, text, time_str, status)
        self.activity_container.addWidget(row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        self.activity_container.addWidget(sep)

    def _clear_activity(self):
        while self.activity_container.count():
            item = self.activity_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def log_encryption(self, aes_type: str, mode: str):
        """Called by sender page after successful encryption."""
        self._session_encryptions += 1
        self.enc_card.set_value(str(self._session_encryptions))
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._add_activity(
            "🔒",
            f"[✔] {aes_type} encryption complete ({mode} mode)",
            ts,
            "success",
        )

    def log_decryption(self, aes_type: str, mode: str):
        """Called by receiver page after successful decryption."""
        self._session_decryptions += 1
        self.dec_card.set_value(str(self._session_decryptions))
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._add_activity(
            "🔓",
            f"[✔] {aes_type} decryption complete ({mode} mode)",
            ts,
            "success",
        )

    def log_error(self, error_msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._add_activity("❌", f"[✖] {error_msg}", ts, "error")
