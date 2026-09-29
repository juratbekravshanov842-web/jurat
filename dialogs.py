"""
Dialogs - PySide6 dialog windows for Shartnoma Generator
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QTextEdit,
    QComboBox, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, pyqtSignal
from PySide6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class VerificationDialog(QDialog):
    """Dialog for verifying contract data before generation"""

    data_confirmed = pyqtSignal(bool)

    def __init__(self, contract_data: dict, parent=None):
        """Initialize verification dialog"""
        super().__init__(parent)
        self.setWindowTitle("Ma'lumotlarni tasdiqlash")
        self.setGeometry(200, 200, 700, 600)
        self.contract_data = contract_data
        self.confirmed = False

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Shartnoma ma'lumotlarini tasdiqlang")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Data table
        self.data_table = QTableWidget(0, 2)
        self.data_table.setHorizontalHeaderLabels(["Maydon", "Qiymat"])
        self.data_table.horizontalHeader().setStretchLastSection(True)

        # Populate table
        for key, value in self.contract_data.items():
            row = self.data_table.rowCount()
            self.data_table.insertRow(row)
            self.data_table.setItem(row, 0, QTableWidgetItem(str(key)))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(value)))

        layout.addWidget(self.data_table)

        # Confirmation checkbox
        self.confirm_checkbox = QCheckBox("Barcha ma'lumotlar to'g'ri, yaratishni boshlash mumkin")
        layout.addWidget(self.confirm_checkbox)

        # Buttons
        button_layout = QHBoxLayout()

        edit_btn = QPushButton("Tahrir qilish")
        edit_btn.clicked.connect(self.reject)
        button_layout.addWidget(edit_btn)

        generate_btn = QPushButton("✓ Yaratish")
        generate_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold")
        generate_btn.clicked.connect(self.confirm)
        button_layout.addWidget(generate_btn)

        layout.addLayout(button_layout)

    def confirm(self):
        """Confirm and generate contract"""
        if not self.confirm_checkbox.isChecked():
            QMessageBox.warning(self, "Tasdiqlash", "Iltimos, barcha ma'lumotlar to'g'ri ekanligini tasdiqlang")
            return

        self.confirmed = True
        self.data_confirmed.emit(True)
        self.accept()

    def get_result(self):
        """Get confirmation result"""
        return self.confirmed


class PreviewDialog(QDialog):
    """Dialog for previewing generated contract"""

    def __init__(self, docx_path: str, parent=None):
        """Initialize preview dialog"""
        super().__init__(parent)
        self.setWindowTitle("Shartnoma ko'rib chiqish")
        self.setGeometry(150, 150, 800, 600)
        self.docx_path = docx_path

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Yaratilgan shartnoma (Preview)")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Note
        note = QLabel(f"Fayl: {self.docx_path}")
        note.setStyleSheet("color: gray")
        layout.addWidget(note)

        # Preview text (simplified - real implementation would use python-docx to extract text)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.load_preview()
        layout.addWidget(self.preview_text)

        # Buttons
        button_layout = QHBoxLayout()

        open_btn = QPushButton("Word'da ochish")
        open_btn.clicked.connect(self.open_in_word)
        button_layout.addWidget(open_btn)

        close_btn = QPushButton("Yopish")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_preview(self):
        """Load preview from DOCX file"""
        try:
            from docx import Document

            doc = Document(self.docx_path)

            # Extract text from document
            text_lines = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_lines.append(para.text)

            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        row_text.append(cell.text)
                    text_lines.append(" | ".join(row_text))

            self.preview_text.setText("\n".join(text_lines))

        except Exception as e:
            logger.error(f"Error loading preview: {e}")
            self.preview_text.setText(f"Xato: {str(e)}")

    def open_in_word(self):
        """Open document in Microsoft Word"""
        try:
            import subprocess
            import platform
            from pathlib import Path

            docx_file = Path(self.docx_path)

            if not docx_file.exists():
                logger.error(f"File not found: {self.docx_path}")
                return

            if platform.system() == 'Windows':
                subprocess.Popen(['start', 'word', str(docx_file)], shell=True)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', '-a', 'Microsoft Word', str(docx_file)])
            else:  # Linux
                subprocess.Popen(['libreoffice', '--writer', str(docx_file)])

        except Exception as e:
            logger.error(f"Error opening document: {e}")
            QMessageBox.error(self, "Xato", f"Hujjatni ochishda xato: {str(e)}")


class SuccessDialog(QDialog):
    """Dialog showing successful contract generation"""

    def __init__(self, docx_path: str, pdf_path: str = None, parent=None):
        """Initialize success dialog"""
        super().__init__(parent)
        self.setWindowTitle("Muvaffaqiyat!")
        self.setGeometry(200, 200, 500, 300)
        self.docx_path = docx_path
        self.pdf_path = pdf_path

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # Success message
        success_label = QLabel("✓ Shartnoma muvaffaqiyatli yaratildi!")
        success_label.setStyleSheet("color: green; font-size: 14px; font-weight: bold")
        layout.addWidget(success_label)

        # File paths
        layout.addWidget(QLabel("\nYaratilgan fayllar:"))

        files_layout = QVBoxLayout()

        # DOCX
        docx_label = QLabel(f"📄 DOCX: {self.docx_path}")
        docx_label.setWordWrap(True)
        files_layout.addWidget(docx_label)

        # PDF
        if self.pdf_path:
            pdf_label = QLabel(f"📕 PDF: {self.pdf_path}")
            pdf_label.setWordWrap(True)
            files_layout.addWidget(pdf_label)

        layout.addLayout(files_layout)

        # Buttons
        button_layout = QHBoxLayout()

        open_folder_btn = QPushButton("📁 Papkada ochish")
        open_folder_btn.clicked.connect(self.open_folder)
        button_layout.addWidget(open_folder_btn)

        new_contract_btn = QPushButton("➕ Yangi shartnoma")
        new_contract_btn.clicked.connect(self.accept)
        button_layout.addWidget(new_contract_btn)

        layout.addLayout(button_layout)

        layout.addStretch()

    def open_folder(self):
        """Open contracts folder in file explorer"""
        try:
            import subprocess
            import platform
            from pathlib import Path

            folder = Path(self.docx_path).parent

            if platform.system() == 'Windows':
                subprocess.Popen(['explorer', str(folder)])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', str(folder)])
            else:  # Linux
                subprocess.Popen(['xdg-open', str(folder)])

        except Exception as e:
            logger.error(f"Error opening folder: {e}")
            QMessageBox.error(self, "Xato", f"Papkani ochishda xato: {str(e)}")


class ErrorDialog(QDialog):
    """Dialog showing errors during contract generation"""

    def __init__(self, errors: list, parent=None):
        """Initialize error dialog"""
        super().__init__(parent)
        self.setWindowTitle("Xatolar")
        self.setGeometry(200, 200, 600, 400)
        self.errors = errors

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # Error message
        error_label = QLabel("✗ Shartnoma yaratishda xatoliklar yuz berdi:")
        error_label.setStyleSheet("color: red; font-size: 12px; font-weight: bold")
        layout.addWidget(error_label)

        # Error list
        error_text = QTextEdit()
        error_text.setReadOnly(True)
        error_text.setText("\n".join(f"• {error}" for error in self.errors))
        layout.addWidget(error_text)

        # Close button
        close_btn = QPushButton("Yopish")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class SettingsDialog(QDialog):
    """Dialog for application settings"""

    def __init__(self, parent=None):
        """Initialize settings dialog"""
        super().__init__(parent)
        self.setWindowTitle("Sozlamalar")
        self.setGeometry(200, 200, 500, 400)

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("OCR Sozlamalari"))

        # Google Vision settings
        self.google_vision_check = QCheckBox("Google Vision API ishlatish")
        layout.addWidget(self.google_vision_check)

        # Tesseract fallback
        self.tesseract_check = QCheckBox("Tesseract fallback ishlatish")
        layout.addWidget(self.tesseract_check)

        # OCR confidence threshold
        layout.addWidget(QLabel("OCR ishonch daraja (0-100):"))
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setMinimum(0)
        self.confidence_spin.setMaximum(100)
        self.confidence_spin.setValue(70)
        layout.addWidget(self.confidence_spin)

        layout.addSpacing(20)
        layout.addWidget(QLabel("Template Sozlamalari"))

        # Template directory
        layout.addWidget(QLabel("Template papkasi:"))
        template_layout = QHBoxLayout()
        self.template_path_label = QLabel("(Avtomatik)")
        template_layout.addWidget(self.template_path_label)
        browse_btn = QPushButton("Tanlash...")
        browse_btn.clicked.connect(self.browse_template_dir)
        template_layout.addWidget(browse_btn)
        layout.addLayout(template_layout)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Saqlash")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def browse_template_dir(self):
        """Browse for template directory"""
        from PySide6.QtWidgets import QFileDialog
        from pathlib import Path

        directory = QFileDialog.getExistingDirectory(
            self, "Template papkasini tanlang",
            str(Path.home() / "Documents")
        )

        if directory:
            self.template_path_label.setText(directory)
