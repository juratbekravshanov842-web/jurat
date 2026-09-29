"""
INN Verifier - Validate and verify Uzbek STIR/INN numbers
"""

import re
from typing import Dict, Tuple, Optional
import logging

from config import INN_PATTERN, INN_LENGTH

logger = logging.getLogger(__name__)


class INNVerifier:
    """Verify Uzbek INN/STIR numbers"""

    # Uzbek INN format: 9 digits
    INN_FORMAT = INN_PATTERN

    def __init__(self):
        """Initialize INN verifier"""
        self.cache = {}  # Cache for API lookups

    @staticmethod
    def validate_format(inn: str) -> Tuple[bool, str]:
        """
        Validate INN format

        Uzbek INN: 9 digits (STIR/SHTIR)

        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not inn:
            return False, "INN bo'sh bo'lishi mumkin emas"

        inn = inn.strip().replace(' ', '').replace('-', '')

        # Check if it's 9 digits
        if not re.match(INNVerifier.INN_FORMAT, inn):
            return False, f"INN noto'g'ri format: {inn} (9 ta raqam kerak)"

        return True, ""

    @staticmethod
    def validate_checksum(inn: str) -> Tuple[bool, str]:
        """
        Validate INN checksum

        Uzbek INN uses a checksum algorithm
        Not fully implemented (API validation preferred)
        """
        valid, error = INNVerifier.validate_format(inn)
        if not valid:
            return False, error

        # Basic check: last digit should be valid
        # Full validation would require official algorithm
        # For now, accept any valid 9-digit format

        return True, ""

    async def lookup_online(self, inn: str) -> Tuple[bool, Dict[str, str]]:
        """
        Lookup INN in online registry

        This would connect to Uzbek government registry
        For now, returns placeholder (requires API access)

        Returns:
            Tuple of (found: bool, data: dict)
        """
        valid, error = self.validate_format(inn)
        if not valid:
            return False, {'error': error}

        # Check cache
        if inn in self.cache:
            cached_data = self.cache[inn]
            logger.info(f"INN {inn} found in cache")
            return True, cached_data

        try:
            # TODO: Implement actual API call to Uzbek registry
            # Example: https://api.gov.uz/endpoint/verification
            # This requires:
            # 1. API key from government
            # 2. HTTPS certificate
            # 3. Proper authentication

            # For now, return placeholder indicating API needed
            logger.warning(f"Online INN lookup not implemented. INN: {inn}")

            # Simulate successful lookup with placeholder data
            data = {
                'inn': inn,
                'name': 'ANIQLANMADI',
                'address': 'ANIQLANMADI',
                'status': 'ANIQLANMADI',
                'note': 'API qo\'shilishi kerak - Online tekshiruv amalga oshirilmadi'
            }

            self.cache[inn] = data
            return True, data

        except Exception as e:
            logger.error(f"Error looking up INN {inn}: {e}")
            return False, {'error': f'INN tekshiruvi xatosi: {str(e)}'}

    def verify_consistency(self, inn: str, company_name: str = None) -> Tuple[bool, str]:
        """
        Verify that INN is consistent with company name

        Basic check: both must be non-empty
        Advanced: would compare against registry

        Returns:
            Tuple of (is_consistent: bool, message: str)
        """
        # Format validation
        valid, error = self.validate_format(inn)
        if not valid:
            return False, error

        # Checksum validation
        valid, error = self.validate_checksum(inn)
        if not valid:
            return False, error

        # Company name check
        if company_name and company_name.strip():
            if len(company_name.strip()) < 3:
                return False, "Korxona nomi juda qisqa"
            return True, "Consistency check passed"
        else:
            return False, "Korxona nomi kerak"

    def full_verification(self, inn: str, company_name: str = None) -> Dict[str, any]:
        """
        Perform full INN verification

        Returns:
            Dictionary with verification results
        """
        result = {
            'inn': inn,
            'format_valid': False,
            'checksum_valid': False,
            'consistency_valid': False,
            'online_verified': False,
            'errors': [],
            'warnings': []
        }

        # 1. Format validation
        valid, error = self.validate_format(inn)
        result['format_valid'] = valid
        if not valid:
            result['errors'].append(error)
            return result

        # 2. Checksum validation
        valid, error = self.validate_checksum(inn)
        result['checksum_valid'] = valid
        if not valid:
            result['warnings'].append(error)

        # 3. Consistency check
        if company_name:
            valid, message = self.verify_consistency(inn, company_name)
            result['consistency_valid'] = valid
            if not valid:
                result['warnings'].append(message)

        # 4. Online verification (placeholder)
        logger.info(f"INN {inn} passed local validation. Online verification not implemented.")
        result['warnings'].append("Online API tekshiruvi qo'shilishi kerak")

        return result


class INNDatabase:
    """Local cache/database of known INNs"""

    def __init__(self):
        """Initialize INN database"""
        self.known_inns = {}

    def add(self, inn: str, company_data: Dict) -> bool:
        """Add INN to database"""
        valid, error = INNVerifier.validate_format(inn)
        if not valid:
            logger.error(f"Invalid INN format: {inn}")
            return False

        self.known_inns[inn] = company_data
        logger.info(f"INN added to database: {inn}")
        return True

    def get(self, inn: str) -> Optional[Dict]:
        """Get company data by INN"""
        valid, error = INNVerifier.validate_format(inn)
        if not valid:
            return None

        return self.known_inns.get(inn)

    def exists(self, inn: str) -> bool:
        """Check if INN exists in database"""
        valid, error = INNVerifier.validate_format(inn)
        if not valid:
            return False

        return inn in self.known_inns

    def update(self, inn: str, company_data: Dict) -> bool:
        """Update INN in database"""
        if not self.exists(inn):
            return self.add(inn, company_data)

        self.known_inns[inn].update(company_data)
        logger.info(f"INN updated in database: {inn}")
        return True

    def list_all(self) -> Dict[str, Dict]:
        """Get all INNs in database"""
        return self.known_inns.copy()


# Test/Usage Examples
if __name__ == "__main__":
    verifier = INNVerifier()
    db = INNDatabase()

    # Test INN validation
    test_inns = [
        '123456789',  # Valid format
        '12345678',   # Too short
        'abcdefghi',  # Invalid characters
        '123 456 789', # Valid with spaces
    ]

    print("INN Format Validation Tests:")
    for test_inn in test_inns:
        valid, error = verifier.validate_format(test_inn)
        print(f"  {test_inn}: {'✓' if valid else '✗'} {error}")

    # Test full verification
    print("\nFull Verification Test:")
    result = verifier.full_verification('123456789', 'ABC MCHJ')
    print(f"  Format: {'✓' if result['format_valid'] else '✗'}")
    print(f"  Checksum: {'✓' if result['checksum_valid'] else '✗'}")
    print(f"  Consistency: {'✓' if result['consistency_valid'] else '✗'}")

    # Test database
    print("\nDatabase Test:")
    company_data = {
        'name': 'ABC MCHJ',
        'address': 'Tashkent',
        'bank': 'Asian Development Bank'
    }

    db.add('123456789', company_data)
    retrieved = db.get('123456789')
    print(f"  Added and retrieved: {retrieved['name']}")
