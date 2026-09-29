"""
Contract Generator - Generate Word and PDF contracts from templates
"""

import os
from pathlib import Path
from typing import Dict, Tuple, Optional, Any
from datetime import datetime
import logging

from config import (
    CONTRACTS_DIR,
    PLACEHOLDERS,
    DATE_FORMAT,
    DATE_FORMAT_ISO
)
from template_parser import TemplateParser
from number_converter import NumberConverter

logger = logging.getLogger(__name__)


class ContractGenerator:
    """Generate contracts from templates with data replacement"""

    def __init__(self, template_path: str):
        """Initialize generator with template"""
        self.template_path = Path(template_path)
        self.parser = None
        self.contract_data = {}
        self.errors = []

        if self.template_path.exists():
            self.parser = TemplateParser(str(self.template_path))
        else:
            logger.error(f"Template not found: {self.template_path}")

    def prepare_replacements(self, contract_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Prepare placeholder replacements from contract data

        Maps contract data fields to template placeholders
        """
        replacements = {}

        try:
            # Contract identifiers
            replacements[PLACEHOLDERS['CONTRACT_NUMBER']] = str(
                contract_data.get('contract_number', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['CONTRACT_DATE']] = str(
                contract_data.get('date', 'ANIQLANMADI')
            )

            # Buyer information
            replacements[PLACEHOLDERS['BUYER_NAME']] = str(
                contract_data.get('buyer_name', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['BUYER_INN']] = str(
                contract_data.get('buyer_inn', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['BUYER_ADDRESS']] = str(
                contract_data.get('buyer_address', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['BUYER_BANK']] = str(
                contract_data.get('buyer_bank', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['BUYER_ACCOUNT']] = str(
                contract_data.get('buyer_account', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['BUYER_MFO']] = str(
                contract_data.get('buyer_mfo', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['BUYER_DIRECTOR']] = str(
                contract_data.get('buyer_director', 'ANIQLANMADI')
            )

            # Seller information
            replacements[PLACEHOLDERS['SELLER_NAME']] = str(
                contract_data.get('seller_name', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['SELLER_INN']] = str(
                contract_data.get('seller_inn', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['SELLER_ADDRESS']] = str(
                contract_data.get('seller_address', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['SELLER_BANK']] = str(
                contract_data.get('seller_bank', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['SELLER_ACCOUNT']] = str(
                contract_data.get('seller_account', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['SELLER_MFO']] = str(
                contract_data.get('seller_mfo', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['SELLER_DIRECTOR']] = str(
                contract_data.get('seller_director', 'ANIQLANMADI')
            )

            # Service details
            replacements[PLACEHOLDERS['SERVICE_TYPE']] = str(
                contract_data.get('service_type', 'ANIQLANMADI')
            )
            replacements[PLACEHOLDERS['SERVICE_DESCRIPTION']] = str(
                contract_data.get('service_description', '')
            )

            # Amount information
            amount = contract_data.get('amount')
            if amount:
                # Format amount with spaces (500000000 → "500 000 000")
                formatted_amount = NumberConverter.format_with_spaces(int(amount))
                replacements[PLACEHOLDERS['AMOUNT']] = formatted_amount

                # Amount in Uzbek words (500000000 → "Besh yuz million sўm")
                amount_words = contract_data.get('amount_words', '')
                replacements[PLACEHOLDERS['AMOUNT_WORDS']] = amount_words

                # Calculate VAT if NDS bilan (with VAT)
                vat_status = contract_data.get('vat_status', 'Aniqlash kerak')
                if vat_status == 'NDS bilan':
                    vat_amount = int(amount) * 0.12
                    vat_formatted = NumberConverter.format_with_spaces(int(vat_amount))
                    replacements[PLACEHOLDERS['VAT_AMOUNT']] = vat_formatted

                    total_amount = int(amount) + int(vat_amount)
                    total_formatted = NumberConverter.format_with_spaces(int(total_amount))
                    replacements[PLACEHOLDERS['TOTAL_AMOUNT']] = total_formatted
                else:
                    replacements[PLACEHOLDERS['VAT_AMOUNT']] = '0'
                    replacements[PLACEHOLDERS['TOTAL_AMOUNT']] = formatted_amount
            else:
                replacements[PLACEHOLDERS['AMOUNT']] = 'ANIQLANMADI'
                replacements[PLACEHOLDERS['AMOUNT_WORDS']] = 'ANIQLANMADI'
                replacements[PLACEHOLDERS['VAT_AMOUNT']] = 'ANIQLANMADI'
                replacements[PLACEHOLDERS['TOTAL_AMOUNT']] = 'ANIQLANMADI'

            # VAT status
            replacements[PLACEHOLDERS['VAT_STATUS']] = str(
                contract_data.get('vat_status', 'Aniqlash kerak')
            )

            return replacements

        except Exception as e:
            logger.error(f"Error preparing replacements: {e}")
            self.errors.append(f"Replacement preparation error: {str(e)}")
            return {}

    def generate_filename(self, contract_data: Dict[str, Any]) -> str:
        """
        Generate standardized contract filename

        Format: YYYY-MM-DD_COMPANY_AMOUNT_SERVICE.docx
        Example: 2026-09-29_ABC_MCHJ_500000000_Avtousluga.docx
        """
        try:
            date = contract_data.get('date', datetime.now().strftime(DATE_FORMAT))
            company = contract_data.get('seller_name', 'UNKNOWN').replace(' ', '_')[:20]
            amount = contract_data.get('amount', 0)
            service = contract_data.get('service_type', 'Boshqa').replace(' ', '_')[:20]

            filename = f"{date}_{company}_{amount}_{service}.docx"
            return filename

        except Exception as e:
            logger.error(f"Error generating filename: {e}")
            return f"contract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

    def generate_contract(self, contract_data: Dict[str, Any],
                         output_dir: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Generate contract Word document

        Args:
            contract_data: Dictionary with all contract information
            output_dir: Output directory (default: CONTRACTS_DIR)

        Returns:
            Tuple of (success: bool, result_dict: {docx_path, pdf_path, errors})
        """
        self.errors = []

        if not self.parser:
            self.errors.append("Template not loaded")
            return False, {'docx_path': None, 'pdf_path': None, 'errors': self.errors}

        try:
            # Use default output directory if not specified
            if output_dir is None:
                output_dir = str(CONTRACTS_DIR)

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate filename
            filename = self.generate_filename(contract_data)
            docx_file = output_path / filename

            # Prepare replacements
            replacements = self.prepare_replacements(contract_data)
            if not replacements:
                return False, {'docx_path': None, 'pdf_path': None, 'errors': self.errors}

            # Replace placeholders and save DOCX
            success, errors = self.parser.replace_in_document(replacements)
            if not success:
                self.errors.extend(errors)
                return False, {'docx_path': None, 'pdf_path': None, 'errors': self.errors}

            # Save DOCX file
            if not self.parser.save_to_docx(str(docx_file)):
                self.errors.append(f"Failed to save DOCX to {docx_file}")
                return False, {'docx_path': None, 'pdf_path': None, 'errors': self.errors}

            logger.info(f"Contract generated: {docx_file}")

            return True, {
                'docx_path': str(docx_file),
                'pdf_path': None,  # PDF generation in separate step
                'filename': filename,
                'errors': []
            }

        except Exception as e:
            logger.error(f"Error generating contract: {e}")
            self.errors.append(f"Contract generation error: {str(e)}")
            return False, {'docx_path': None, 'pdf_path': None, 'errors': self.errors}

    @staticmethod
    def docx_to_pdf(docx_path: str, pdf_path: str) -> Tuple[bool, str]:
        """
        Convert DOCX to PDF

        Uses LibreOffice in headless mode (most reliable method)
        Fallback: reportlab for simple conversion
        """
        try:
            docx_file = Path(docx_path)
            pdf_file = Path(pdf_path)

            if not docx_file.exists():
                return False, f"DOCX file not found: {docx_path}"

            pdf_file.parent.mkdir(parents=True, exist_ok=True)

            # Try using LibreOffice (most reliable for complex documents)
            import subprocess
            import platform

            try:
                if platform.system() == 'Windows':
                    # Windows path to LibreOffice
                    libreoffice_paths = [
                        r'C:\Program Files\LibreOffice\program\soffice.exe',
                        r'C:\Program Files (x86)\LibreOffice\program\soffice.exe'
                    ]

                    libreoffice_exe = None
                    for path in libreoffice_paths:
                        if Path(path).exists():
                            libreoffice_exe = path
                            break

                    if libreoffice_exe:
                        subprocess.run([
                            libreoffice_exe,
                            '--headless',
                            '--convert-to', 'pdf',
                            '--outdir', str(pdf_file.parent),
                            str(docx_file)
                        ], check=True, capture_output=True)

                        logger.info(f"PDF generated via LibreOffice: {pdf_path}")
                        return True, str(pdf_path)
                else:
                    # Linux/Mac: try libreoffice
                    subprocess.run([
                        'libreoffice',
                        '--headless',
                        '--convert-to', 'pdf',
                        '--outdir', str(pdf_file.parent),
                        str(docx_file)
                    ], check=True, capture_output=True)

                    logger.info(f"PDF generated via LibreOffice: {pdf_path}")
                    return True, str(pdf_path)

            except (FileNotFoundError, subprocess.CalledProcessError):
                # Fallback: use python-docx with reportlab
                logger.warning("LibreOffice not found, trying reportlab conversion")

                try:
                    from docx2pdf import convert
                    convert(docx_path, pdf_path)
                    logger.info(f"PDF generated via reportlab: {pdf_path}")
                    return True, str(pdf_path)
                except ImportError:
                    logger.error("docx2pdf not installed")
                    return False, "PDF conversion failed: docx2pdf not installed"

        except Exception as e:
            logger.error(f"Error converting DOCX to PDF: {e}")
            return False, f"PDF conversion error: {str(e)}"

    @staticmethod
    def create_contract(template_path: str, contract_data: Dict[str, Any],
                       output_dir: Optional[str] = None,
                       generate_pdf: bool = True) -> Tuple[bool, Dict[str, Any]]:
        """
        Convenience method: generate both DOCX and PDF in one call

        Returns:
            Tuple of (success: bool, result_dict)
        """
        generator = ContractGenerator(template_path)

        # Generate DOCX
        success, result = generator.generate_contract(contract_data, output_dir)
        if not success:
            return False, result

        docx_path = result['docx_path']
        pdf_path = None

        # Generate PDF if requested
        if generate_pdf and docx_path:
            pdf_filename = Path(docx_path).stem + '.pdf'
            pdf_path = str(Path(docx_path).parent / pdf_filename)

            success, error = ContractGenerator.docx_to_pdf(docx_path, pdf_path)
            if not success:
                logger.warning(f"PDF generation failed: {error}")
                pdf_path = None

        result['pdf_path'] = pdf_path
        return True, result


# Test/Usage Examples
if __name__ == "__main__":
    # Example usage
    template_path = "path/to/template.docx"

    contract_data = {
        'contract_number': '2026-09-29_001',
        'date': '29.09.2026',
        'buyer_name': 'ABC MCHJ',
        'buyer_inn': '123456789',
        'buyer_address': 'Tashkent, Uzbekistan',
        'buyer_bank': 'Asian Development Bank',
        'buyer_account': '12345678901234567890',
        'buyer_mfo': '12345',
        'buyer_director': 'John Doe',
        'seller_name': 'XYZ Corp',
        'seller_inn': '987654321',
        'seller_address': 'Bukhara, Uzbekistan',
        'seller_bank': 'National Bank of Uzbekistan',
        'seller_account': '09876543210987654321',
        'seller_mfo': '54321',
        'seller_director': 'Jane Smith',
        'service_type': 'Avtousluga',
        'service_description': 'Car rental services',
        'amount': 500000000,
        'amount_words': 'Besh yuz million sўm',
        'vat_status': 'NDS bilan'
    }

    # Method 1: Using ContractGenerator class
    generator = ContractGenerator(template_path)
    success, result = generator.generate_contract(contract_data)

    if success:
        print(f"DOCX generated: {result['docx_path']}")
    else:
        print(f"Errors: {result['errors']}")

    # Method 2: One-call method with PDF generation
    success, result = ContractGenerator.create_contract(
        template_path,
        contract_data,
        generate_pdf=True
    )

    if success:
        print(f"Contract generated:")
        print(f"  DOCX: {result['docx_path']}")
        print(f"  PDF: {result['pdf_path']}")
    else:
        print(f"Errors: {result['errors']}")
