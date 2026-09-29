"""
Contract Validator - Comprehensive validation before contract generation
"""

import re
from datetime import datetime
from typing import Tuple, List, Dict, Any
from config import (
    VALIDATION_RULES,
    INN_PATTERN,
    DEFAULT_SERVICE_TYPES,
    VAT_STATUSES
)


class ContractValidator:
    """Validate contract data before generation"""

    # Error messages (Uzbek)
    ERRORS = {
        'empty_field': '{field} to\'ldirilmadi',
        'invalid_format': '{field} noto\'g\'ri formatda',
        'too_short': '{field} juda qisqa (min: {min})',
        'too_long': '{field} juda uzun (max: {max})',
        'invalid_inn': 'INN noto\'g\'ri: {inn}',
        'inn_mismatch': 'INN va korxona nomi mos kelmadi',
        'invalid_amount': 'Summa noto\'g\'ri: {amount}',
        'amount_too_small': 'Summa juda kichik (min: {min})',
        'amount_too_large': 'Summa juda katta (max: {max})',
        'invalid_account': 'Hisob raqami noto\'g\'ri (20 ta raqam kerak)',
        'invalid_mfo': 'MFO noto\'g\'ri (5 ta raqam kerak)',
        'duplicate_parties': 'Buyurtmachi va Bajaruvchi bir xil bo\'la olmaydi',
        'invalid_date': 'Sana noto\'g\'ri',
        'future_date': 'Sana tukundan keyin bo\'la olmaydi',
        'invalid_service': 'Xizmat turi noto\'g\'ri',
        'vat_not_selected': 'NDS holati tanlanmadi',
        'template_not_found': 'Shablon topilmadi',
        'invalid_contract_number': 'Shartnoma raqami noto\'g\'ri'
    }

    @staticmethod
    def validate_company_name(name: str) -> Tuple[bool, str]:
        """Validate company name"""
        if not name or not name.strip():
            return False, ContractValidator.ERRORS['empty_field'].format(field='Korxona nomi')

        name = name.strip()
        min_len = VALIDATION_RULES['company_name_min_length']
        max_len = VALIDATION_RULES['company_name_max_length']

        if len(name) < min_len:
            return False, ContractValidator.ERRORS['too_short'].format(
                field='Korxona nomi',
                min=min_len
            )

        if len(name) > max_len:
            return False, ContractValidator.ERRORS['too_long'].format(
                field='Korxona nomi',
                max=max_len
            )

        # Check for invalid characters (only allow letters, numbers, spaces, and common separators)
        if not re.match(r'^[А-Яа-яЎўЃғҚқҚ\w\s\.\-\"\']+$', name):
            return False, ContractValidator.ERRORS['invalid_format'].format(
                field='Korxona nomi'
            )

        return True, ""

    @staticmethod
    def validate_inn(inn: str) -> Tuple[bool, str]:
        """Validate INN format"""
        if not inn or not inn.strip():
            return False, ContractValidator.ERRORS['empty_field'].format(field='INN')

        inn = inn.strip()

        # Check format: must be 9 digits
        if not re.match(INN_PATTERN, inn):
            return False, ContractValidator.ERRORS['invalid_inn'].format(inn=inn)

        return True, ""

    @staticmethod
    def validate_address(address: str) -> Tuple[bool, str]:
        """Validate address"""
        if not address or not address.strip():
            return False, ContractValidator.ERRORS['empty_field'].format(field='Manzil')

        address = address.strip()
        min_len = VALIDATION_RULES['address_min_length']
        max_len = VALIDATION_RULES['address_max_length']

        if len(address) < min_len:
            return False, ContractValidator.ERRORS['too_short'].format(
                field='Manzil',
                min=min_len
            )

        if len(address) > max_len:
            return False, ContractValidator.ERRORS['too_long'].format(
                field='Manzil',
                max=max_len
            )

        return True, ""

    @staticmethod
    def validate_bank(bank: str) -> Tuple[bool, str]:
        """Validate bank name"""
        if not bank or not bank.strip():
            return False, ContractValidator.ERRORS['empty_field'].format(field='Bank')

        if len(bank.strip()) < 3:
            return False, ContractValidator.ERRORS['too_short'].format(
                field='Bank',
                min=3
            )

        return True, ""

    @staticmethod
    def validate_account(account: str) -> Tuple[bool, str]:
        """Validate account number"""
        if not account or not account.strip():
            return False, ContractValidator.ERRORS['empty_field'].format(field='Hisob raqami')

        # Remove spaces
        account = account.strip().replace(' ', '')

        # Must be digits only
        if not account.isdigit():
            return False, ContractValidator.ERRORS['invalid_account']

        # Uzbek account format: 20 digits
        required_len = VALIDATION_RULES['account_number_length']
        if len(account) != required_len:
            return False, ContractValidator.ERRORS['invalid_account']

        return True, ""

    @staticmethod
    def validate_mfo(mfo: str) -> Tuple[bool, str]:
        """Validate MFO (Bank code)"""
        if not mfo or not mfo.strip():
            return False, ContractValidator.ERRORS['empty_field'].format(field='MFO')

        mfo = mfo.strip()

        # Must be digits only
        if not mfo.isdigit():
            return False, ContractValidator.ERRORS['invalid_mfo']

        # Standard MFO length: 5 digits
        required_len = VALIDATION_RULES['mfo_length']
        if len(mfo) != required_len:
            return False, ContractValidator.ERRORS['invalid_mfo']

        return True, ""

    @staticmethod
    def validate_director(director: str) -> Tuple[bool, str]:
        """Validate director name"""
        if not director or not director.strip():
            return False, ContractValidator.ERRORS['empty_field'].format(field='Rahbari')

        director = director.strip()
        min_len = VALIDATION_RULES['director_name_min_length']
        max_len = VALIDATION_RULES['director_name_max_length']

        if len(director) < min_len:
            return False, ContractValidator.ERRORS['too_short'].format(
                field='Rahbari',
                min=min_len
            )

        if len(director) > max_len:
            return False, ContractValidator.ERRORS['too_long'].format(
                field='Rahbari',
                max=max_len
            )

        return True, ""

    @staticmethod
    def validate_amount(amount: Any) -> Tuple[bool, str]:
        """Validate contract amount"""
        try:
            if amount is None:
                return False, ContractValidator.ERRORS['empty_field'].format(field='Summa')

            # Convert to string and clean
            amount_str = str(amount).replace(' ', '').replace(',', '')

            # Must be digits
            if not amount_str.isdigit():
                return False, ContractValidator.ERRORS['invalid_amount'].format(amount=amount)

            amount_int = int(amount_str)

            min_amount = VALIDATION_RULES['min_amount']
            max_amount = VALIDATION_RULES['max_amount']

            if amount_int < min_amount:
                return False, ContractValidator.ERRORS['amount_too_small'].format(
                    min=min_amount
                )

            if amount_int > max_amount:
                return False, ContractValidator.ERRORS['amount_too_large'].format(
                    max=max_amount
                )

            return True, ""

        except Exception as e:
            return False, ContractValidator.ERRORS['invalid_amount'].format(amount=str(e))

    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, str]:
        """Validate contract date"""
        if not date_str or not date_str.strip():
            return False, ContractValidator.ERRORS['empty_field'].format(field='Sana')

        try:
            # Try parsing date in DD.MM.YYYY format
            date_obj = datetime.strptime(date_str.strip(), '%d.%m.%Y')

            # Check if date is not in the future
            today = datetime.now().date()
            if date_obj.date() > today:
                return False, ContractValidator.ERRORS['future_date']

            return True, ""

        except ValueError:
            return False, ContractValidator.ERRORS['invalid_date']

    @staticmethod
    def validate_contract_number(contract_number: str) -> Tuple[bool, str]:
        """Validate contract number"""
        if not contract_number or not contract_number.strip():
            return False, ContractValidator.ERRORS['empty_field'].format(field='Shartnoma raqami')

        number = contract_number.strip()
        min_len = VALIDATION_RULES['contract_number_min_length']
        max_len = VALIDATION_RULES['contract_number_max_length']

        if len(number) < min_len or len(number) > max_len:
            return False, ContractValidator.ERRORS['invalid_contract_number']

        return True, ""

    @staticmethod
    def validate_service_type(service_type: str) -> Tuple[bool, str]:
        """Validate service type"""
        if not service_type or not service_type.strip():
            return False, ContractValidator.ERRORS['empty_field'].format(field='Xizmat turi')

        service_type = service_type.strip()

        # Check if it's a valid service type or custom
        if service_type not in DEFAULT_SERVICE_TYPES:
            # Allow custom service types (not in predefined list)
            if len(service_type) < 3:
                return False, ContractValidator.ERRORS['invalid_service']

        return True, ""

    @staticmethod
    def validate_vat_status(vat_status: str) -> Tuple[bool, str]:
        """Validate VAT status"""
        if not vat_status or not vat_status.strip():
            return False, ContractValidator.ERRORS['vat_not_selected']

        vat_status = vat_status.strip()

        if vat_status not in VAT_STATUSES:
            return False, ContractValidator.ERRORS['vat_not_selected']

        return True, ""

    @staticmethod
    def validate_different_parties(buyer_id: int, seller_id: int) -> Tuple[bool, str]:
        """Validate that buyer and seller are different"""
        if buyer_id == seller_id:
            return False, ContractValidator.ERRORS['duplicate_parties']

        return True, ""

    @staticmethod
    def validate_inn_consistency(inn: str, company_name: str) -> Tuple[bool, str]:
        """
        Validate that INN and company name are consistent
        This is a basic check - real validation would call an API
        """
        # For now, just check that both are non-empty
        # In production, this would verify against official registry
        if not inn or not company_name:
            return False, "INN va korxona nomi mos kelmadi"

        return True, ""

    @classmethod
    def validate_complete_contract(cls, contract_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate complete contract data

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate Buyer
        valid, error = cls.validate_company_name(contract_data.get('buyer_name', ''))
        if not valid:
            errors.append(f"Buyurtmachi: {error}")

        valid, error = cls.validate_inn(contract_data.get('buyer_inn', ''))
        if not valid:
            errors.append(f"Buyurtmachi INN: {error}")

        valid, error = cls.validate_address(contract_data.get('buyer_address', ''))
        if not valid:
            errors.append(f"Buyurtmachi manzili: {error}")

        valid, error = cls.validate_bank(contract_data.get('buyer_bank', ''))
        if not valid:
            errors.append(f"Buyurtmachi banki: {error}")

        valid, error = cls.validate_account(contract_data.get('buyer_account', ''))
        if not valid:
            errors.append(f"Buyurtmachi hisob raqami: {error}")

        valid, error = cls.validate_mfo(contract_data.get('buyer_mfo', ''))
        if not valid:
            errors.append(f"Buyurtmachi MFO: {error}")

        valid, error = cls.validate_director(contract_data.get('buyer_director', ''))
        if not valid:
            errors.append(f"Buyurtmachi rahbari: {error}")

        # Validate Seller
        valid, error = cls.validate_company_name(contract_data.get('seller_name', ''))
        if not valid:
            errors.append(f"Bajaruvchi: {error}")

        valid, error = cls.validate_inn(contract_data.get('seller_inn', ''))
        if not valid:
            errors.append(f"Bajaruvchi INN: {error}")

        valid, error = cls.validate_address(contract_data.get('seller_address', ''))
        if not valid:
            errors.append(f"Bajaruvchi manzili: {error}")

        valid, error = cls.validate_bank(contract_data.get('seller_bank', ''))
        if not valid:
            errors.append(f"Bajaruvchi banki: {error}")

        valid, error = cls.validate_account(contract_data.get('seller_account', ''))
        if not valid:
            errors.append(f"Bajaruvchi hisob raqami: {error}")

        valid, error = cls.validate_mfo(contract_data.get('seller_mfo', ''))
        if not valid:
            errors.append(f"Bajaruvchi MFO: {error}")

        valid, error = cls.validate_director(contract_data.get('seller_director', ''))
        if not valid:
            errors.append(f"Bajaruvchi rahbari: {error}")

        # Validate Service and Amount
        valid, error = cls.validate_service_type(contract_data.get('service_type', ''))
        if not valid:
            errors.append(f"Xizmat turi: {error}")

        valid, error = cls.validate_amount(contract_data.get('amount'))
        if not valid:
            errors.append(f"Summa: {error}")

        # Validate Contract Details
        valid, error = cls.validate_date(contract_data.get('date', ''))
        if not valid:
            errors.append(f"Sana: {error}")

        valid, error = cls.validate_contract_number(contract_data.get('contract_number', ''))
        if not valid:
            errors.append(f"Shartnoma raqami: {error}")

        valid, error = cls.validate_vat_status(contract_data.get('vat_status', ''))
        if not valid:
            errors.append(f"NDS: {error}")

        # Validate parties are different
        buyer_id = contract_data.get('buyer_id')
        seller_id = contract_data.get('seller_id')
        if buyer_id and seller_id:
            valid, error = cls.validate_different_parties(buyer_id, seller_id)
            if not valid:
                errors.append(error)

        return len(errors) == 0, errors
