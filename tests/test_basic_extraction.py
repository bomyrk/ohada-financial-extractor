"""
Unit tests for basic extraction functionality
"""

import unittest
from pathlib import Path

import numpy as np

from ohada_extractor import FinancialExtractor
from ohada_extractor.core.schemas import OHADA_STATEMENTS
from ohada_extractor.core.statement import FinancialStatement


class TestFinancialExtractor(unittest.TestCase):
    """Test FinancialExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FinancialExtractor()
        self.sample_file = Path(__file__).parent.parent / "examples" / "data" / "DSF_Normal_Tantanpion_2024.xlsx"

    def test_extractor_initialization(self):
        """Test that extractor initializes correctly."""
        self.assertIsNone(self.extractor._workbook)
        self.assertEqual(len(self.extractor._raw_data), 0)

    def test_schemas_defined(self):
        """Test that all required statements are defined."""
        required_statements = [
            "assets_sheet",
            "liabilities_sheet",
            "income_statement",
            "cashflow",
        ]
        for stmt in required_statements:
            self.assertIn(stmt, OHADA_STATEMENTS)

    def test_assets_schema(self):
        """Test assets schema configuration."""
        assets = OHADA_STATEMENTS["assets_sheet"]
        self.assertEqual(assets.name, "Balance Sheet Assets")
        self.assertEqual(assets.start_account, "AD")
        self.assertEqual(assets.end_account, "BZ")
        self.assertEqual(assets.account_count, 29)
        self.assertTrue(assets.has_value_types)

    def test_liabilities_schema(self):
        """Test liabilities schema configuration."""
        liab = OHADA_STATEMENTS["liabilities_sheet"]
        self.assertEqual(liab.name, "Balance Sheet Liability")
        self.assertEqual(liab.start_account, "CA")
        self.assertEqual(liab.end_account, "DZ")
        self.assertEqual(liab.account_count, 28)
        self.assertFalse(liab.has_value_types)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_extract_from_excel(self):
        """Test extraction from Excel file."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        self.assertIsNotNone(statement)
        self.assertIsNotNone(statement.periods)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_financial_statement_json_round_trip(self):
        """Test JSON persistence and xarray rebuild after loading."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        statement.build_metadata()
        original_report = statement.build_coherence_report()

        json_payload = statement.to_json_string(ensure_ascii=False)
        restored = FinancialStatement.from_json_string(json_payload)
        restored_report = restored.build_coherence_report()

        self.assertEqual(restored.periods, statement.periods)
        self.assertEqual(restored.file_path, statement.file_path)
        self.assertEqual(len(restored.notes), len(statement.notes))
        self.assertIsNotNone(restored.metadata)
        self.assertEqual(restored.metadata.legal_form, statement.metadata.legal_form)
        self.assertEqual(restored_report.total_checks, original_report.total_checks)
        self.assertEqual(restored_report.data_quality_score, original_report.data_quality_score)

        for key in ["asset", "liability", "income", "cashflow", "other"]:
            original = statement.arrays[key]
            round_tripped = restored.arrays[key]

            self.assertEqual(original.dims, round_tripped.dims)
            self.assertEqual(original.shape, round_tripped.shape)
            np.testing.assert_allclose(original.values, round_tripped.values, equal_nan=True)


class TestOHADAStatements(unittest.TestCase):
    """Test OHADA statement definitions."""

    def test_all_accounts_have_codes(self):
        """Test that all accounts have valid codes."""
        for _stmt_key, stmt in OHADA_STATEMENTS.items():
            for label, code in stmt.accounts:
                self.assertIsInstance(label, str)
                self.assertIsInstance(code, str)
                self.assertGreater(len(label), 0)
                self.assertGreater(len(code), 0)
                self.assertTrue(code.isupper() or code.isdigit())


if __name__ == "__main__":
    unittest.main()
