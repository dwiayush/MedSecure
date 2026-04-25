"""
main.py — MedSecure Application Entry Point & Main Window
=========================================================
Architecture:
  - QMainWindow with collapsible sidebar navigation.
  - Stacked widget for page switching (Dashboard, Sender, Receiver, Settings).
  - Worker threads (QThread) for crypto operations to keep UI responsive.
  - Signal/slot system for progress updates and log messages.
"""

import sys
import os

# ── Add project root to path ──────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect, QScrollArea,
)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QFontDatabase, QIcon, QPixmap, QColor, QPalette, QCursor

from app.ui.dashboard_page import DashboardPage
from app.ui.sender_page import SenderPage
from app.ui.receiver_page import ReceiverPage
from app.ui.settings_page import SettingsPage
from app.ui.styles import DARK_THEME, LIGHT_THEME


# ─────────────────────────────────────────────────────────────────────────────
# THEME MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class ThemeManager:
    """Singleton-style theme manager shared across all pages."""
    _current = "dark"
    _listeners = []

    @classmethod
    def current_theme(cls) -> str:
        return cls._current

    @classmethod
    def toggle(cls):
        cls._current = "light" if cls._current == "dark" else "dark"
        for cb in cls._listeners:
            cb(cls._current)

    @classmethod
    def stylesheet(cls) -> str:
        return DARK_THEME if cls._current == "dark" else LIGHT_THEME

    @classmethod
    def register(cls, callback):
        cls._listeners.append(callback)

    @classmethod
    def is_dark(cls) -> bool:
        return cls._current == "dark"


# ─────────────────────────────────────────────────────────────────────────────
# NAV BUTTON
# ─────────────────────────────────────────────────────────────────────────────

class NavButton(QPushButton):
    """Sidebar navigation button with icon + label and active state."""

    def __init__(self, icon_text: str, label: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.label_text = label
        self._active = False
        self._collapsed = False
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setCheckable(False)
        self.setFixedHeight(52)
        self._update_text()

    def _update_text(self):
        if self._collapsed:
            self.setText(self.icon_text)
            self.setToolTip(self.label_text)
        else:
            self.setText(f"  {self.icon_text}  {self.label_text}")
            self.setToolTip("")

    def set_active(self, active: bool):
        self._active = active
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_collapsed(self, collapsed: bool):
        self._collapsed = collapsed
        self._update_text()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

class Sidebar(QFrame):
    """Collapsible left sidebar with navigation buttons."""

    page_changed = pyqtSignal(int)
    EXPANDED_WIDTH = 240
    COLLAPSED_WIDTH = 68

    def __init__(self, parent=None):
        super().__init__(parent)
        self._collapsed = False
        self.setObjectName("Sidebar")
        self.setFixedWidth(self.EXPANDED_WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Logo area ─────────────────────────────────────────────────────────
        self.logo_frame = QFrame()
        self.logo_frame.setObjectName("LogoFrame")
        self.logo_frame.setFixedHeight(80)
        logo_layout = QHBoxLayout(self.logo_frame)
        logo_layout.setContentsMargins(16, 0, 16, 0)

        self.logo_icon = QLabel("🔐")
        self.logo_icon.setFont(QFont("Segoe UI Emoji", 22))
        self.logo_icon.setFixedWidth(36)
        logo_layout.addWidget(self.logo_icon)

        self.logo_text = QLabel("MedSecure")
        self.logo_text.setObjectName("LogoText")
        self.logo_text.setFont(QFont("Georgia", 15, QFont.Bold))
        logo_layout.addWidget(self.logo_text)
        layout.addWidget(self.logo_frame)

        # ── Divider ───────────────────────────────────────────────────────────
        div = QFrame()
        div.setObjectName("Divider")
        div.setFixedHeight(1)
        layout.addWidget(div)
        layout.addSpacing(12)

        # ── Nav section label ─────────────────────────────────────────────────
        self.nav_label = QLabel("  NAVIGATION")
        self.nav_label.setObjectName("NavSectionLabel")
        self.nav_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self.nav_label)
        layout.addSpacing(4)

        # ── Nav buttons ───────────────────────────────────────────────────────
        nav_items = [
            ("⊞", "Dashboard"),
            ("⬆", "Sender Panel"),
            ("⬇", "Receiver Panel"),
            ("⚙", "Settings"),
        ]
        self.nav_buttons = []
        for i, (icon, label) in enumerate(nav_items):
            btn = NavButton(icon, label)
            btn.setObjectName("NavButton")
            btn.clicked.connect(lambda checked, idx=i: self._on_nav_click(idx))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addSpacing(8)

        # ── Divider ───────────────────────────────────────────────────────────
        div2 = QFrame()
        div2.setObjectName("Divider")
        div2.setFixedHeight(1)
        layout.addWidget(div2)
        layout.addSpacing(8)

        # ── Tools section label ───────────────────────────────────────────────
        self.tools_label = QLabel("  TOOLS")
        self.tools_label.setObjectName("NavSectionLabel")
        self.tools_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self.tools_label)
        layout.addSpacing(4)

        self.toggle_btn = NavButton("◀", "Collapse Sidebar")
        self.toggle_btn.setObjectName("NavButton")
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        layout.addWidget(self.toggle_btn)

        layout.addStretch()

        # ── Version footer ────────────────────────────────────────────────────
        self.version_label = QLabel("  v1.0.0  |  HIPAA Ready")
        self.version_label.setObjectName("VersionLabel")
        self.version_label.setFont(QFont("Segoe UI", 8))
        layout.addWidget(self.version_label)
        layout.addSpacing(12)

        # Activate first button
        self.nav_buttons[0].set_active(True)

    def _on_nav_click(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)
        self.page_changed.emit(index)

    def toggle_collapse(self):
        self._collapsed = not self._collapsed
        target_w = self.COLLAPSED_WIDTH if self._collapsed else self.EXPANDED_WIDTH

        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(200)
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(target_w)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.anim2 = QPropertyAnimation(self, b"maximumWidth")
        self.anim2.setDuration(200)
        self.anim2.setStartValue(self.width())
        self.anim2.setEndValue(target_w)
        self.anim2.setEasingCurve(QEasingCurve.InOutQuad)

        self.anim.start()
        self.anim2.start()

        # Update all button collapsed state
        for btn in self.nav_buttons:
            btn.set_collapsed(self._collapsed)
        self.toggle_btn.set_collapsed(self._collapsed)

        # Show/hide text labels
        self.logo_text.setVisible(not self._collapsed)
        self.nav_label.setVisible(not self._collapsed)
        self.tools_label.setVisible(not self._collapsed)
        self.version_label.setVisible(not self._collapsed)

        if self._collapsed:
            self.toggle_btn.icon_text = "▶"
            self.toggle_btn._update_text()
        else:
            self.toggle_btn.icon_text = "◀"
            self.toggle_btn._update_text()

    def set_page(self, index: int):
        self._on_nav_click(index)


# ─────────────────────────────────────────────────────────────────────────────
# TITLE BAR
# ─────────────────────────────────────────────────────────────────────────────

class TitleBar(QFrame):
    """Custom top title bar with breadcrumb and theme toggle."""

    theme_toggled = pyqtSignal()

    PAGE_TITLES = {
        0: ("Dashboard", "System overview and statistics"),
        1: ("Sender Panel", "Encrypt & embed medical data"),
        2: ("Receiver Panel", "Extract & decrypt stego images"),
        3: ("Settings", "Application preferences"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 24, 0)

        # ── Page title ────────────────────────────────────────────────────────
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("PageTitle")
        self.page_title.setFont(QFont("Georgia", 16, QFont.Bold))
        title_col.addWidget(self.page_title)

        self.page_subtitle = QLabel("System overview and statistics")
        self.page_subtitle.setObjectName("PageSubtitle")
        self.page_subtitle.setFont(QFont("Segoe UI", 9))
        title_col.addWidget(self.page_subtitle)

        layout.addLayout(title_col)
        layout.addStretch()

        # ── Status pill ───────────────────────────────────────────────────────
        self.status_pill = QLabel("● SYSTEM READY")
        self.status_pill.setObjectName("StatusPill")
        self.status_pill.setFont(QFont("Segoe UI", 9, QFont.Bold))
        layout.addWidget(self.status_pill)
        layout.addSpacing(16)

        # ── Theme toggle ──────────────────────────────────────────────────────
        self.theme_btn = QPushButton("☀  Light Mode")
        self.theme_btn.setObjectName("ThemeToggleBtn")
        self.theme_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.theme_btn.clicked.connect(self._on_theme_click)
        layout.addWidget(self.theme_btn)

    def _on_theme_click(self):
        ThemeManager.toggle()
        if ThemeManager.is_dark():
            self.theme_btn.setText("☀  Light Mode")
        else:
            self.theme_btn.setText("🌙  Dark Mode")
        self.theme_toggled.emit()

    def set_page(self, index: int):
        title, subtitle = self.PAGE_TITLES.get(index, ("", ""))
        self.page_title.setText(title)
        self.page_subtitle.setText(subtitle)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """
    MedSecure main application window.
    Layout: [Sidebar] | [TitleBar + StackedWidget]
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MedSecure — Secure Medical Data Transmission")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 860)
        self.setObjectName("MainWindow")

        # ── Central widget ────────────────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────────────
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._switch_page)
        main_layout.addWidget(self.sidebar)

        # ── Right content area ────────────────────────────────────────────────
        right_area = QWidget()
        right_area.setObjectName("RightArea")
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Title bar
        self.title_bar = TitleBar()
        self.title_bar.theme_toggled.connect(self._apply_theme)
        right_layout.addWidget(self.title_bar)

        # Thin separator
        sep = QFrame()
        sep.setObjectName("TitleSeparator")
        sep.setFixedHeight(1)
        right_layout.addWidget(sep)

        # Stacked pages
        self.stack = QStackedWidget()
        self.stack.setObjectName("PageStack")

        self.dashboard = DashboardPage()
        self.sender = SenderPage()
        self.receiver = ReceiverPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.sender)
        self.stack.addWidget(self.receiver)
        self.stack.addWidget(self.settings_page)

        right_layout.addWidget(self.stack)
        main_layout.addWidget(right_area)

        # ── Connect sender → receiver pass-through ────────────────────────────
        self.sender.navigate_to_receiver.connect(lambda: self._switch_page(2))
        self.settings_page.theme_changed.connect(self._handle_settings_theme)

        # ── Apply initial theme ───────────────────────────────────────────────
        self._apply_theme()

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        self.title_bar.set_page(index)
        self.sidebar.nav_buttons[index].set_active(True)
        for i, btn in enumerate(self.sidebar.nav_buttons):
            btn.set_active(i == index)

    def _apply_theme(self):
        self.setStyleSheet(ThemeManager.stylesheet())

    def _handle_settings_theme(self, theme_name: str):
        if theme_name == "dark" and ThemeManager.current_theme() != "dark":
            ThemeManager.toggle()
            self.title_bar.theme_btn.setText("☀  Light Mode")
        elif theme_name == "light" and ThemeManager.current_theme() != "light":
            ThemeManager.toggle()
            self.title_bar.theme_btn.setText("🌙  Dark Mode")
        self._apply_theme()


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MedSecure")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MedSecure Health Systems")

    # High DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Load font
    QFontDatabase.addApplicationFont(":/fonts/Inter-Regular.ttf")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
