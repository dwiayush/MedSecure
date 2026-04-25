"""
sender_page.py — Sender Panel (Encrypt & Embed)
================================================
UI for the full sender workflow:
  - Mode toggle: Image / Text
  - AES type selection
  - Key mode: Auto / Custom
  - Image upload (data + cover)
  - Text input
  - Progress tracking
  - Log output
  - Image preview panels
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QCheckBox,
    QProgressBar, QFileDialog, QScrollArea, QSizePolicy, QButtonGroup,
    QRadioButton, QMessageBox, QApplication,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPixmap, QImage

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class EncryptionWorker(QObject):
    """
    Worker object that runs encryption in a background QThread
    so the UI remains responsive during heavy crypto operations.
    """
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, params: dict):
        super().__init__()
        self.params = params

    def run(self):
        try:
            from app.controllers.crypto_controller import (
                encrypt_and_embed_image, encrypt_and_embed_text
            )
            p = self.params
            if p["mode"] == "image":
                result = encrypt_and_embed_image(
                    data_image_path=p["data_path"],
                    cover_image_path=p["cover_path"],
                    output_stego_path=p["output_path"],
                    aes_type=p["aes_type"],
                    use_custom_key=p["use_custom_key"],
                    passphrase=p.get("passphrase", ""),
                    compress=p.get("compress", True),
                    progress_cb=lambda pct, msg: self.progress.emit(pct, msg),
                )
            else:
                result = encrypt_and_embed_text(
                    text=p["text"],
                    cover_image_path=p["cover_path"],
                    output_stego_path=p["output_path"],
                    aes_type=p["aes_type"],
                    use_custom_key=p["use_custom_key"],
                    passphrase=p.get("passphrase", ""),
                    progress_cb=lambda pct, msg: self.progress.emit(pct, msg),
                )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ImagePreviewBox(QFrame):
    """Reusable image preview widget with label and dimensions readout."""

    def __init__(self, title: str, placeholder: str = "No image loaded", parent=None):
        super().__init__(parent)
        self.setObjectName("ImagePreviewFrame")
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        title_lbl = QLabel(title.upper())
        title_lbl.setObjectName("CardTitle")
        title_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        layout.addWidget(title_lbl)

        self.image_label = QLabel(placeholder)
        self.image_label.setObjectName("ImagePreviewLabel")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(160)
        self.image_label.setWordWrap(True)
        self.image_label.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.image_label, 1)

        self.info_label = QLabel("")
        self.info_label.setObjectName("CardSubValue")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

    def set_image(self, path: str):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.image_label.setText(f"Cannot preview:\n{os.path.basename(path)}")
            return
        scaled = pixmap.scaled(
            self.image_label.width() or 320,
            self.image_label.height() or 180,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)
        size = os.path.getsize(path)
        self.info_label.setText(
            f"{pixmap.width()}×{pixmap.height()} px  ·  {size / 1024:.1f} KB  ·  {os.path.basename(path)}"
        )

    def set_image_from_bytes(self, data: bytes, label: str = ""):
        qimg = QImage.fromData(data)
        if qimg.isNull():
            self.image_label.setText("Cannot preview image")
            return
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(
            self.image_label.width() or 320,
            self.image_label.height() or 180,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)
        if label:
            self.info_label.setText(label)

    def clear(self, placeholder: str = "No image loaded"):
        self.image_label.clear()
        self.image_label.setText(placeholder)
        self.info_label.setText("")


class SenderPage(QWidget):
    """
    Sender Panel — full UI for encryption + steganography embedding.
    """

    navigate_to_receiver = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data_image_path = ""
        self._cover_image_path = ""
        self._output_path = ""
        self._worker_thread = None
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(20)

        # ── Top Control Row ───────────────────────────────────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # Mode toggle card
        mode_card = QFrame()
        mode_card.setObjectName("Card")
        mode_layout = QVBoxLayout(mode_card)
        mode_layout.setContentsMargins(18, 14, 18, 14)
        mode_layout.setSpacing(8)

        mode_title = QLabel("ENCRYPTION MODE")
        mode_title.setObjectName("CardTitle")
        mode_layout.addWidget(mode_title)

        mode_btn_row = QHBoxLayout()
        self.image_mode_btn = QRadioButton("🖼  Image Mode")
        self.text_mode_btn = QRadioButton("📄  Text Mode")
        self.image_mode_btn.setChecked(True)
        self.image_mode_btn.toggled.connect(self._on_mode_change)

        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.image_mode_btn, 0)
        self.mode_group.addButton(self.text_mode_btn, 1)

        mode_btn_row.addWidget(self.image_mode_btn)
        mode_btn_row.addWidget(self.text_mode_btn)
        mode_btn_row.addStretch()
        mode_layout.addLayout(mode_btn_row)
        top_row.addWidget(mode_card, 35)

        # AES selection card
        aes_card = QFrame()
        aes_card.setObjectName("Card")
        aes_layout = QVBoxLayout(aes_card)
        aes_layout.setContentsMargins(18, 14, 18, 14)
        aes_layout.setSpacing(8)

        aes_title = QLabel("AES CIPHER")
        aes_title.setObjectName("CardTitle")
        aes_layout.addWidget(aes_title)

        self.aes_combo = QComboBox()
        self.aes_combo.addItems(["AES-256", "AES-192", "AES-128"])
        self.aes_combo.setCurrentIndex(0)
        self.aes_combo.setToolTip("AES-256 provides 256-bit security (recommended for medical data)")
        aes_layout.addWidget(self.aes_combo)

        self.compress_check = QCheckBox("Compress image before encryption")
        self.compress_check.setChecked(True)
        self.compress_check.setToolTip("Uses lossless PNG compression to reduce payload size")
        aes_layout.addWidget(self.compress_check)

        top_row.addWidget(aes_card, 30)

        # Key mode card
        key_card = QFrame()
        key_card.setObjectName("Card")
        key_layout = QVBoxLayout(key_card)
        key_layout.setContentsMargins(18, 14, 18, 14)
        key_layout.setSpacing(8)

        key_title = QLabel("KEY MODE")
        key_title.setObjectName("CardTitle")
        key_layout.addWidget(key_title)

        self.auto_key_radio = QRadioButton("🔑  Auto-generated key")
        self.custom_key_radio = QRadioButton("✏  Custom passphrase")
        self.auto_key_radio.setChecked(True)
        self.auto_key_radio.toggled.connect(self._on_key_mode_change)

        self.key_mode_group = QButtonGroup(self)
        self.key_mode_group.addButton(self.auto_key_radio, 0)
        self.key_mode_group.addButton(self.custom_key_radio, 1)

        key_layout.addWidget(self.auto_key_radio)
        key_layout.addWidget(self.custom_key_radio)

        self.passphrase_input = QLineEdit()
        self.passphrase_input.setPlaceholderText("Enter secure passphrase (min 8 chars)...")
        self.passphrase_input.setEchoMode(QLineEdit.Password)
        self.passphrase_input.setEnabled(False)
        key_layout.addWidget(self.passphrase_input)

        top_row.addWidget(key_card, 35)
        layout.addLayout(top_row)

        # ── Middle Row: Input + Previews ──────────────────────────────────────
        middle_row = QHBoxLayout()
        middle_row.setSpacing(16)

        # Left: Input controls
        input_card = QFrame()
        input_card.setObjectName("Card")
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(20, 18, 20, 18)
        input_layout.setSpacing(14)

        input_hdr = QLabel("Input Data")
        input_hdr.setObjectName("SectionHeader")
        input_hdr.setFont(QFont("Georgia", 13, QFont.Bold))
        input_layout.addWidget(input_hdr)

        sep1 = QFrame(); sep1.setFrameShape(QFrame.HLine)
        input_layout.addWidget(sep1)

        # Image mode inputs
        self.image_inputs_widget = QWidget()
        img_inputs_layout = QVBoxLayout(self.image_inputs_widget)
        img_inputs_layout.setContentsMargins(0, 0, 0, 0)
        img_inputs_layout.setSpacing(12)

        data_lbl = QLabel("DATA IMAGE")
        data_lbl.setObjectName("FieldLabel")
        img_inputs_layout.addWidget(data_lbl)

        self.data_image_btn = QPushButton("⬆  Upload Medical Image (PNG, JPG, BMP, TIFF)")
        self.data_image_btn.setObjectName("UploadBtn")
        self.data_image_btn.setFixedHeight(60)
        self.data_image_btn.clicked.connect(self._pick_data_image)
        img_inputs_layout.addWidget(self.data_image_btn)

        self.data_image_path_lbl = QLabel("No file selected")
        self.data_image_path_lbl.setObjectName("CardSubValue")
        img_inputs_layout.addWidget(self.data_image_path_lbl)

        input_layout.addWidget(self.image_inputs_widget)

        # Text mode input
        self.text_inputs_widget = QWidget()
        text_inputs_layout = QVBoxLayout(self.text_inputs_widget)
        text_inputs_layout.setContentsMargins(0, 0, 0, 0)
        text_inputs_layout.setSpacing(12)

        text_lbl = QLabel("PATIENT DATA / REPORT TEXT")
        text_lbl.setObjectName("FieldLabel")
        text_inputs_layout.addWidget(text_lbl)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Enter medical report, patient data, or any text to encrypt securely...\n\n"
            "Example:\nPatient: John Doe | DOB: 01/01/1980\n"
            "Diagnosis: Type-2 Diabetes\nPrescription: Metformin 500mg..."
        )
        self.text_input.setMinimumHeight(140)
        text_inputs_layout.addWidget(self.text_input)

        char_row = QHBoxLayout()
        self.char_count_lbl = QLabel("0 characters")
        self.char_count_lbl.setObjectName("CardSubValue")
        self.text_input.textChanged.connect(self._update_char_count)
        char_row.addWidget(self.char_count_lbl)
        char_row.addStretch()
        text_inputs_layout.addLayout(char_row)

        self.text_inputs_widget.setVisible(False)
        input_layout.addWidget(self.text_inputs_widget)

        # Cover image (always shown)
        cover_lbl = QLabel("COVER IMAGE (CARRIER)")
        cover_lbl.setObjectName("FieldLabel")
        input_layout.addWidget(cover_lbl)

        self.cover_image_btn = QPushButton("🖼  Upload Cover Image (PNG recommended, >800×600)")
        self.cover_image_btn.setObjectName("UploadBtn")
        self.cover_image_btn.setFixedHeight(60)
        self.cover_image_btn.clicked.connect(self._pick_cover_image)
        input_layout.addWidget(self.cover_image_btn)

        self.cover_path_lbl = QLabel("No cover image selected")
        self.cover_path_lbl.setObjectName("CardSubValue")
        input_layout.addWidget(self.cover_path_lbl)

        # Capacity indicator
        self.capacity_lbl = QLabel("")
        self.capacity_lbl.setObjectName("CardSubValue")
        self.capacity_lbl.setWordWrap(True)
        input_layout.addWidget(self.capacity_lbl)

        input_layout.addStretch()
        middle_row.addWidget(input_card, 40)

        # Right: Image previews
        preview_col = QVBoxLayout()
        preview_col.setSpacing(12)

        self.data_preview = ImagePreviewBox("Medical Image", "Upload medical image →")
        self.cover_preview = ImagePreviewBox("Cover Image", "Upload cover image →")
        self.stego_preview = ImagePreviewBox("Stego Output", "Stego image appears here after encryption")

        preview_col.addWidget(self.data_preview, 1)
        preview_col.addWidget(self.cover_preview, 1)
        preview_col.addWidget(self.stego_preview, 1)

        middle_row.addLayout(preview_col, 60)
        layout.addLayout(middle_row)

        # ── Output Path ───────────────────────────────────────────────────────
        out_card = QFrame()
        out_card.setObjectName("Card")
        out_layout = QHBoxLayout(out_card)
        out_layout.setContentsMargins(18, 14, 18, 14)
        out_layout.setSpacing(12)

        out_lbl = QLabel("OUTPUT")
        out_lbl.setObjectName("FieldLabel")
        out_lbl.setFixedWidth(64)
        out_layout.addWidget(out_lbl)

        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Output stego image path (auto-set, or browse)...")
        out_layout.addWidget(self.output_path_input, 1)

        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("SecondaryBtn")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._pick_output_path)
        out_layout.addWidget(browse_btn)

        layout.addWidget(out_card)

        # ── Progress & Logs ───────────────────────────────────────────────────
        progress_card = QFrame()
        progress_card.setObjectName("Card")
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(18, 14, 18, 14)
        progress_layout.setSpacing(10)

        prog_header_row = QHBoxLayout()
        prog_hdr = QLabel("Encryption Progress")
        prog_hdr.setObjectName("SectionHeader")
        prog_hdr.setFont(QFont("Georgia", 12, QFont.Bold))
        prog_header_row.addWidget(prog_hdr)
        prog_header_row.addStretch()

        self.status_lbl = QLabel("Ready")
        self.status_lbl.setObjectName("CardSubValue")
        prog_header_row.addWidget(self.status_lbl)
        progress_layout.addLayout(prog_header_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)
        progress_layout.addWidget(self.progress_bar)

        log_lbl = QLabel("OPERATION LOG")
        log_lbl.setObjectName("FieldLabel")
        progress_layout.addWidget(log_lbl)

        self.log_panel = QPlainTextEdit()
        self.log_panel.setObjectName("LogPanel")
        self.log_panel.setReadOnly(True)
        self.log_panel.setFixedHeight(110)
        self.log_panel.setPlaceholderText("Encryption log appears here...")
        progress_layout.addWidget(self.log_panel)

        layout.addWidget(progress_card)

        # ── Action Buttons ────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.clear_btn = QPushButton("🗑  Clear All")
        self.clear_btn.setObjectName("SecondaryBtn")
        self.clear_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(self.clear_btn)

        btn_row.addStretch()

        self.encrypt_btn = QPushButton("🔒  Encrypt & Embed")
        self.encrypt_btn.setObjectName("PrimaryBtn")
        self.encrypt_btn.setFixedHeight(46)
        self.encrypt_btn.setMinimumWidth(200)
        self.encrypt_btn.clicked.connect(self._start_encryption)
        btn_row.addWidget(self.encrypt_btn)

        layout.addLayout(btn_row)

        scroll.setWidget(content)
        outer.addWidget(scroll)

    # ── Event Handlers ────────────────────────────────────────────────────────

    def _on_mode_change(self, image_mode: bool):
        self.image_inputs_widget.setVisible(image_mode)
        self.text_inputs_widget.setVisible(not image_mode)
        self.data_preview.clear("Upload medical image →" if image_mode else "Text mode — no image preview")

    def _on_key_mode_change(self, auto: bool):
        self.passphrase_input.setEnabled(not auto)
        if auto:
            self.passphrase_input.clear()

    def _pick_data_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Medical Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.tif)"
        )
        if path:
            self._data_image_path = path
            self.data_image_path_lbl.setText(os.path.basename(path))
            self.data_image_btn.setText(f"✔  {os.path.basename(path)}")
            self.data_preview.set_image(path)
            self._update_output_default(path)

    def _pick_cover_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Cover Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self._cover_image_path = path
            self.cover_path_lbl.setText(os.path.basename(path))
            self.cover_image_btn.setText(f"✔  {os.path.basename(path)}")
            self.cover_preview.set_image(path)
            self._update_capacity_info()

    def _pick_output_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Stego Image", "stego_output.png",
            "PNG Image (*.png)"
        )
        if path:
            self._output_path = path
            self.output_path_input.setText(path)

    def _update_output_default(self, data_path: str):
        base = os.path.splitext(data_path)[0]
        default_out = base + "_stego.png"
        self.output_path_input.setText(default_out)
        self._output_path = default_out

    def _update_capacity_info(self):
        if not self._cover_image_path:
            return
        try:
            from app.core.compression import calculate_steganography_capacity, get_image_info
            cap = calculate_steganography_capacity(self._cover_image_path)
            info = get_image_info(self._cover_image_path)
            self.capacity_lbl.setText(
                f"  Cover capacity: {cap:,} bytes ({cap/1024:.1f} KB)  ·  "
                f"{info['width']}×{info['height']} px"
            )
        except Exception as e:
            self.capacity_lbl.setText(f"  Cannot read cover image: {e}")

    def _update_char_count(self):
        n = len(self.text_input.toPlainText())
        self.char_count_lbl.setText(f"{n:,} characters  ≈  {n} bytes")

    def _log(self, msg: str):
        self.log_panel.appendPlainText(msg)

    def _clear_all(self):
        self._data_image_path = ""
        self._cover_image_path = ""
        self._output_path = ""
        self.data_image_btn.setText("⬆  Upload Medical Image (PNG, JPG, BMP, TIFF)")
        self.cover_image_btn.setText("🖼  Upload Cover Image (PNG recommended, >800×600)")
        self.data_image_path_lbl.setText("No file selected")
        self.cover_path_lbl.setText("No cover image selected")
        self.output_path_input.clear()
        self.passphrase_input.clear()
        self.text_input.clear()
        self.progress_bar.setValue(0)
        self.status_lbl.setText("Ready")
        self.log_panel.clear()
        self.data_preview.clear("Upload medical image →")
        self.cover_preview.clear("Upload cover image →")
        self.stego_preview.clear("Stego image appears here after encryption")
        self.capacity_lbl.clear()

    def _start_encryption(self):
        # ── Validation ────────────────────────────────────────────────────────
        mode = "image" if self.image_mode_btn.isChecked() else "text"
        aes_type = self.aes_combo.currentText()
        use_custom = self.custom_key_radio.isChecked()
        passphrase = self.passphrase_input.text()

        if mode == "image" and not self._data_image_path:
            self._show_error("Please upload a medical image to encrypt.")
            return

        if mode == "text" and not self.text_input.toPlainText().strip():
            self._show_error("Please enter text to encrypt.")
            return

        if not self._cover_image_path:
            self._show_error("Please upload a cover (carrier) image.")
            return

        if use_custom:
            from app.core.aes_module import validate_custom_key
            valid, msg = validate_custom_key(passphrase, aes_type)
            if not valid:
                self._show_error(f"Key validation failed:\n{msg}")
                return

        output_path = self.output_path_input.text().strip()
        if not output_path:
            output_path = os.path.join(os.path.dirname(self._cover_image_path), "stego_output.png")
            self.output_path_input.setText(output_path)

        # ── Build params ──────────────────────────────────────────────────────
        params = {
            "mode": mode,
            "cover_path": self._cover_image_path,
            "output_path": output_path,
            "aes_type": aes_type,
            "use_custom_key": use_custom,
            "passphrase": passphrase,
        }
        if mode == "image":
            params["data_path"] = self._data_image_path
            params["compress"] = self.compress_check.isChecked()
        else:
            params["text"] = self.text_input.toPlainText()

        # ── Start worker ──────────────────────────────────────────────────────
        self.encrypt_btn.setEnabled(False)
        self.encrypt_btn.setText("⏳  Encrypting...")
        self.progress_bar.setValue(0)
        self.log_panel.clear()
        self._log(f"[→] Starting {aes_type} encryption in {mode.upper()} mode...")
        if use_custom:
            self._log(f"[→] Custom passphrase key mode — PBKDF2-HMAC-SHA256 derivation.")
        else:
            self._log(f"[→] Auto-generated key mode — os.urandom({16 if aes_type=='AES-128' else (24 if aes_type=='AES-192' else 32)} bytes)")
        self._log(f"[→] ECC curve: SECP384R1 (NIST P-384, 192-bit security)")

        self._worker_thread = QThread()
        self._worker = EncryptionWorker(params)
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker_thread.start()

    def _on_progress(self, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        self.status_lbl.setText(msg.split("]")[-1].strip() if "]" in msg else msg)
        self._log(msg)

    def _on_finished(self, result: dict):
        self._worker_thread.quit()
        self._worker_thread.wait()
        self.encrypt_btn.setEnabled(True)
        self.encrypt_btn.setText("🔒  Encrypt & Embed")
        self.progress_bar.setValue(100)
        self.status_lbl.setText("Complete ✔")

        self._log("")
        self._log("═" * 50)
        self._log("[✔] ENCRYPTION COMPLETE")
        self._log(f"    Mode:          {result['mode']}")
        self._log(f"    AES Type:      {result['aes_type']}")
        self._log(f"    Key Mode:      {result['key_mode']}")
        self._log(f"    Plaintext:     {result['plaintext_size']:,} bytes")
        self._log(f"    Ciphertext:    {result['ciphertext_size']:,} bytes")
        self._log(f"    Payload:       {result['payload_size']:,} bytes")
        self._log(f"    Utilization:   {result['utilization_pct']}% of cover capacity")
        self._log(f"    PSNR:          {result['psnr_db']} dB (>50 dB = imperceptible)")
        self._log(f"    Output:        {result['stego_path']}")
        self._log("═" * 50)

        # Show stego image preview
        stego_path = result.get("stego_path", "")
        if stego_path and os.path.exists(stego_path):
            self.stego_preview.set_image(stego_path)
            self._output_path = stego_path

        QMessageBox.information(
            self, "Encryption Successful",
            f"✔ Data encrypted and embedded successfully!\n\n"
            f"AES Type:    {result['aes_type']}\n"
            f"PSNR:        {result['psnr_db']} dB\n"
            f"Utilization: {result['utilization_pct']}%\n\n"
            f"Stego image saved to:\n{result['stego_path']}"
        )

    def _on_error(self, error_msg: str):
        self._worker_thread.quit()
        self._worker_thread.wait()
        self.encrypt_btn.setEnabled(True)
        self.encrypt_btn.setText("🔒  Encrypt & Embed")
        self.progress_bar.setValue(0)
        self.status_lbl.setText("Error ✖")
        self._log(f"[✖] ERROR: {error_msg}")
        self._show_error(f"Encryption failed:\n\n{error_msg}")

    def _show_error(self, msg: str):
        QMessageBox.critical(self, "MedSecure — Error", msg)
