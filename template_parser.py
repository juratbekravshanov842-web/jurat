"""
Template Parser - Word (.docx) template manipulation
Handles placeholder replacement while preserving formatting
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from docx import Document
from docx.oxml import OxmlElement
import logging

logger = logging.getLogger(__name__)


class TemplateParser:
    """Parse and manipulate Word (.docx) templates with placeholder replacement"""

    # Placeholder pattern: {{PLACEHOLDER_NAME}}
    PLACEHOLDER_PATTERN = r'\{\{([A-Z_]+)\}\}'

    def __init__(self, template_path: str):
        """Initialize template parser with path to .docx file"""
        self.template_path = Path(template_path)
        self.document = None
        self.placeholders = []
        self.load_template()
        self._scan_placeholders()

    def load_template(self) -> bool:
        """Load Word document from file"""
        try:
            if not self.template_path.exists():
                logger.error(f"Template not found: {self.template_path}")
                return False

            self.document = Document(self.template_path)
            logger.info(f"Template loaded: {self.template_path}")
            return True

        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return False

    def _scan_placeholders(self):
        """Scan document for all placeholders"""
        self.placeholders = []

        # Scan paragraphs
        for paragraph in self.document.paragraphs:
            matches = re.findall(self.PLACEHOLDER_PATTERN, paragraph.text)
            self.placeholders.extend(matches)

        # Scan table cells
        for table in self.document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        matches = re.findall(self.PLACEHOLDER_PATTERN, paragraph.text)
                        self.placeholders.extend(matches)

        # Remove duplicates and sort
        self.placeholders = sorted(list(set(self.placeholders)))
        logger.info(f"Found {len(self.placeholders)} unique placeholders: {self.placeholders}")

    def get_placeholders(self) -> List[str]:
        """Get list of all placeholders in template"""
        return self.placeholders.copy()

    def replace_placeholder_in_paragraph(self, paragraph, placeholder: str, replacement: str) -> bool:
        """
        Replace placeholder in a single paragraph while preserving run formatting

        Handles cases where placeholder spans multiple runs
        """
        try:
            placeholder_pattern = r'\{\{' + re.escape(placeholder) + r'\}\}'

            # Check if placeholder exists in paragraph
            if not re.search(placeholder_pattern, paragraph.text):
                return True  # Not in this paragraph, that's OK

            # Try simple replacement if placeholder is in single run
            for run in paragraph.runs:
                if re.search(placeholder_pattern, run.text):
                    run.text = re.sub(placeholder_pattern, replacement, run.text)
                    return True

            # Handle case where placeholder spans multiple runs
            # Reconstruct paragraph text
            full_text = paragraph.text
            new_text = re.sub(placeholder_pattern, replacement, full_text)

            if new_text != full_text:
                # Clear existing runs
                for run in paragraph.runs:
                    r = run._element
                    r.getparent().remove(r)

                # Add new run with replacement text
                new_run = paragraph.add_run(new_text)

                # Try to preserve formatting from first original run if it existed
                if paragraph.runs and len(paragraph.runs) > 0:
                    first_run = paragraph.runs[0]
                    if first_run._element.rPr is not None:
                        new_run._element.rPr = first_run._element.rPr

                return True

            return True

        except Exception as e:
            logger.error(f"Error replacing placeholder {placeholder} in paragraph: {e}")
            return False

    def replace_in_document(self, replacements: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Replace all placeholders in document

        Args:
            replacements: Dict of {placeholder_name: replacement_value}

        Returns:
            Tuple of (success: bool, errors: List[str])
        """
        errors = []

        if not self.document:
            errors.append("Document not loaded")
            return False, errors

        try:
            # Replace in paragraphs
            for paragraph in self.document.paragraphs:
                for placeholder, replacement in replacements.items():
                    success = self.replace_placeholder_in_paragraph(
                        paragraph,
                        placeholder,
                        str(replacement) if replacement else ""
                    )
                    if not success:
                        errors.append(f"Failed to replace {placeholder} in paragraph")

            # Replace in table cells
            for table in self.document.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            for placeholder, replacement in replacements.items():
                                success = self.replace_placeholder_in_paragraph(
                                    paragraph,
                                    placeholder,
                                    str(replacement) if replacement else ""
                                )
                                if not success:
                                    errors.append(f"Failed to replace {placeholder} in table cell")

            return len(errors) == 0, errors

        except Exception as e:
            logger.error(f"Error replacing in document: {e}")
            errors.append(f"Document replacement error: {str(e)}")
            return False, errors

    def save_to_docx(self, output_path: str) -> bool:
        """
        Save modified document to output path

        Preserves all formatting, styles, tables, and structure
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            self.document.save(output_file)
            logger.info(f"Document saved: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving document: {e}")
            return False

    def get_document_info(self) -> Dict[str, any]:
        """Get information about document structure"""
        if not self.document:
            return {}

        return {
            'paragraphs': len(self.document.paragraphs),
            'tables': len(self.document.tables),
            'placeholders': len(self.placeholders),
            'placeholder_names': self.placeholders,
            'sections': len(self.document.sections),
            'core_properties': {
                'title': self.document.core_properties.title,
                'author': self.document.core_properties.author,
                'created': str(self.document.core_properties.created),
            }
        }

    @classmethod
    def create_from_template(cls, template_path: str, replacements: Dict[str, str],
                            output_path: str) -> Tuple[bool, List[str]]:
        """
        Convenience method: load template, replace placeholders, save to output

        Returns:
            Tuple of (success: bool, errors: List[str])
        """
        try:
            # Load template
            parser = cls(template_path)

            # Replace placeholders
            success, errors = parser.replace_in_document(replacements)
            if not success:
                logger.error(f"Replacement failed: {errors}")
                return False, errors

            # Save output
            if not parser.save_to_docx(output_path):
                errors.append(f"Failed to save document to {output_path}")
                return False, errors

            logger.info(f"Template processed successfully: {template_path} → {output_path}")
            return True, []

        except Exception as e:
            logger.error(f"Error in create_from_template: {e}")
            return False, [str(e)]


class TemplateAnalyzer:
    """Analyze template structure for debugging and validation"""

    def __init__(self, template_path: str):
        """Initialize analyzer"""
        self.template_path = Path(template_path)
        self.document = None
        self.load()

    def load(self):
        """Load document"""
        try:
            if self.template_path.exists():
                self.document = Document(self.template_path)
                logger.info(f"Document loaded for analysis: {self.template_path}")
        except Exception as e:
            logger.error(f"Error loading document: {e}")

    def analyze_paragraphs(self) -> List[Dict]:
        """Analyze all paragraphs in document"""
        if not self.document:
            return []

        paragraphs = []
        for idx, para in enumerate(self.document.paragraphs):
            paragraphs.append({
                'index': idx,
                'text': para.text[:100],  # First 100 chars
                'length': len(para.text),
                'runs': len(para.runs),
                'style': para.style.name if para.style else 'None'
            })

        return paragraphs

    def analyze_tables(self) -> List[Dict]:
        """Analyze all tables in document"""
        if not self.document:
            return []

        tables = []
        for idx, table in enumerate(self.document.tables):
            cell_count = sum(len(row.cells) for row in table.rows)
            tables.append({
                'index': idx,
                'rows': len(table.rows),
                'columns': len(table.columns) if table.columns else 0,
                'total_cells': cell_count
            })

        return tables

    def get_full_report(self) -> Dict:
        """Get comprehensive analysis report"""
        return {
            'file': str(self.template_path),
            'exists': self.template_path.exists(),
            'size_bytes': self.template_path.stat().st_size if self.template_path.exists() else 0,
            'paragraphs_count': len(self.document.paragraphs) if self.document else 0,
            'tables_count': len(self.document.tables) if self.document else 0,
            'paragraphs': self.analyze_paragraphs(),
            'tables': self.analyze_tables()
        }


# Test/Usage Examples
if __name__ == "__main__":
    # Example usage
    template_path = "path/to/template.docx"
    output_path = "path/to/output.docx"

    # Method 1: Using TemplateParser class
    parser = TemplateParser(template_path)

    print("Placeholders found:")
    for placeholder in parser.get_placeholders():
        print(f"  - {placeholder}")

    replacements = {
        'CONTRACT_NUMBER': '2026-09-29_001',
        'BUYER_NAME': 'ABC MCHJ',
        'BUYER_INN': '123456789',
        'AMOUNT': '500 000 000',
        'AMOUNT_WORDS': 'Besh yuz million sўm'
    }

    success, errors = parser.replace_in_document(replacements)
    if success:
        parser.save_to_docx(output_path)
        print(f"Template processed successfully → {output_path}")
    else:
        print(f"Errors: {errors}")

    # Method 2: One-call convenience method
    success, errors = TemplateParser.create_from_template(
        template_path,
        replacements,
        output_path
    )

    # Method 3: Analyze template structure
    analyzer = TemplateAnalyzer(template_path)
    report = analyzer.get_full_report()
    print(f"\nTemplate Analysis:")
    print(f"  Paragraphs: {report['paragraphs_count']}")
    print(f"  Tables: {report['tables_count']}")
