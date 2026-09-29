"""
Main Window - PySide6 UI for Shartnoma Generator
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox,
    QDateEdit, QFileDialog, QMessageBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QProgressBar, QStatusBar
)
from PySide6.QtCore import Qt, QDate, pyqtSignal, QThread
from PySide6.QtGui import QFont, QIcon
from pathlib import Path
from datetime import datetime
import logging

from config import (
    APP_NAME, APP_VERSION, DEFAULT_SERVICE_TYPES,
    VAT_STATUSES, CONTRACTS_DIR, TEMPLATES_DIR, UI_CONFIG
)
from db_manager import DatabaseManager
from ocr_module import OCREngine
from inn_verifier import INNVerifier
from validator import ContractValidator
from contract_generator import ContractGenerator

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        """Initialize main window"""
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, UI_CONFIG['window_width'], UI_CONFIG['window_height'])

        # Initialize managers
        self.db = DatabaseManager(str(Path.home() / "Documents" / "Shartnoma_Generator" / "database.db"))
        self.ocr_engine = OCREngine()
        self.inn_verifier = INNVerifier()

        # Current contract data
        self.contract_data = {}
        self.current_buyer = None
        self.current_seller = None

        # Setup UI
        self.init_ui()

    def init_ui(self):
        """Initialize user interface"""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Tab widget for different sections
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Tab 1: Input
        tabs.addTab(self.create_input_tab(), "Ma'lumot kiritish")

        # Tab 2: Rekvizit
        tabs.addTab(self.create_rekvizit_tab(), "Rekvizit")

        # Tab 3: Tomonlar
        tabs.addTab(self.create_parties_tab(), "Tomonlar")

        # Tab 4: Xizmat va summa
        tabs.addTab(self.create_service_tab(), "Xizmat va summa")

        # Tab 5: Ko'rib chiqish
        tabs.addTab(self.create_review_tab(), "Ko'rib chiqish")

        # Status bar
        self.statusBar().showMessage("Tayyor")

    def create_input_tab(self):
        """Create input tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Ma'lumot kiritish usuli")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Method selection
        method_layout = QHBoxLayout()

        # Image upload button
        self.upload_btn = QPushButton("Rekvizit yuklash (JPG/PNG)")
        self.upload_btn.clicked.connect(self.upload_image)
        method_layout.addWidget(self.upload_btn)

        # INN input
        self.inn_input = QLineEdit()
        self.inn_input.setPlaceholderText("yoki INN kiritish")
        self.inn_input.returnPressed.connect(self.lookup_by_inn)
        method_layout.addWidget(self.inn_input)

        # Search button
        search_btn = QPushButton("Qidirish")
        search_btn.clicked.connect(self.lookup_by_inn)
        method_layout.addWidget(search_btn)

        layout.addLayout(method_layout)

        # Status display
        self.status_label = QLabel("Tayyor")
        self.status_label.setStyleSheet("color: green")
        layout.addWidget(self.status_label)

        # Extracted data display
        self.extracted_data_table = QTableWidget(0, 2)
        self.extracted_data_table.setHorizontalHeaderLabels(["Maydon", "Qiymat"])
        layout.addWidget(self.extracted_data_table)

        layout.addStretch()
        return widget

    def create_rekvizit_tab(self):
        """Create rekvizit (details) tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Company info section
        company_layout = QVBoxLayout()

        # Company name
        layout.addWidget(QLabel("Korxona nomi:"))
        self.company_name_input = QLineEdit()
        layout.addWidget(self.company_name_input)

        # INN
        layout.addWidget(QLabel("INN (9 ta raqam):"))
        self.inn_verified_input = QLineEdit()
        self.inn_verified_input.setReadOnly(True)
        layout.addWidget(self.inn_verified_input)

        # Address
        layout.addWidget(QLabel("Manzil:"))
        self.address_input = QLineEdit()
        layout.addWidget(self.address_input)

        # Bank
        layout.addWidget(QLabel("Bank:"))
        self.bank_input = QLineEdit()
        layout.addWidget(self.bank_input)

        # Account
        layout.addWidget(QLabel("Hisob raqami (20 ta raqam):"))
        self.account_input = QLineEdit()
        layout.addWidget(self.account_input)

        # MFO
        layout.addWidget(QLabel("MFO (5 ta raqam):"))
        self.mfo_input = QLineEdit()
        layout.addWidget(self.mfo_input)

        # Director
        layout.addWidget(QLabel("Rahbari:"))
        self.director_input = QLineEdit()
        layout.addWidget(self.director_input)

        # Verify button
        verify_btn = QPushButton("Tekshirish")
        verify_btn.clicked.connect(self.verify_rekvizit)
        layout.addWidget(verify_btn)

        # Verification status
        self.verify_status_label = QLabel("")
        self.verify_status_label.setStyleSheet("color: blue")
        layout.addWidget(self.verify_status_label)

        layout.addStretch()
        return widget

    def create_parties_tab(self):
        """Create parties selection tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Buyurtmachi (Harid qiluvchi):"))

        # Buyer selection
        buyer_layout = QHBoxLayout()
        self.buyer_combo = QComboBox()
        self.buyer_combo.currentIndexChanged.connect(self.on_buyer_changed)
        buyer_layout.addWidget(self.buyer_combo)

        add_buyer_btn = QPushButton("+ Yangi")
        add_buyer_btn.clicked.connect(self.add_new_buyer)
        buyer_layout.addWidget(add_buyer_btn)

        layout.addLayout(buyer_layout)

        # Buyer details display
        self.buyer_details = QLabel("")
        layout.addWidget(self.buyer_details)

        layout.addSpacing(20)

        layout.addWidget(QLabel("Bajaruvchi (Sotuvchi):"))

        # Seller selection
        seller_layout = QHBoxLayout()
        self.seller_combo = QComboBox()
        self.seller_combo.currentIndexChanged.connect(self.on_seller_changed)
        seller_layout.addWidget(self.seller_combo)

        add_seller_btn = QPushButton("+ Yangi")
        add_seller_btn.clicked.connect(self.add_new_seller)
        seller_layout.addWidget(add_seller_btn)

        layout.addLayout(seller_layout)

        # Seller details display
        self.seller_details = QLabel("")
        layout.addWidget(self.seller_details)

        layout.addStretch()
        return widget

    def create_service_tab(self):
        """Create service and amount tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Service type
        layout.addWidget(QLabel("Xizmat turi:"))
        self.service_combo = QComboBox()
        self.service_combo.addItems(DEFAULT_SERVICE_TYPES)
        layout.addWidget(self.service_combo)

        # Amount
        layout.addWidget(QLabel("Summa (so'm):"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Masalan: 500000000")
        self.amount_input.textChanged.connect(self.on_amount_changed)
        layout.addWidget(self.amount_input)

        # Formatted amount display
        self.formatted_amount = QLabel("")
        self.formatted_amount.setStyleSheet("background-color: #f0f0f0; padding: 10px")
        layout.addWidget(self.formatted_amount)

        # Amount in words
        self.amount_words = QLabel("")
        self.amount_words.setStyleSheet("background-color: #f0f0f0; padding: 10px")
        layout.addWidget(self.amount_words)

        # VAT status
        layout.addWidget(QLabel("NDS holati:"))
        self.vat_combo = QComboBox()
        self.vat_combo.addItems(VAT_STATUSES)
        layout.addWidget(self.vat_combo)

        # Date
        layout.addWidget(QLabel("Sana:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit)

        # Contract number
        layout.addWidget(QLabel("Shartnoma raqami (avtomatik):"))
        self.contract_number_input = QLineEdit()
        self.contract_number_input.setReadOnly(True)
        layout.addWidget(self.contract_number_input)

        layout.addStretch()
        return widget

    def create_review_tab(self):
        """Create review and generate tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Shartnomani ko'rib chiqing va yaratishni boshlang"))

        # Review table
        self.review_table = QTableWidget(0, 2)
        self.review_table.setHorizontalHeaderLabels(["Maydon", "Qiymat"])
        layout.addWidget(self.review_table)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()

        preview_btn = QPushButton("Ko'rib chiqish (Preview)")
        preview_btn.clicked.connect(self.preview_contract)
        button_layout.addWidget(preview_btn)

        generate_btn = QPushButton("✓ Shartnoma yaratish")
        generate_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold")
        generate_btn.clicked.connect(self.generate_contract)
        button_layout.addWidget(generate_btn)

        reset_btn = QPushButton("Qayta boshlash")
        reset_btn.clicked.connect(self.reset_form)
        button_layout.addWidget(reset_btn)

        layout.addLayout(button_layout)

        layout.addStretch()
        return widget

    def upload_image(self):
        """Upload and process image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Rekvizit yuklash", "",
            "Image Files (*.jpg *.jpeg *.png);;PDF Files (*.pdf)"
        )

        if not file_path:
            return

        self.status_label.setText("OCR ishlatilmoqda...")
        self.status_label.setStyleSheet("color: orange")

        try:
            # Extract text using OCR
            success, fields = self.ocr_engine.extract_fields(file_path)

            if success:
                self.display_extracted_data(fields)
                self.status_label.setText(f"✓ Matnlar ekstraktsiya qilindi (ishonch: {fields.get('ocr_confidence', 0):.0%})")
                self.status_label.setStyleSheet("color: green")
            else:
                self.status_label.setText("✗ OCR xatosi: matnlar topilmadi")
                self.status_label.setStyleSheet("color: red")

        except Exception as e:
            logger.error(f"Error in upload_image: {e}")
            self.status_label.setText(f"✗ Xato: {str(e)}")
            self.status_label.setStyleSheet("color: red")

    def lookup_by_inn(self):
        """Look up company by INN"""
        inn = self.inn_input.text().strip()

        if not inn:
            QMessageBox.warning(self, "Xato", "INN kiritishing kerak")
            return

        # Verify INN format
        valid, error = self.inn_verifier.validate_format(inn)
        if not valid:
            QMessageBox.warning(self, "INN xatosi", error)
            return

        # Look up in database
        company = self.db.get_counterparty_by_inn(inn)

        if company:
            self.populate_rekvizit(company)
            self.status_label.setText("✓ Korxona ma'lumotlari topildi")
            self.status_label.setStyleSheet("color: green")
        else:
            QMessageBox.information(self, "Natija", "Bu INN database'da topilmadi. Ma'lumotlarni qo'l bilan kiritishingiz kerak.")
            self.status_label.setText("⚠ Yangi korxona")
            self.status_label.setStyleSheet("color: orange")

    def display_extracted_data(self, fields):
        """Display extracted fields in table"""
        self.extracted_data_table.setRowCount(0)

        for key, value in fields.items():
            if key not in ['full_text']:
                row = self.extracted_data_table.rowCount()
                self.extracted_data_table.insertRow(row)
                self.extracted_data_table.setItem(row, 0, QTableWidgetItem(key))
                self.extracted_data_table.setItem(row, 1, QTableWidgetItem(str(value)))

    def populate_rekvizit(self, company_data):
        """Populate rekvizit fields from company data"""
        self.company_name_input.setText(company_data.get('name', ''))
        self.inn_verified_input.setText(company_data.get('inn', ''))
        self.address_input.setText(company_data.get('address', ''))
        self.bank_input.setText(company_data.get('bank', ''))
        self.account_input.setText(company_data.get('account', ''))
        self.mfo_input.setText(company_data.get('mfo', ''))
        self.director_input.setText(company_data.get('director', ''))

    def verify_rekvizit(self):
        """Verify rekvizit data"""
        # Collect data
        company_name = self.company_name_input.text().strip()
        inn = self.inn_verified_input.text().strip()
        address = self.address_input.text().strip()
        bank = self.bank_input.text().strip()
        account = self.account_input.text().strip()
        mfo = self.mfo_input.text().strip()
        director = self.director_input.text().strip()

        # Validate
        errors = []

        valid, error = ContractValidator.validate_company_name(company_name)
        if not valid:
            errors.append(f"Korxona nomi: {error}")

        valid, error = ContractValidator.validate_inn(inn)
        if not valid:
            errors.append(f"INN: {error}")

        valid, error = ContractValidator.validate_address(address)
        if not valid:
            errors.append(f"Manzil: {error}")

        valid, error = ContractValidator.validate_bank(bank)
        if not valid:
            errors.append(f"Bank: {error}")

        valid, error = ContractValidator.validate_account(account)
        if not valid:
            errors.append(f"Hisob raqami: {error}")

        valid, error = ContractValidator.validate_mfo(mfo)
        if not valid:
            errors.append(f"MFO: {error}")

        valid, error = ContractValidator.validate_director(director)
        if not valid:
            errors.append(f"Rahbari: {error}")

        if errors:
            QMessageBox.critical(self, "Validatsiya xatolari", "\n".join(errors))
            self.verify_status_label.setText("✗ Xatoliklar bor")
            self.verify_status_label.setStyleSheet("color: red")
        else:
            QMessageBox.information(self, "Muvaffaqiyat", "Barcha ma'lumotlar to'g'ri")
            self.verify_status_label.setText("✓ To'g'ri")
            self.verify_status_label.setStyleSheet("color: green")

    def on_buyer_changed(self):
        """Handle buyer selection change"""
        pass  # TODO: Implement

    def on_seller_changed(self):
        """Handle seller selection change"""
        pass  # TODO: Implement

    def add_new_buyer(self):
        """Add new buyer"""
        pass  # TODO: Implement

    def add_new_seller(self):
        """Add new seller"""
        pass  # TODO: Implement

    def on_amount_changed(self):
        """Update amount display when amount changes"""
        try:
            from number_converter import NumberConverter

            amount_str = self.amount_input.text().strip()
            if amount_str:
                formatted, words = NumberConverter.convert_amount(amount_str)
                self.formatted_amount.setText(f"Formatlab: {formatted} so'm")
                self.amount_words.setText(f"So'zla: {words}")
        except Exception as e:
            logger.error(f"Error formatting amount: {e}")

    def preview_contract(self):
        """Preview contract"""
        QMessageBox.information(self, "Preview", "Preview funktsiyasi qo'shiladi")

    def generate_contract(self):
        """Generate contract"""
        QMessageBox.information(self, "Yaratish", "Shartnoma yaratish funktsiyasi qo'shiladi")

    def reset_form(self):
        """Reset form to initial state"""
        self.company_name_input.clear()
        self.inn_input.clear()
        self.address_input.clear()
        self.bank_input.clear()
        self.account_input.clear()
        self.mfo_input.clear()
        self.director_input.clear()
        self.amount_input.clear()
        self.contract_number_input.clear()
        self.extracted_data_table.setRowCount(0)
