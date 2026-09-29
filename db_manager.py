"""
Database Manager - SQLite Operations
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite Database Manager"""

    def __init__(self, db_path: str):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection = None
        self.init_connection()
        self.create_tables()

    def init_connection(self):
        """Initialize database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Database connected: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Database execution error: {e}")
            raise

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch single row"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows"""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def create_tables(self):
        """Create database tables"""
        tables = {
            'my_company': '''
                CREATE TABLE IF NOT EXISTS my_company (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    inn TEXT UNIQUE NOT NULL,
                    address TEXT,
                    bank TEXT,
                    account TEXT,
                    mfo TEXT,
                    director TEXT,
                    oked TEXT,
                    vat_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'counterparties': '''
                CREATE TABLE IF NOT EXISTS counterparties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    inn TEXT UNIQUE NOT NULL,
                    address TEXT,
                    bank TEXT,
                    account TEXT,
                    mfo TEXT,
                    director TEXT,
                    oked TEXT,
                    vat_code TEXT,
                    source TEXT,
                    verified BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'service_types': '''
                CREATE TABLE IF NOT EXISTS service_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    template_id INTEGER,
                    FOREIGN KEY (template_id) REFERENCES templates(id)
                )
            ''',
            'templates': '''
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    service_type_id INTEGER,
                    placeholders TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (service_type_id) REFERENCES service_types(id)
                )
            ''',
            'generated_contracts': '''
                CREATE TABLE IF NOT EXISTS generated_contracts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_number TEXT UNIQUE NOT NULL,
                    date DATE NOT NULL,
                    buyer_id INTEGER,
                    seller_id INTEGER,
                    service_type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    amount_words TEXT NOT NULL,
                    vat_status TEXT,
                    template_id INTEGER,
                    docx_path TEXT,
                    pdf_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (buyer_id) REFERENCES counterparties(id),
                    FOREIGN KEY (seller_id) REFERENCES counterparties(id),
                    FOREIGN KEY (template_id) REFERENCES templates(id)
                )
            ''',
            'template_uploads': '''
                CREATE TABLE IF NOT EXISTS template_uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_filename TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    service_type TEXT,
                    uploaded_by TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        }

        for table_name, create_query in tables.items():
            try:
                self.execute(create_query)
                logger.info(f"Table created/verified: {table_name}")
            except sqlite3.Error as e:
                logger.error(f"Error creating table {table_name}: {e}")

    # ============================
    # MY COMPANY OPERATIONS
    # ============================

    def add_my_company(self, company_data: Dict[str, Any]) -> int:
        """Add or update my company"""
        query = '''
            INSERT OR REPLACE INTO my_company
            (name, inn, address, bank, account, mfo, director, oked, vat_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            company_data.get('name'),
            company_data.get('inn'),
            company_data.get('address'),
            company_data.get('bank'),
            company_data.get('account'),
            company_data.get('mfo'),
            company_data.get('director'),
            company_data.get('oked'),
            company_data.get('vat_code')
        )
        cursor = self.execute(query, params)
        return cursor.lastrowid

    def get_my_company(self) -> Optional[Dict]:
        """Get my company details"""
        query = 'SELECT * FROM my_company LIMIT 1'
        return self.fetch_one(query)

    # ============================
    # COUNTERPARTIES OPERATIONS
    # ============================

    def add_counterparty(self, counterparty_data: Dict[str, Any]) -> int:
        """Add counterparty"""
        query = '''
            INSERT INTO counterparties
            (name, inn, address, bank, account, mfo, director, oked, vat_code, source, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            counterparty_data.get('name'),
            counterparty_data.get('inn'),
            counterparty_data.get('address'),
            counterparty_data.get('bank'),
            counterparty_data.get('account'),
            counterparty_data.get('mfo'),
            counterparty_data.get('director'),
            counterparty_data.get('oked'),
            counterparty_data.get('vat_code'),
            counterparty_data.get('source', 'manual'),
            counterparty_data.get('verified', 0)
        )
        cursor = self.execute(query, params)
        return cursor.lastrowid

    def get_counterparty_by_inn(self, inn: str) -> Optional[Dict]:
        """Get counterparty by INN"""
        query = 'SELECT * FROM counterparties WHERE inn = ?'
        return self.fetch_one(query, (inn,))

    def get_counterparty_by_id(self, counterparty_id: int) -> Optional[Dict]:
        """Get counterparty by ID"""
        query = 'SELECT * FROM counterparties WHERE id = ?'
        return self.fetch_one(query, (counterparty_id,))

    def get_all_counterparties(self) -> List[Dict]:
        """Get all counterparties"""
        query = 'SELECT * FROM counterparties ORDER BY created_at DESC'
        return self.fetch_all(query)

    def search_counterparties(self, search_term: str) -> List[Dict]:
        """Search counterparties by name or INN"""
        query = '''
            SELECT * FROM counterparties
            WHERE name LIKE ? OR inn LIKE ?
            ORDER BY created_at DESC
        '''
        search_param = f"%{search_term}%"
        return self.fetch_all(query, (search_param, search_param))

    def update_counterparty(self, counterparty_id: int, counterparty_data: Dict[str, Any]):
        """Update counterparty"""
        query = '''
            UPDATE counterparties
            SET name = ?, address = ?, bank = ?, account = ?, mfo = ?,
                director = ?, oked = ?, vat_code = ?, verified = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        params = (
            counterparty_data.get('name'),
            counterparty_data.get('address'),
            counterparty_data.get('bank'),
            counterparty_data.get('account'),
            counterparty_data.get('mfo'),
            counterparty_data.get('director'),
            counterparty_data.get('oked'),
            counterparty_data.get('vat_code'),
            counterparty_data.get('verified', 0),
            counterparty_id
        )
        self.execute(query, params)

    # ============================
    # TEMPLATES OPERATIONS
    # ============================

    def add_template(self, template_data: Dict[str, Any]) -> int:
        """Add template"""
        query = '''
            INSERT INTO templates
            (name, filename, file_path, service_type_id, placeholders)
            VALUES (?, ?, ?, ?, ?)
        '''
        params = (
            template_data.get('name'),
            template_data.get('filename'),
            template_data.get('file_path'),
            template_data.get('service_type_id'),
            json.dumps(template_data.get('placeholders', []))
        )
        cursor = self.execute(query, params)
        return cursor.lastrowid

    def get_template_by_id(self, template_id: int) -> Optional[Dict]:
        """Get template by ID"""
        query = 'SELECT * FROM templates WHERE id = ?'
        return self.fetch_one(query, (template_id,))

    def get_all_templates(self) -> List[Dict]:
        """Get all templates"""
        query = 'SELECT * FROM templates ORDER BY created_at DESC'
        return self.fetch_all(query)

    # ============================
    # GENERATED CONTRACTS OPERATIONS
    # ============================

    def add_generated_contract(self, contract_data: Dict[str, Any]) -> int:
        """Add generated contract record"""
        query = '''
            INSERT INTO generated_contracts
            (contract_number, date, buyer_id, seller_id, service_type,
             amount, amount_words, vat_status, template_id, docx_path, pdf_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            contract_data.get('contract_number'),
            contract_data.get('date'),
            contract_data.get('buyer_id'),
            contract_data.get('seller_id'),
            contract_data.get('service_type'),
            contract_data.get('amount'),
            contract_data.get('amount_words'),
            contract_data.get('vat_status'),
            contract_data.get('template_id'),
            contract_data.get('docx_path'),
            contract_data.get('pdf_path')
        )
        cursor = self.execute(query, params)
        return cursor.lastrowid

    def get_generated_contracts(self, limit: int = 50) -> List[Dict]:
        """Get latest generated contracts"""
        query = '''
            SELECT * FROM generated_contracts
            ORDER BY created_at DESC
            LIMIT ?
        '''
        return self.fetch_all(query, (limit,))

    def search_generated_contracts(self, search_term: str) -> List[Dict]:
        """Search generated contracts"""
        query = '''
            SELECT * FROM generated_contracts
            WHERE contract_number LIKE ? OR service_type LIKE ?
            ORDER BY created_at DESC
        '''
        search_param = f"%{search_term}%"
        return self.fetch_all(query, (search_param, search_param))

    def get_next_contract_number(self, date_str: str) -> str:
        """Get next contract number for given date"""
        query = '''
            SELECT COUNT(*) as count FROM generated_contracts
            WHERE date = ?
        '''
        result = self.fetch_one(query, (date_str,))
        count = result['count'] if result else 0
        return f"{date_str}_{count + 1:03d}"

    # ============================
    # SERVICE TYPES OPERATIONS
    # ============================

    def add_service_type(self, name: str, description: str = None) -> int:
        """Add service type"""
        query = '''
            INSERT OR IGNORE INTO service_types (name, description)
            VALUES (?, ?)
        '''
        cursor = self.execute(query, (name, description))
        return cursor.lastrowid

    def get_all_service_types(self) -> List[Dict]:
        """Get all service types"""
        query = 'SELECT * FROM service_types ORDER BY name'
        return self.fetch_all(query)

    # ============================
    # STATISTICS
    # ============================

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_counterparties': self.fetch_one('SELECT COUNT(*) as count FROM counterparties')['count'],
            'total_templates': self.fetch_one('SELECT COUNT(*) as count FROM templates')['count'],
            'total_generated': self.fetch_one('SELECT COUNT(*) as count FROM generated_contracts')['count'],
            'service_types': self.fetch_one('SELECT COUNT(*) as count FROM service_types')['count']
        }

    def vacuum(self):
        """Optimize database"""
        self.execute('VACUUM')
        logger.info("Database optimized (VACUUM)")
