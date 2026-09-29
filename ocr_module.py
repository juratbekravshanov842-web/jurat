"""
OCR Module - Extract text from images using Google Vision API and Tesseract
"""

import os
import base64
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import json

from config import (
    GOOGLE_VISION_ENABLED,
    GOOGLE_VISION_CREDENTIALS_PATH,
    TESSERACT_PATH,
    USE_TESSERACT_FALLBACK,
    OCR_CONFIDENCE_THRESHOLD
)

logger = logging.getLogger(__name__)


class GoogleVisionOCR:
    """Google Cloud Vision API for OCR"""

    def __init__(self):
        """Initialize Google Vision client"""
        self.client = None
        self.enabled = False
        self.init_client()

    def init_client(self):
        """Initialize Google Vision API client"""
        if not GOOGLE_VISION_ENABLED:
            logger.warning("Google Vision API is disabled")
            return

        try:
            from google.cloud import vision
            from google.oauth2 import service_account

            # Check if credentials file exists
            if not Path(GOOGLE_VISION_CREDENTIALS_PATH).exists():
                logger.warning(f"Google credentials not found: {GOOGLE_VISION_CREDENTIALS_PATH}")
                return

            # Set environment variable for Google credentials
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(GOOGLE_VISION_CREDENTIALS_PATH)

            self.client = vision.ImageAnnotatorClient()
            self.enabled = True
            logger.info("Google Vision API initialized successfully")

        except ImportError:
            logger.warning("google-cloud-vision not installed")
        except Exception as e:
            logger.error(f"Error initializing Google Vision: {e}")

    def extract_text_from_image(self, image_path: str) -> Tuple[bool, str, float]:
        """
        Extract text from image using Google Vision API

        Returns:
            Tuple of (success: bool, text: str, confidence: float)
        """
        if not self.enabled:
            return False, "", 0.0

        try:
            from google.cloud import vision

            image_file = Path(image_path)
            if not image_file.exists():
                logger.error(f"Image file not found: {image_path}")
                return False, "", 0.0

            # Read image file
            with open(image_path, 'rb') as f:
                image_content = f.read()

            # Create image object
            image = vision.Image(content=image_content)

            # Perform text detection
            response = self.client.document_text_detection(image=image)

            # Extract full text
            full_text = response.full_text_annotation.text if response.full_text_annotation else ""

            # Calculate confidence from detected blocks
            confidence = self._calculate_confidence(response)

            if full_text:
                logger.info(f"Extracted {len(full_text)} characters from {image_path} (confidence: {confidence:.2f})")
                return True, full_text, confidence
            else:
                logger.warning(f"No text detected in {image_path}")
                return False, "", 0.0

        except Exception as e:
            logger.error(f"Error extracting text with Google Vision: {e}")
            return False, "", 0.0

    @staticmethod
    def _calculate_confidence(response) -> float:
        """Calculate confidence score from Google Vision response"""
        try:
            if not response.text_annotations:
                return 0.0

            # Calculate average confidence from all detected text blocks
            confidences = []
            for text_annotation in response.text_annotations[1:]:  # Skip first (full text)
                if hasattr(text_annotation, 'confidence'):
                    confidences.append(text_annotation.confidence)

            return sum(confidences) / len(confidences) if confidences else 0.5

        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5


class TesseractOCR:
    """Tesseract OCR fallback"""

    def __init__(self):
        """Initialize Tesseract"""
        self.available = False
        self.init_tesseract()

    def init_tesseract(self):
        """Initialize Tesseract engine"""
        if not USE_TESSERACT_FALLBACK:
            logger.warning("Tesseract fallback disabled")
            return

        try:
            import pytesseract
            from PIL import Image

            # Set Tesseract path for Windows
            if Path(TESSERACT_PATH).exists():
                pytesseract.pytesseract.pytesseract_cmd = TESSERACT_PATH

            self.available = True
            logger.info("Tesseract OCR initialized successfully")

        except ImportError:
            logger.warning("pytesseract or PIL not installed")
        except Exception as e:
            logger.error(f"Error initializing Tesseract: {e}")

    def extract_text_from_image(self, image_path: str) -> Tuple[bool, str, float]:
        """
        Extract text from image using Tesseract OCR

        Returns:
            Tuple of (success: bool, text: str, confidence: float)
        """
        if not self.available:
            return False, "", 0.0

        try:
            import pytesseract
            from PIL import Image

            image_file = Path(image_path)
            if not image_file.exists():
                logger.error(f"Image file not found: {image_path}")
                return False, "", 0.0

            # Open image
            image = Image.open(image_path)

            # Extract text
            text = pytesseract.image_to_string(image, lang='uzb+eng')

            # Get confidence data
            data = pytesseract.image_to_data(image, lang='uzb+eng')
            confidence = self._calculate_confidence(data)

            if text.strip():
                logger.info(f"Extracted {len(text)} characters from {image_path} via Tesseract (confidence: {confidence:.2f})")
                return True, text, confidence
            else:
                logger.warning(f"No text detected in {image_path} by Tesseract")
                return False, "", 0.0

        except Exception as e:
            logger.error(f"Error extracting text with Tesseract: {e}")
            return False, "", 0.0

    @staticmethod
    def _calculate_confidence(data: str) -> float:
        """Calculate confidence from Tesseract data output"""
        try:
            lines = data.split('\n')
            confidences = []

            for line in lines[1:]:  # Skip header
                parts = line.split('\t')
                if len(parts) >= 11:
                    try:
                        conf = float(parts[10])
                        if conf >= 0:  # Valid confidence
                            confidences.append(conf / 100.0)
                    except ValueError:
                        pass

            return sum(confidences) / len(confidences) if confidences else 0.5

        except Exception as e:
            logger.error(f"Error calculating Tesseract confidence: {e}")
            return 0.5


class OCREngine:
    """Main OCR engine - tries Google Vision first, falls back to Tesseract"""

    def __init__(self):
        """Initialize OCR engine"""
        self.google_vision = GoogleVisionOCR()
        self.tesseract = TesseractOCR()

    def extract_text(self, image_path: str) -> Tuple[bool, str, float, str]:
        """
        Extract text from image using best available method

        Returns:
            Tuple of (success: bool, text: str, confidence: float, method: str)
        """
        if not Path(image_path).exists():
            logger.error(f"Image file not found: {image_path}")
            return False, "", 0.0, "none"

        # Try Google Vision first
        if self.google_vision.enabled:
            success, text, confidence = self.google_vision.extract_text_from_image(image_path)
            if success and confidence >= OCR_CONFIDENCE_THRESHOLD:
                return success, text, confidence, "google_vision"

        # Fall back to Tesseract
        if self.tesseract.available:
            success, text, confidence = self.tesseract.extract_text_from_image(image_path)
            if success:
                return success, text, confidence, "tesseract"

        logger.error("No OCR method available")
        return False, "", 0.0, "none"

    def extract_fields(self, image_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Extract specific fields from image (INN, company name, etc.)

        Uses OCR and pattern matching
        """
        import re

        success, text, confidence, method = self.extract_text(image_path)

        if not success:
            return False, {}

        fields = self._extract_structured_fields(text)
        fields['ocr_confidence'] = confidence
        fields['ocr_method'] = method
        fields['full_text'] = text

        logger.info(f"Extracted fields: {list(fields.keys())}")

        return True, fields

    @staticmethod
    def _extract_structured_fields(text: str) -> Dict[str, str]:
        """Extract structured fields from OCR text using regex patterns"""
        fields = {}

        try:
            # INN pattern: 9 digits
            inn_match = re.search(r'\b(\d{9})\b', text)
            if inn_match:
                fields['inn'] = inn_match.group(1)

            # Company name patterns (Cyrillic text)
            # Look for text between common markers
            company_patterns = [
                r'Корхона номи:\s*([А-Яа-яЎўҚқ\s\w\-\.]+)',
                r'Компания:\s*([А-Яа-яЎўҚқ\s\w\-\.]+)',
                r'Юридик шахс:\s*([А-Яа-яЎўҚқ\s\w\-\.]+)'
            ]

            for pattern in company_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields['company_name'] = match.group(1).strip()
                    break

            # Account number pattern: 20 digits
            account_match = re.search(r'\b(\d{20})\b', text)
            if account_match:
                fields['account'] = account_match.group(1)

            # MFO pattern: 5 digits
            mfo_match = re.search(r'\bMFO[:\s]+(\d{5})\b', text, re.IGNORECASE)
            if mfo_match:
                fields['mfo'] = mfo_match.group(1)

            # Bank name (look for common bank names)
            bank_patterns = [
                r'Банк:\s*([А-Яа-яЎўҚқ\s\w\-\.&]+)',
                r'Bank:\s*([A-Za-z\s\-\.&]+)'
            ]

            for pattern in bank_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields['bank'] = match.group(1).strip()
                    break

            # Director name patterns
            director_patterns = [
                r'Раис:\s*([А-Яа-яЎўҚқ\s]+)',
                r'Директор:\s*([А-Яа-яЎўҚқ\s]+)',
                r'Director:\s*([A-Za-z\s]+)'
            ]

            for pattern in director_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields['director'] = match.group(1).strip()
                    break

            # Address patterns
            address_patterns = [
                r'Манзил:\s*([А-Яа-яЎўҚқ\d\s\,\.]+)',
                r'Address:\s*([A-Za-z\d\s\,\.]+)'
            ]

            for pattern in address_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields['address'] = match.group(1).strip()
                    break

            return fields

        except Exception as e:
            logger.error(f"Error extracting structured fields: {e}")
            return fields


# Test/Usage Examples
if __name__ == "__main__":
    engine = OCREngine()

    # Example: Extract text from image
    image_path = "path/to/rekvizit.jpg"

    # Method 1: Extract all text
    success, text, confidence, method = engine.extract_text(image_path)
    if success:
        print(f"Extracted text ({method}, confidence: {confidence:.2f}):")
        print(text[:500])

    # Method 2: Extract structured fields
    success, fields = engine.extract_fields(image_path)
    if success:
        print("\nExtracted fields:")
        for key, value in fields.items():
            if key != 'full_text':
                print(f"  {key}: {value}")
