"""
SHARTNOMA GENERATOR - Global Configuration
"""

import os
from pathlib import Path
from datetime import datetime

# ============================
# APPLICATION INFO
# ============================
APP_NAME = "SHARTNOMA GENERATOR"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Jurat"

# ============================
# PATHS
# ============================
BASE_DIR = Path.home()
APP_DATA_DIR = BASE_DIR / "Documents" / "Shartnoma_Generator"
TEMPLATES_DIR = APP_DATA_DIR / "Templates"
CONTRACTS_DIR = APP_DATA_DIR / "Contracts"
SETTINGS_DIR = APP_DATA_DIR / "Settings"
DATABASE_PATH = APP_DATA_DIR / "database.db"

# Create directories if not exist
for directory in [APP_DATA_DIR, TEMPLATES_DIR, CONTRACTS_DIR, SETTINGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================
# DATABASE
# ============================
DATABASE_CONFIG = {
    'path': str(DATABASE_PATH),
    'timeout': 5.0,
    'check_same_thread': False
}

# ============================
# OCR CONFIGURATION
# ============================
GOOGLE_VISION_ENABLED = True
GOOGLE_VISION_CREDENTIALS_PATH = SETTINGS_DIR / "google_credentials.json"

# Tesseract
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
USE_TESSERACT_FALLBACK = True

# ============================
# CONTRACT CONFIGURATION
# ============================
CONTRACT_NUMBER_FORMAT = "{date}_{counter:03d}"  # e.g., "2026-09-29_001"

# Service Types (mapped from user's requirement doc)
DEFAULT_SERVICE_TYPES = [
    "Katlavan qazish",      # Excavation service
    "Avto xizmat",           # Auto service
    "Shagal tashish",       # Transport
    "Maxsus texnika xizmati", # Special equipment service
    "Transport xizmati",     # Transport service
    "Mexanizm xizmati",      # Mechanical service
    "Boshqa"                # Other
]

# Template Mapping - which template to use for which service type
TEMPLATE_MAPPING = {
    "Katlavan qazish": "toshkent_stroy_build_unversal_shartnoma.docx",     # Construction/excavation
    "Avto xizmat": "toshkent_logistikdan_unversal_shartnoma.docx",         # Auto/logistics
    "Mexanizm xizmati": "toshkent_stroy_build_unversal_shartnoma.docx",   # Mechanism service
    "Shagal tashish": "toshkent_logistikdan_unversal_shartnoma.docx",      # Transport
    "Transport xizmati": "toshkent_logistikdan_unversal_shartnoma.docx",   # Transport service
    "Maxsus texnika xizmati": "RAYXONA_SHIRINA_SERVIS_UNVERSAL_SHARTNOMA.docx",  # Special equipment
    "Boshqa": "toshkent_stroy_build_unversal_shartnoma.docx"               # Default template
}

# Default template (fallback)
DEFAULT_TEMPLATE = "toshkent_stroy_build_unversal_shartnoma.docx"

# VAT Statuses
VAT_STATUSES = [
    "NDS bilan",
    "NDSsiz",
    "Aniqlash kerak"
]

# ============================
# UI CONFIGURATION
# ============================
UI_CONFIG = {
    'window_width': 1000,
    'window_height': 800,
    'theme': 'light',  # 'light' or 'dark'
    'language': 'uz',  # 'uz' or 'en'
    'font_family': 'Arial',
    'font_size': 10
}

# ============================
# PLACEHOLDERS (Word Template)
# ============================
PLACEHOLDERS = {
    'CONTRACT_NUMBER': '{{CONTRACT_NUMBER}}',
    'CONTRACT_DATE': '{{CONTRACT_DATE}}',
    'BUYER_NAME': '{{BUYER_NAME}}',
    'BUYER_INN': '{{BUYER_INN}}',
    'BUYER_ADDRESS': '{{BUYER_ADDRESS}}',
    'BUYER_BANK': '{{BUYER_BANK}}',
    'BUYER_ACCOUNT': '{{BUYER_ACCOUNT}}',
    'BUYER_MFO': '{{BUYER_MFO}}',
    'BUYER_DIRECTOR': '{{BUYER_DIRECTOR}}',
    'SELLER_NAME': '{{SELLER_NAME}}',
    'SELLER_INN': '{{SELLER_INN}}',
    'SELLER_ADDRESS': '{{SELLER_ADDRESS}}',
    'SELLER_BANK': '{{SELLER_BANK}}',
    'SELLER_ACCOUNT': '{{SELLER_ACCOUNT}}',
    'SELLER_MFO': '{{SELLER_MFO}}',
    'SELLER_DIRECTOR': '{{SELLER_DIRECTOR}}',
    'SERVICE_TYPE': '{{SERVICE_TYPE}}',
    'SERVICE_DESCRIPTION': '{{SERVICE_DESCRIPTION}}',
    'AMOUNT': '{{AMOUNT}}',
    'AMOUNT_WORDS': '{{AMOUNT_WORDS}}',
    'VAT_STATUS': '{{VAT_STATUS}}',
    'VAT_AMOUNT': '{{VAT_AMOUNT}}',
    'TOTAL_AMOUNT': '{{TOTAL_AMOUNT}}'
}

# ============================
# INN VALIDATION
# ============================
INN_LENGTH = 9  # Uzbek INN format: 9 digits
INN_PATTERN = r'^\d{9}$'

# ============================
# DATE FORMATS
# ============================
DATE_FORMAT = '%d.%m.%Y'
DATE_FORMAT_ISO = '%Y-%m-%d'

# ============================
# VALIDATION RULES
# ============================
VALIDATION_RULES = {
    'company_name_min_length': 3,
    'company_name_max_length': 255,
    'address_min_length': 10,
    'address_max_length': 500,
    'director_name_min_length': 5,
    'director_name_max_length': 255,
    'account_number_length': 20,  # Uzbek account format
    'mfo_length': 5,  # Uzbek MFO format
    'contract_number_min_length': 5,
    'contract_number_max_length': 50,
    'min_amount': 1000,  # Minimum contract amount
    'max_amount': 9999999999999  # Maximum contract amount
}

# ============================
# OCR CONFIDENCE THRESHOLD
# ============================
OCR_CONFIDENCE_THRESHOLD = 0.70  # 70% confidence required

# ============================
# DEBUGGING
# ============================
DEBUG = False
LOG_LEVEL = 'INFO'  # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

# ============================
# LOGGING
# ============================
LOG_DIR = APP_DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / f"shartnoma_generator_{datetime.now().strftime('%Y%m%d')}.log"

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
