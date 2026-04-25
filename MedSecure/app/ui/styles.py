"""
styles.py — MedSecure Complete Stylesheet
==========================================
Design Language:
  - Medical/clinical aesthetic: precise, trustworthy, clean.
  - Dark theme: Deep navy/slate with teal accents (clinical tech feel).
  - Light theme: Soft white/grey with blue-green accents.
  - Typography: Georgia for headings, Segoe UI for body.
  - Subtle depth through borders and box shadows.
"""

DARK_THEME = """
/* ═══════════════════════════════════════════════════════════
   GLOBAL BASE
   ═══════════════════════════════════════════════════════════ */
QMainWindow, QWidget#RightArea {
    background-color: #0f1923;
    color: #e2e8f0;
}

QWidget {
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: #e2e8f0;
}

/* ═══════════════════════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════════════════════ */
QFrame#Sidebar {
    background-color: #0b1520;
    border-right: 1px solid #1e3a52;
}

QLabel#LogoText {
    color: #38bdf8;
    font-size: 17px;
    font-weight: bold;
    font-family: Georgia, serif;
    letter-spacing: 1px;
}

QLabel#NavSectionLabel {
    color: #4a6d8c;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    padding-left: 8px;
}

QLabel#VersionLabel {
    color: #2d5a7a;
    font-size: 9px;
    padding-left: 8px;
}

QPushButton#NavButton {
    text-align: left;
    padding: 0px 18px;
    font-size: 13px;
    font-weight: 500;
    color: #7a9bb5;
    background-color: transparent;
    border: none;
    border-radius: 0px;
    border-left: 3px solid transparent;
}

QPushButton#NavButton:hover {
    background-color: #112233;
    color: #e2e8f0;
    border-left: 3px solid #2d7a9a;
}

QPushButton#NavButton[active=true] {
    background-color: #0f2d44;
    color: #38bdf8;
    border-left: 3px solid #38bdf8;
    font-weight: bold;
}

QFrame#Divider {
    background-color: #1e3a52;
    max-height: 1px;
}

QFrame#LogoFrame {
    background-color: #0b1520;
    border-bottom: 1px solid #1a3348;
}

/* ═══════════════════════════════════════════════════════════
   TITLE BAR
   ═══════════════════════════════════════════════════════════ */
QFrame#TitleBar {
    background-color: #0f1d2e;
    border-bottom: 0px;
}

QFrame#TitleSeparator {
    background-color: #1e3a52;
}

QLabel#PageTitle {
    color: #e2e8f0;
    font-family: Georgia, serif;
    font-size: 18px;
    font-weight: bold;
}

QLabel#PageSubtitle {
    color: #4a8aab;
    font-size: 11px;
}

QLabel#StatusPill {
    color: #22d3a0;
    background-color: #0a2e1e;
    border: 1px solid #22d3a0;
    border-radius: 12px;
    padding: 4px 14px;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
}

QPushButton#ThemeToggleBtn {
    background-color: #1a3a55;
    color: #7fc4e8;
    border: 1px solid #2a5a7a;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton#ThemeToggleBtn:hover {
    background-color: #1f4a6a;
    color: #a8d8f0;
}

/* ═══════════════════════════════════════════════════════════
   PAGE STACK
   ═══════════════════════════════════════════════════════════ */
QStackedWidget#PageStack {
    background-color: #0f1923;
}

/* ═══════════════════════════════════════════════════════════
   CARDS / PANELS
   ═══════════════════════════════════════════════════════════ */
QFrame#Card {
    background-color: #0f2035;
    border: 1px solid #1e3a55;
    border-radius: 12px;
    padding: 4px;
}

QFrame#CardAccent {
    background-color: #0f2035;
    border: 1px solid #38bdf8;
    border-radius: 12px;
}

QFrame#StatCard {
    background-color: #0d1e30;
    border: 1px solid #1a3550;
    border-radius: 10px;
}

QLabel#CardTitle {
    color: #7fc8e8;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1.5px;
}

QLabel#CardValue {
    color: #38bdf8;
    font-size: 32px;
    font-weight: bold;
    font-family: Georgia, serif;
}

QLabel#CardSubValue {
    color: #4a8aab;
    font-size: 11px;
}

/* ═══════════════════════════════════════════════════════════
   SECTION HEADERS
   ═══════════════════════════════════════════════════════════ */
QLabel#SectionHeader {
    color: #e2e8f0;
    font-size: 15px;
    font-weight: bold;
    font-family: Georgia, serif;
}

QLabel#SectionSubHeader {
    color: #4a8aab;
    font-size: 11px;
}

QLabel#FieldLabel {
    color: #7aaccc;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

/* ═══════════════════════════════════════════════════════════
   INPUT CONTROLS
   ═══════════════════════════════════════════════════════════ */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #091524;
    border: 1px solid #1e3a55;
    border-radius: 8px;
    padding: 10px 14px;
    color: #c8e6f5;
    font-size: 13px;
    selection-background-color: #1a5a7a;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #38bdf8;
    background-color: #0a1c30;
}

QLineEdit:disabled {
    background-color: #071018;
    color: #2d5a7a;
    border-color: #0f2535;
}

QComboBox {
    background-color: #091524;
    border: 1px solid #1e3a55;
    border-radius: 8px;
    padding: 10px 14px;
    color: #c8e6f5;
    font-size: 13px;
    min-width: 140px;
}

QComboBox:focus {
    border: 1px solid #38bdf8;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #0f2035;
    border: 1px solid #1e3a55;
    color: #c8e6f5;
    selection-background-color: #1a4a6a;
    outline: none;
    border-radius: 4px;
}

/* ═══════════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════════ */
QPushButton#PrimaryBtn {
    background-color: #0e5a8a;
    color: #ffffff;
    border: 1px solid #38bdf8;
    border-radius: 9px;
    padding: 12px 28px;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

QPushButton#PrimaryBtn:hover {
    background-color: #1270a8;
    border-color: #60d0ff;
}

QPushButton#PrimaryBtn:pressed {
    background-color: #0a4570;
}

QPushButton#PrimaryBtn:disabled {
    background-color: #091822;
    color: #2a5a7a;
    border-color: #1a3a55;
}

QPushButton#SecondaryBtn {
    background-color: transparent;
    color: #38bdf8;
    border: 1px solid #2a5a7a;
    border-radius: 9px;
    padding: 11px 24px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton#SecondaryBtn:hover {
    background-color: #0f2a3f;
    border-color: #38bdf8;
}

QPushButton#DangerBtn {
    background-color: #2a0f0f;
    color: #f87171;
    border: 1px solid #7a2020;
    border-radius: 9px;
    padding: 11px 24px;
    font-size: 13px;
}

QPushButton#DangerBtn:hover {
    background-color: #3a1515;
    border-color: #f87171;
}

QPushButton#UploadBtn {
    background-color: #091a2a;
    color: #7fc8e8;
    border: 2px dashed #2a5a7a;
    border-radius: 10px;
    padding: 20px;
    font-size: 13px;
}

QPushButton#UploadBtn:hover {
    background-color: #0f2535;
    border-color: #38bdf8;
    color: #a8e0f8;
}

/* ═══════════════════════════════════════════════════════════
   TOGGLE / CHECKBOX
   ═══════════════════════════════════════════════════════════ */
QCheckBox {
    color: #a0c8e0;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #2a5a7a;
    background-color: #091524;
}

QCheckBox::indicator:checked {
    background-color: #0e7a9a;
    border-color: #38bdf8;
}

/* ═══════════════════════════════════════════════════════════
   RADIO BUTTONS
   ═══════════════════════════════════════════════════════════ */
QRadioButton {
    color: #a0c8e0;
    font-size: 13px;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 1px solid #2a5a7a;
    background-color: #091524;
}

QRadioButton::indicator:checked {
    background-color: #38bdf8;
    border-color: #38bdf8;
}

/* ═══════════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════════ */
QProgressBar {
    background-color: #091524;
    border: 1px solid #1a3550;
    border-radius: 6px;
    height: 10px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0e5a8a, stop:1 #38bdf8);
    border-radius: 5px;
}

/* ═══════════════════════════════════════════════════════════
   LOG PANEL
   ═══════════════════════════════════════════════════════════ */
QPlainTextEdit#LogPanel {
    background-color: #050e18;
    border: 1px solid #1a3550;
    border-radius: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    color: #4fcf90;
    padding: 10px;
}

/* ═══════════════════════════════════════════════════════════
   SCROLL BARS
   ═══════════════════════════════════════════════════════════ */
QScrollBar:vertical {
    background-color: #091524;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #1e3a55;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #2a5a7a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #091524;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #1e3a55;
    border-radius: 4px;
    min-width: 20px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ═══════════════════════════════════════════════════════════
   IMAGE PREVIEW
   ═══════════════════════════════════════════════════════════ */
QFrame#ImagePreviewFrame {
    background-color: #050e18;
    border: 1px solid #1a3550;
    border-radius: 10px;
}

QLabel#ImagePreviewLabel {
    color: #2a5a7a;
    font-size: 12px;
}

/* ═══════════════════════════════════════════════════════════
   SEPARATOR
   ═══════════════════════════════════════════════════════════ */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #1a3550;
    background-color: #1a3550;
}

/* ═══════════════════════════════════════════════════════════
   TABS (Settings)
   ═══════════════════════════════════════════════════════════ */
QTabWidget::pane {
    border: 1px solid #1e3a55;
    border-radius: 8px;
    background-color: #0f2035;
    top: -1px;
}

QTabBar::tab {
    background-color: #091524;
    color: #4a8aab;
    padding: 10px 22px;
    border: 1px solid #1a3550;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    font-size: 12px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #0f2035;
    color: #38bdf8;
    border-color: #1e3a55;
}

QTabBar::tab:hover:!selected {
    background-color: #0d1e30;
    color: #7fc8e8;
}

/* ═══════════════════════════════════════════════════════════
   TOOLTIPS
   ═══════════════════════════════════════════════════════════ */
QToolTip {
    background-color: #0f2035;
    color: #c8e6f5;
    border: 1px solid #2a5a7a;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ═══════════════════════════════════════════════════════════
   DASHBOARD SPECIFIC
   ═══════════════════════════════════════════════════════════ */
QLabel#DashHeroTitle {
    color: #38bdf8;
    font-size: 28px;
    font-weight: bold;
    font-family: Georgia, serif;
}

QLabel#DashHeroSubtitle {
    color: #4a8aab;
    font-size: 13px;
}

QLabel#ActivityItem {
    color: #7aaccc;
    font-size: 12px;
    padding: 4px 0px;
}

QFrame#ActivityDot {
    background-color: #22d3a0;
    border-radius: 5px;
}

/* ═══════════════════════════════════════════════════════════
   SCROLL AREA
   ═══════════════════════════════════════════════════════════ */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}
"""


LIGHT_THEME = """
/* ═══════════════════════════════════════════════════════════
   GLOBAL BASE — LIGHT
   ═══════════════════════════════════════════════════════════ */
QMainWindow, QWidget#RightArea {
    background-color: #f0f4f8;
    color: #1a2e42;
}

QWidget {
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: #1a2e42;
}

/* ═══════════════════════════════════════════════════════════
   SIDEBAR — LIGHT
   ═══════════════════════════════════════════════════════════ */
QFrame#Sidebar {
    background-color: #ffffff;
    border-right: 1px solid #d0dde8;
}

QLabel#LogoText {
    color: #0e6a9a;
    font-size: 17px;
    font-weight: bold;
    font-family: Georgia, serif;
    letter-spacing: 1px;
}

QLabel#NavSectionLabel {
    color: #8aaccc;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    padding-left: 8px;
}

QLabel#VersionLabel {
    color: #aabbd0;
    font-size: 9px;
    padding-left: 8px;
}

QPushButton#NavButton {
    text-align: left;
    padding: 0px 18px;
    font-size: 13px;
    font-weight: 500;
    color: #5a7a9a;
    background-color: transparent;
    border: none;
    border-radius: 0px;
    border-left: 3px solid transparent;
}

QPushButton#NavButton:hover {
    background-color: #eef4fa;
    color: #1a2e42;
    border-left: 3px solid #4aaad0;
}

QPushButton#NavButton[active=true] {
    background-color: #e0f0fa;
    color: #0e6a9a;
    border-left: 3px solid #0e6a9a;
    font-weight: bold;
}

QFrame#Divider {
    background-color: #d0dde8;
    max-height: 1px;
}

QFrame#LogoFrame {
    background-color: #ffffff;
    border-bottom: 1px solid #d8e8f0;
}

/* ═══════════════════════════════════════════════════════════
   TITLE BAR — LIGHT
   ═══════════════════════════════════════════════════════════ */
QFrame#TitleBar {
    background-color: #ffffff;
    border-bottom: 0px;
}

QFrame#TitleSeparator {
    background-color: #d0dde8;
}

QLabel#PageTitle {
    color: #1a2e42;
    font-family: Georgia, serif;
    font-size: 18px;
    font-weight: bold;
}

QLabel#PageSubtitle {
    color: #5a8aaa;
    font-size: 11px;
}

QLabel#StatusPill {
    color: #0a7a55;
    background-color: #d0f5e8;
    border: 1px solid #0a7a55;
    border-radius: 12px;
    padding: 4px 14px;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
}

QPushButton#ThemeToggleBtn {
    background-color: #eef4fa;
    color: #2a6a9a;
    border: 1px solid #c0d8ea;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton#ThemeToggleBtn:hover {
    background-color: #ddeef8;
    border-color: #4aaad0;
}

/* ═══════════════════════════════════════════════════════════
   PAGE STACK — LIGHT
   ═══════════════════════════════════════════════════════════ */
QStackedWidget#PageStack {
    background-color: #f0f4f8;
}

/* ═══════════════════════════════════════════════════════════
   CARDS — LIGHT
   ═══════════════════════════════════════════════════════════ */
QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #d0dde8;
    border-radius: 12px;
    padding: 4px;
}

QFrame#CardAccent {
    background-color: #ffffff;
    border: 1px solid #0e6a9a;
    border-radius: 12px;
}

QFrame#StatCard {
    background-color: #ffffff;
    border: 1px solid #d0dde8;
    border-radius: 10px;
}

QLabel#CardTitle {
    color: #2a7aaa;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1.5px;
}

QLabel#CardValue {
    color: #0e6a9a;
    font-size: 32px;
    font-weight: bold;
    font-family: Georgia, serif;
}

QLabel#CardSubValue {
    color: #5a8aaa;
    font-size: 11px;
}

/* ═══════════════════════════════════════════════════════════
   SECTION HEADERS — LIGHT
   ═══════════════════════════════════════════════════════════ */
QLabel#SectionHeader {
    color: #1a2e42;
    font-size: 15px;
    font-weight: bold;
    font-family: Georgia, serif;
}

QLabel#SectionSubHeader {
    color: #5a8aaa;
    font-size: 11px;
}

QLabel#FieldLabel {
    color: #2a6a9a;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

/* ═══════════════════════════════════════════════════════════
   INPUT CONTROLS — LIGHT
   ═══════════════════════════════════════════════════════════ */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #f8fbfd;
    border: 1px solid #c0d5e8;
    border-radius: 8px;
    padding: 10px 14px;
    color: #1a2e42;
    font-size: 13px;
    selection-background-color: #b0d8f0;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #0e6a9a;
    background-color: #f0f8ff;
}

QLineEdit:disabled {
    background-color: #edf2f7;
    color: #8aaccc;
    border-color: #d0dde8;
}

QComboBox {
    background-color: #f8fbfd;
    border: 1px solid #c0d5e8;
    border-radius: 8px;
    padding: 10px 14px;
    color: #1a2e42;
    font-size: 13px;
    min-width: 140px;
}

QComboBox:focus {
    border: 1px solid #0e6a9a;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #c0d5e8;
    color: #1a2e42;
    selection-background-color: #c8e8f8;
    outline: none;
}

/* ═══════════════════════════════════════════════════════════
   BUTTONS — LIGHT
   ═══════════════════════════════════════════════════════════ */
QPushButton#PrimaryBtn {
    background-color: #0e6a9a;
    color: #ffffff;
    border: 1px solid #0e6a9a;
    border-radius: 9px;
    padding: 12px 28px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton#PrimaryBtn:hover {
    background-color: #1280b8;
    border-color: #1280b8;
}

QPushButton#PrimaryBtn:pressed {
    background-color: #0a5080;
}

QPushButton#PrimaryBtn:disabled {
    background-color: #d0dde8;
    color: #8aaccc;
    border-color: #c0d0e0;
}

QPushButton#SecondaryBtn {
    background-color: transparent;
    color: #0e6a9a;
    border: 1px solid #0e6a9a;
    border-radius: 9px;
    padding: 11px 24px;
    font-size: 13px;
}

QPushButton#SecondaryBtn:hover {
    background-color: #e0f0fa;
}

QPushButton#DangerBtn {
    background-color: #fff0f0;
    color: #c0392b;
    border: 1px solid #c0392b;
    border-radius: 9px;
    padding: 11px 24px;
    font-size: 13px;
}

QPushButton#DangerBtn:hover {
    background-color: #fce0e0;
}

QPushButton#UploadBtn {
    background-color: #f0f8ff;
    color: #2a7aaa;
    border: 2px dashed #7ab8d8;
    border-radius: 10px;
    padding: 20px;
    font-size: 13px;
}

QPushButton#UploadBtn:hover {
    background-color: #e0f0fa;
    border-color: #0e6a9a;
    color: #0e6a9a;
}

/* ═══════════════════════════════════════════════════════════
   CHECKBOX / RADIO — LIGHT
   ═══════════════════════════════════════════════════════════ */
QCheckBox {
    color: #2a4a6a;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #8aaccf;
    background-color: #f8fbfd;
}

QCheckBox::indicator:checked {
    background-color: #0e6a9a;
    border-color: #0e6a9a;
}

QRadioButton {
    color: #2a4a6a;
    font-size: 13px;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 1px solid #8aaccf;
    background-color: #f8fbfd;
}

QRadioButton::indicator:checked {
    background-color: #0e6a9a;
    border-color: #0e6a9a;
}

/* ═══════════════════════════════════════════════════════════
   PROGRESS BAR — LIGHT
   ═══════════════════════════════════════════════════════════ */
QProgressBar {
    background-color: #e0eef8;
    border: 1px solid #c0d5e8;
    border-radius: 6px;
    height: 10px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0e6a9a, stop:1 #38bdf8);
    border-radius: 5px;
}

/* ═══════════════════════════════════════════════════════════
   LOG PANEL — LIGHT
   ═══════════════════════════════════════════════════════════ */
QPlainTextEdit#LogPanel {
    background-color: #f0f8f0;
    border: 1px solid #c0d8c8;
    border-radius: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    color: #1a5a2a;
    padding: 10px;
}

/* ═══════════════════════════════════════════════════════════
   SCROLL BARS — LIGHT
   ═══════════════════════════════════════════════════════════ */
QScrollBar:vertical {
    background-color: #eef4fa;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #b0cce0;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7aaac8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #eef4fa;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #b0cce0;
    border-radius: 4px;
    min-width: 20px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ═══════════════════════════════════════════════════════════
   IMAGE PREVIEW — LIGHT
   ═══════════════════════════════════════════════════════════ */
QFrame#ImagePreviewFrame {
    background-color: #f0f4f8;
    border: 1px solid #c0d5e8;
    border-radius: 10px;
}

QLabel#ImagePreviewLabel {
    color: #7aaac8;
    font-size: 12px;
}

QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #c8d8e8;
    background-color: #c8d8e8;
}

/* ═══════════════════════════════════════════════════════════
   TABS — LIGHT
   ═══════════════════════════════════════════════════════════ */
QTabWidget::pane {
    border: 1px solid #c8d8e8;
    border-radius: 8px;
    background-color: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background-color: #eef4fa;
    color: #5a8aaa;
    padding: 10px 22px;
    border: 1px solid #c8d8e8;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    font-size: 12px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0e6a9a;
    border-color: #c8d8e8;
}

/* ═══════════════════════════════════════════════════════════
   DASHBOARD — LIGHT
   ═══════════════════════════════════════════════════════════ */
QLabel#DashHeroTitle {
    color: #0e6a9a;
    font-size: 28px;
    font-weight: bold;
    font-family: Georgia, serif;
}

QLabel#DashHeroSubtitle {
    color: #5a8aaa;
    font-size: 13px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QToolTip {
    background-color: #ffffff;
    color: #1a2e42;
    border: 1px solid #c0d5e8;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""
