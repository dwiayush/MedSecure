"""
receiver_page.py — Receiver Panel (Extract & Decrypt)
======================================================
UI for the full receiver workflow:
  - Upload stego image
  - Auto-detect mode and AES type from payload header
  - Optional passphrase input (if sender used custom key)
  - Progress tracking
  - Log output
  - Display recovered image or text
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QLineEdit, QPlainTextEdit, QTextEdit, QProgressBar, QFileDialog,
    QScrollArea, QSizePolicy, QMessageBox, QApplication,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPixmap, QImage

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.ui.sender_page import ImagePreviewBox


class DecryptionWorker(QObject):
    """Background worker for decryption — keeps UI responsive."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, params: dict):
        super().__init__()
        self.params = params

    def run(self):
        try:
            from app.controllers.crypto_controller import extract_and_decrypt
            p = self.params
            result = extract_and_decrypt(
                stego_image_path=p["stego_path"],
                output_path=p.get("output_path", ""),
                passphrase=p.get("passphrase", ""),
                progress_cb=lambda pct, msg: self.progress.emit(pct, msg),
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ReceiverPage(QWidget):
    """
    Receiver Panel — UI for extraction and decryption of stego images.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stego_path = ""
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

        # ── Info Banner ───────────────────────────────────────────────────────
        banner = QFrame()
        banner.setObjectName("Card")
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(20, 14, 20, 14)
        banner_layout.setSpacing(16)

        info_icon = QLabel("ℹ")
        info_icon.setFont(QFont("Segoe UI Emoji", 20))
        info_icon.setFixedWidth(32)
        banner_layout.addWidget(info_icon)

        info_text = QLabel(
            "Upload a MedSecure stego image. The system will automatically detect "
            "the encryption parameters (AES type, mode) from the embedded payload header. "
            "If a custom passphrase was used during encryption, enter it below."
        )
        info_text.setObjectName("SectionSubHeader")
        info_text.setWordWrap(True)
        info_text.setFont(QFont("Segoe UI", 12))
        banner_layout.addWidget(info_text, 1)
        layout.addWidget(banner)

        # ── Main Content Row ──────────────────────────────────────────────────
        main_row = QHBoxLayout()
        main_row.setSpacing(16)

        # ── Left: Controls ────────────────────────────────────────────────────
        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        # Upload card
        upload_card = QFrame()
        upload_card.setObjectName("Card")
        upload_layout = QVBoxLayout(upload_card)
        upload_layout.setContentsMargins(20, 18, 20, 18)
        upload_layout.setSpacing(14)

        upload_hdr = QLabel("Stego Image Input")
        upload_hdr.setObjectName("SectionHeader")
        upload_hdr.setFont(QFont("Georgia", 13, QFont.Bold))
        upload_layout.addWidget(upload_hdr)

        sep1 = QFrame(); sep1.setFrameShape(QFrame.HLine)
        upload_layout.addWidget(sep1)

        stego_lbl = QLabel("STEGO IMAGE")
        stego_lbl.setObjectName("FieldLabel")
        upload_layout.addWidget(stego_lbl)

        self.stego_upload_btn = QPushButton("⬇  Upload Stego Image (PNG)")
        self.stego_upload_btn.setObjectName("UploadBtn")
        self.stego_upload_btn.setFixedHeight(70)
        self.stego_upload_btn.clicked.connect(self._pick_stego_image)
        upload_layout.addWidget(self.stego_upload_btn)

        self.stego_path_lbl = QLabel("No stego image selected")
        self.stego_path_lbl.setObjectName("CardSubValue")
        upload_layout.addWidget(self.stego_path_lbl)

        left_col.addWidget(upload_card)

        # Key input card
        key_card = QFrame()
        key_card.setObjectName("Card")
        key_layout = QVBoxLayout(key_card)
        key_layout.setContentsMargins(20, 18, 20, 18)
        key_layout.setSpacing(12)

        key_hdr = QLabel("Key Configuration")
        key_hdr.setObjectName("SectionHeader")
        key_hdr.setFont(QFont("Georgia", 13, QFont.Bold))
        key_layout.addWidget(key_hdr)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        key_layout.addWidget(sep2)

        key_info_lbl = QLabel(
            "If the sender used an auto-generated key, leave passphrase empty.\n"
            "If a custom passphrase was used, enter the same passphrase here."
        )
        key_info_lbl.setObjectName("SectionSubHeader")
        key_info_lbl.setWordWrap(True)
        key_info_lbl.setFont(QFont("Segoe UI", 11))
        key_layout.addWidget(key_info_lbl)

        pass_lbl = QLabel("PASSPHRASE (IF CUSTOM KEY WAS USED)")
        pass_lbl.setObjectName("FieldLabel")
        key_layout.addWidget(pass_lbl)

        pass_row = QHBoxLayout()
        self.passphrase_input = QLineEdit()
        self.passphrase_input.setPlaceholderText("Enter decryption passphrase (leave empty if auto-key)...")
        self.passphrase_input.setEchoMode(QLineEdit.Password)
        pass_row.addWidget(self.passphrase_input)

        self.show_pass_btn = QPushButton("👁")
        self.show_pass_btn.setObjectName("SecondaryBtn")
        self.show_pass_btn.setFixedSize(40, 40)
        self.show_pass_btn.setCheckable(True)
        self.show_pass_btn.toggled.connect(self._toggle_passphrase_visibility)
        pass_row.addWidget(self.show_pass_btn)
        key_layout.addLayout(pass_row)

        out_lbl = QLabel("OUTPUT PATH (FOR RECOVERED IMAGE)")
        out_lbl.setObjectName("FieldLabel")
        key_layout.addWidget(out_lbl)

        out_row = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Output path for recovered image (auto-set)...")
        out_row.addWidget(self.output_path_input)

        out_browse = QPushButton("Browse")
        out_browse.setObjectName("SecondaryBtn")
        out_browse.setFixedWidth(90)
        out_browse.clicked.connect(self._pick_output_path)
        out_row.addWidget(out_browse)
        key_layout.addLayout(out_row)

        left_col.addWidget(key_card)

        # Progress + Log card
        progress_card = QFrame()
        progress_card.setObjectName("Card")
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(20, 18, 20, 18)
        progress_layout.setSpacing(10)

        prog_hdr_row = QHBoxLayout()
        prog_hdr = QLabel("Decryption Progress")
        prog_hdr.setObjectName("SectionHeader")
        prog_hdr.setFont(QFont("Georgia", 12, QFont.Bold))
        prog_hdr_row.addWidget(prog_hdr)
        prog_hdr_row.addStretch()
        self.status_lbl = QLabel("Ready")
        self.status_lbl.setObjectName("CardSubValue")
        prog_hdr_row.addWidget(self.status_lbl)
        progress_layout.addLayout(prog_hdr_row)

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
        self.log_panel.setFixedHeight(120)
        self.log_panel.setPlaceholderText("Decryption log appears here...")
        progress_layout.addWidget(self.log_panel)

        left_col.addWidget(progress_card)

        # Action buttons
        btn_row = QHBoxLayout()
        self.clear_btn = QPushButton("🗑  Clear")
        self.clear_btn.setObjectName("SecondaryBtn")
        self.clear_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()

        self.decrypt_btn = QPushButton("🔓  Extract & Decrypt")
        self.decrypt_btn.setObjectName("PrimaryBtn")
        self.decrypt_btn.setFixedHeight(46)
        self.decrypt_btn.setMinimumWidth(200)
        self.decrypt_btn.clicked.connect(self._start_decryption)
        btn_row.addWidget(self.decrypt_btn)

        left_col.addLayout(btn_row)

        main_row.addLayout(left_col, 45)

        # ── Right: Previews ───────────────────────────────────────────────────
        right_col = QVBoxLayout()
        right_col.setSpacing(12)

        self.stego_preview = ImagePreviewBox("Stego Image Input", "Upload stego image →")
        right_col.addWidget(self.stego_preview, 1)

        # Recovered content card
        recovered_card = QFrame()
        recovered_card.setObjectName("Card")
        recovered_layout = QVBoxLayout(recovered_card)
        recovered_layout.setContentsMargins(16, 14, 16, 14)
        recovered_layout.setSpacing(10)

        rec_hdr = QLabel("RECOVERED CONTENT")
        rec_hdr.setObjectName("CardTitle")
        recovered_layout.addWidget(rec_hdr)

        # Recovered image
        self.recovered_image_preview = ImagePreviewBox(
            "Recovered Image", "Decrypted image appears here after extraction"
        )
        self.recovered_image_preview.setMinimumHeight(160)
        recovered_layout.addWidget(self.recovered_image_preview, 1)

        # Recovered text
        self.recovered_text_label = QLabel("DECRYPTED TEXT")
        self.recovered_text_label.setObjectName("FieldLabel")
        self.recovered_text_label.setVisible(False)
        recovered_layout.addWidget(self.recovered_text_label)

        self.recovered_text_area = QTextEdit()
        self.recovered_text_area.setReadOnly(True)
        self.recovered_text_area.setPlaceholderText("Decrypted text appears here...")
        self.recovered_text_area.setMinimumHeight(120)
        self.recovered_text_area.setVisible(False)
        recovered_layout.addWidget(self.recovered_text_area)

        # Metadata display
        self.metadata_lbl = QLabel("")
        self.metadata_lbl.setObjectName("CardSubValue")
        self.metadata_lbl.setWordWrap(True)
        self.metadata_lbl.setFont(QFont("Consolas", 10))
        recovered_layout.addWidget(self.metadata_lbl)

        # Save recovered text button
        self.save_text_btn = QPushButton("💾  Save Decrypted Text")
        self.save_text_btn.setObjectName("SecondaryBtn")
        self.save_text_btn.setVisible(False)
        self.save_text_btn.clicked.connect(self._save_recovered_text)
        recovered_layout.addWidget(self.save_text_btn)

        right_col.addWidget(recovered_card, 2)

        main_row.addLayout(right_col, 55)
        layout.addLayout(main_row)

        scroll.setWidget(content)
        outer.addWidget(scroll)

    # ── Event Handlers ────────────────────────────────────────────────────────

    def _pick_stego_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Stego Image", "",
            "PNG Images (*.png);;All Images (*.png *.jpg *.bmp)"
        )
        if path:
            self._stego_path = path
            self.stego_path_lbl.setText(os.path.basename(path))
            self.stego_upload_btn.setText(f"✔  {os.path.basename(path)}")
            self.stego_preview.set_image(path)
            # Auto-set output path
            base = os.path.splitext(path)[0]
            self.output_path_input.setText(base + "_recovered.png")

    def _pick_output_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Recovered Image", "recovered_image.png",
            "PNG Image (*.png);;JPEG Image (*.jpg)"
        )
        if path:
            self.output_path_input.setText(path)

    def _toggle_passphrase_visibility(self, checked: bool):
        self.passphrase_input.setEchoMode(
            QLineEdit.Normal if checked else QLineEdit.Password
        )
        self.show_pass_btn.setText("🙈" if checked else "👁")

    def _log(self, msg: str):
        self.log_panel.appendPlainText(msg)

    def _clear_all(self):
        self._stego_path = ""
        self.stego_upload_btn.setText("⬇  Upload Stego Image (PNG)")
        self.stego_path_lbl.setText("No stego image selected")
        self.passphrase_input.clear()
        self.output_path_input.clear()
        self.progress_bar.setValue(0)
        self.status_lbl.setText("Ready")
        self.log_panel.clear()
        self.stego_preview.clear("Upload stego image →")
        self.recovered_image_preview.clear("Decrypted image appears here after extraction")
        self.recovered_text_area.clear()
        self.recovered_text_area.setVisible(False)
        self.recovered_text_label.setVisible(False)
        self.save_text_btn.setVisible(False)
        self.metadata_lbl.clear()

    def _start_decryption(self):
        if not self._stego_path:
            self._show_error("Please upload a stego image.")
            return

        output_path = self.output_path_input.text().strip()
        if not output_path:
            output_path = os.path.join(os.path.dirname(self._stego_path), "recovered.png")
            self.output_path_input.setText(output_path)

        params = {
            "stego_path": self._stego_path,
            "output_path": output_path,
            "passphrase": self.passphrase_input.text(),
        }

        self.decrypt_btn.setEnabled(False)
        self.decrypt_btn.setText("⏳  Decrypting...")
        self.progress_bar.setValue(0)
        self.log_panel.clear()
        self.recovered_text_area.setVisible(False)
        self.recovered_text_label.setVisible(False)
        self.save_text_btn.setVisible(False)
        self.metadata_lbl.clear()

        self._log("[→] Starting LSB payload extraction...")
        self._log(f"[→] Stego image: {os.path.basename(self._stego_path)}")

        self._worker_thread = QThread()
        self._worker = DecryptionWorker(params)
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
        self.decrypt_btn.setEnabled(True)
        self.decrypt_btn.setText("🔓  Extract & Decrypt")
        self.progress_bar.setValue(100)
        self.status_lbl.setText("Complete ✔")

        self._log("")
        self._log("═" * 50)
        self._log("[✔] DECRYPTION COMPLETE")
        self._log(f"    Mode:       {result['mode']}")
        self._log(f"    AES Type:   {result['aes_type']}")
        self._log(f"    Key Mode:   {result['key_mode']}")
        self._log(f"    Data Size:  {result['plaintext_size']:,} bytes")
        self._log("═" * 50)

        # Show metadata
        self.metadata_lbl.setText(
            f"Mode: {result['mode']}  ·  AES: {result['aes_type']}  ·  "
            f"Key: {result['key_mode']}  ·  Size: {result['plaintext_size']:,} bytes"
        )

        if result["mode"] == "Text":
            # Show recovered text
            self.recovered_image_preview.setVisible(False)
            self.recovered_text_label.setVisible(True)
            self.recovered_text_area.setVisible(True)
            self.save_text_btn.setVisible(True)
            self.recovered_text_area.setPlainText(result.get("text", ""))
            self._log(f"[✔] Text recovered: {len(result.get('text',''))} characters")

        else:
            # Show recovered image
            self.recovered_image_preview.setVisible(True)
            self.recovered_text_area.setVisible(False)
            self.recovered_text_label.setVisible(False)
            self.save_text_btn.setVisible(False)

            img_data = result.get("image_bytes")
            if img_data:
                self.recovered_image_preview.set_image_from_bytes(
                    img_data, f"Recovered  ·  {result['plaintext_size']:,} bytes"
                )

            saved_path = result.get("recovered_image_path", "")
            if saved_path:
                self._log(f"[✔] Image saved to: {saved_path}")

        QMessageBox.information(
            self, "Decryption Successful",
            f"✔ Data successfully extracted and decrypted!\n\n"
            f"Mode:      {result['mode']}\n"
            f"AES Type:  {result['aes_type']}\n"
            f"Data Size: {result['plaintext_size']:,} bytes\n"
            f"Integrity: SHA-256 verified ✔"
        )

    def _on_error(self, error_msg: str):
        self._worker_thread.quit()
        self._worker_thread.wait()
        self.decrypt_btn.setEnabled(True)
        self.decrypt_btn.setText("🔓  Extract & Decrypt")
        self.progress_bar.setValue(0)
        self.status_lbl.setText("Error ✖")
        self._log(f"[✖] ERROR: {error_msg}")
        self._show_error(f"Decryption failed:\n\n{error_msg}")

    def _save_recovered_text(self):
        text = self.recovered_text_area.toPlainText()
        if not text:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Recovered Text", "recovered_report.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            QMessageBox.information(self, "Saved", f"Text saved to:\n{path}")

    def _show_error(self, msg: str):
        QMessageBox.critical(self, "MedSecure — Error", msg)
