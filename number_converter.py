"""
Number Converter - Format amounts and convert to words
Uzbek language support with Cyrillic output
"""

from typing import Tuple


class NumberConverter:
    """Convert numbers to formatted strings and Uzbek words"""

    # Uzbek digit words in Cyrillic
    ONES = {
        0: '',
        1: 'Бир',
        2: 'Икки',
        3: 'Уч',
        4: 'Тўрт',
        5: 'Беш',
        6: 'Олти',
        7: 'Ёт',
        8: 'Саккиз',
        9: 'Тўйин'
    }

    TENS = {
        0: '',
        1: 'ўн',  # 10-19 special case
        2: 'Йигирма',
        3: 'Ўттиз',
        4: 'Қирқ',
        5: 'Эллик',
        6: 'Олтмиш',
        7: 'Йттамиш',
        8: 'Саксон',
        9: 'Тўқсон'
    }

    TEENS = {
        10: 'Ўн',
        11: 'ўн бир',
        12: 'ўн икки',
        13: 'ўн уч',
        14: 'ўн тўрт',
        15: 'ўн беш',
        16: 'ўн олти',
        17: 'ўн ёт',
        18: 'ўн саккиз',
        19: 'ўн тўйин'
    }

    SCALES = [
        (1000000000, 'миллиард'),
        (1000000, 'миллион'),
        (1000, 'минг'),
    ]

    @classmethod
    def format_with_spaces(cls, number: int) -> str:
        """
        Format number with spaces for thousands
        500000000 -> "500 000 000"
        """
        if not isinstance(number, int) or number < 0:
            return str(number)

        formatted = f"{number:,}".replace(',', ' ')
        return formatted

    @classmethod
    def to_cyrillic_words(cls, number: int) -> str:
        """
        Convert number to Uzbek words in Cyrillic
        500000000 -> "Бeш yuz million so'm"
        """
        if number == 0:
            return 'Нол'

        if number < 0:
            return 'Минус ' + cls.to_cyrillic_words(abs(number))

        # Split into groups
        result = []
        remaining = number

        for scale_value, scale_name in cls.SCALES:
            if remaining >= scale_value:
                group_value = remaining // scale_value
                remaining = remaining % scale_value

                # Convert group to words
                group_words = cls._convert_group_to_words(group_value)
                result.append(f"{group_words} {scale_name}")

        # Handle remainder (0-999)
        if remaining > 0:
            group_words = cls._convert_group_to_words(remaining)
            result.append(group_words)

        # Join and format
        text = ' '.join(result)

        # Add currency
        return f"{text} сўм"

    @classmethod
    def _convert_group_to_words(cls, number: int) -> str:
        """
        Convert number 0-999 to words
        """
        if number == 0:
            return ''

        if number < 10:
            return cls.ONES[number]

        if 10 <= number <= 19:
            return cls.TEENS[number]

        if number < 100:
            tens_digit = number // 10
            ones_digit = number % 10
            result = cls.TENS[tens_digit]
            if ones_digit > 0:
                result += ' ' + cls.ONES[ones_digit]
            return result

        # 100-999
        hundreds = number // 100
        remainder = number % 100

        result = f"{cls.ONES[hundreds]} юз"

        if remainder > 0:
            result += ' ' + cls._convert_group_to_words(remainder)

        return result

    @classmethod
    def convert_amount(cls, amount_str: str) -> Tuple[str, str]:
        """
        Convert amount string to formatted and word versions

        Returns:
            Tuple of (formatted_with_spaces, words_in_cyrillic)
        """
        try:
            # Remove any existing spaces
            amount_clean = amount_str.replace(' ', '').replace(',', '')

            # Convert to integer
            amount_int = int(amount_clean)

            if amount_int < 0:
                raise ValueError("Amount cannot be negative")

            # Format with spaces
            formatted = cls.format_with_spaces(amount_int)

            # Convert to words
            words = cls.to_cyrillic_words(amount_int)

            return formatted, words

        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid amount format: {amount_str}") from e

    @staticmethod
    def validate_amount(amount: str) -> Tuple[bool, str]:
        """
        Validate amount format

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Remove spaces and commas
            clean = amount.replace(' ', '').replace(',', '')

            # Must be digits only
            if not clean.isdigit():
                return False, "Amount must contain only digits"

            # Convert to integer
            amount_int = int(clean)

            # Check minimum
            if amount_int < 1000:
                return False, "Amount must be at least 1,000"

            # Check maximum (9999999999999 - 13 nines)
            if amount_int > 9999999999999:
                return False, "Amount is too large"

            return True, ""

        except Exception as e:
            return False, str(e)


# Test/Usage Examples
if __name__ == "__main__":
    test_amounts = [
        500000000,
        4000000000,
        425000000,
        3000000000,
        12345,
        1000,
        999999999999
    ]

    for amount in test_amounts:
        formatted, words = NumberConverter.convert_amount(str(amount))
        print(f"\nAmount: {amount}")
        print(f"Formatted: {formatted} so'm")
        print(f"Words: {words}")
