"""
Unit tests for basic extraction functionality
"""

import unittest
import numpy as np
from pathlib import Path
from src.ohada_extractor import FinancialExtractor
from src.ohada_extractor.core.schemas import OHADA_STATEMENTS


class TestFinancialExtractor(unittest.TestCase):
    """Test FinancialExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FinancialExtractor()
        self.sample_file = Path(__file__).parent.parent / 'examples' / 'data' / 'sample_ohada_statement_2024.xlsx'

    def test_extractor_initialization(self):
        """Test that extractor initializes correctly."""
        self.assertIsNone(self.extractor.workbook)
        self.assertEqual(len(self.extractor.raw_data), 0)

    def test_schemas_defined(self):
        """Test that all required statements are defined."""
        required_statements = ['assets_sheet', 'liabilities_sheet', 'income_statement', 'cashflow']
        for stmt in required_statements:
            self.assertIn(stmt, OHADA_STATEMENTS)

    def test_assets_schema(self):
        """Test assets schema configuration."""
        assets = OHADA_STATEMENTS['assets_sheet']
        self.assertEqual(assets.name, 'Balance Sheet Asset')
        self.assertEqual(assets.start_account, 'AD')
        self.assertEqual(assets.end_account, 'BZ')
        self.assertEqual(assets.account_count, 29)
        self.assertTrue(assets.has_value_types)

    def test_liabilities_schema(self):
        """Test liabilities schema configuration."""
        liab = OHADA_STATEMENTS['liabilities_sheet']
        self.assertEqual(liab.name, 'Balance Sheet Liability')
        self.assertEqual(liab.start_account, 'CA')
        self.assertEqual(liab.end_account, 'DZ')
        self.assertEqual(liab.account_count, 28)
        self.assertFalse(liab.has_value_types)

    @unittest.skipIf(
        not Path('examples/data/sample_ohada_statement_2024.xlsx').exists(),
        "Sample data not available"
    )
    def test_extract_from_excel(self):
        """Test extraction from Excel file."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        self.assertIsNotNone(statement)
        self.assertIsNotNone(statement.periods)


class TestOHADAStatements(unittest.TestCase):
    """Test OHADA statement definitions."""
    
    def test_all_accounts_have_codes(self):
        """Test that all accounts have valid codes."""
        for stmt_key, stmt in OHADA_STATEMENTS.items():
            for label, code in stmt.accounts:
                self.assertIsInstance(label, str)
                self.assertIsInstance(code, str)
                self.assertGreater(len(label), 0)
                self.assertGreater(len(code), 0)
                self.assertTrue(code.isupper() or code.isdigit())


if __name__ == '__main__':
    unittest.main()