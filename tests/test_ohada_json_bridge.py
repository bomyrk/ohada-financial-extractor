"""
Unit tests for OHADA JSON bridge methods on FinancialStatement
"""

import json
import unittest
from pathlib import Path

import numpy as np

from ohada_extractor import FinancialExtractor
from ohada_extractor.core.statement import FinancialStatement


class TestOHADAJSONBridge(unittest.TestCase):
    """Test OHADA JSON bridge methods on FinancialStatement."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FinancialExtractor()
        self.sample_file = Path(__file__).parent.parent / "examples" / "data" / "DSF_Normal_Tantanpion_2024.xlsx"

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_to_ohada_json_returns_string(self):
        """Test that to_ohada_json returns a JSON string."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Call the new method
        ohada_json_str = statement.to_ohada_json()
        
        # Assert it returns a string
        self.assertIsInstance(ohada_json_str, str)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_to_ohada_json_parsable(self):
        """Test that to_ohada_json output can be parsed by json.loads."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Call the new method
        ohada_json_str = statement.to_ohada_json()
        
        # Assert it parses successfully
        parsed = json.loads(ohada_json_str)
        self.assertIsInstance(parsed, dict)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_to_ohada_json_structure(self):
        """Test that to_ohada_json contains expected OHADA structure keys."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Call the new method
        ohada_json_str = statement.to_ohada_json()
        parsed = json.loads(ohada_json_str)
        
        # Assert the parsed structure contains expected keys
        self.assertIn("balance_sheet", parsed)
        self.assertIn("income_statement", parsed)
        self.assertIn("cashflow_statement", parsed)
        
        # Assert balance_sheet has assets and liabilities
        self.assertIn("assets", parsed["balance_sheet"])
        self.assertIn("liabilities", parsed["balance_sheet"])

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_to_ohada_dict_returns_dict(self):
        """Test that to_ohada_dict returns a dictionary."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Call the new method
        ohada_dict = statement.to_ohada_dict()
        
        # Assert it returns a dict
        self.assertIsInstance(ohada_dict, dict)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_to_ohada_dict_structure(self):
        """Test that to_ohada_dict contains expected OHADA structure keys."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Call the new method
        ohada_dict = statement.to_ohada_dict()
        
        # Assert the structure contains expected keys
        self.assertIn("balance_sheet", ohada_dict)
        self.assertIn("income_statement", ohada_dict)
        self.assertIn("cashflow_statement", ohada_dict)
        
        # Assert balance_sheet has assets and liabilities
        self.assertIn("assets", ohada_dict["balance_sheet"])
        self.assertIn("liabilities", ohada_dict["balance_sheet"])

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_to_ohada_json_and_dict_consistency(self):
        """Test that to_ohada_json and to_ohada_dict produce consistent structures."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Get both outputs
        ohada_dict = statement.to_ohada_dict()
        ohada_json_str = statement.to_ohada_json()
        parsed_json = json.loads(ohada_json_str)
        
        # They should have the same top-level keys
        self.assertEqual(set(ohada_dict.keys()), set(parsed_json.keys()))

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_existing_to_json_unchanged(self):
        """Test that existing to_json() still returns raw dict shape."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Call existing method
        raw_dict = statement.to_json()
        
        # Assert it returns a dict with original structure
        self.assertIsInstance(raw_dict, dict)
        self.assertIn("assets", raw_dict)
        self.assertIn("liabilities", raw_dict)
        self.assertIn("income", raw_dict)
        self.assertIn("cashflow", raw_dict)
        self.assertIn("other", raw_dict)
        self.assertIn("periods", raw_dict)
        self.assertIn("file_path", raw_dict)
        
        # Assert it does NOT have the OHADA structured keys
        self.assertNotIn("balance_sheet", raw_dict)
        self.assertNotIn("income_statement", raw_dict)
        self.assertNotIn("cashflow_statement", raw_dict)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_existing_to_dict_unchanged(self):
        """Test that existing to_dict() still returns raw dict shape."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Call existing method
        raw_dict = statement.to_dict()
        
        # Assert it returns a dict with original structure
        self.assertIsInstance(raw_dict, dict)
        self.assertIn("assets", raw_dict)
        self.assertIn("liabilities", raw_dict)
        self.assertIn("income", raw_dict)
        self.assertIn("cashflow", raw_dict)
        self.assertIn("other", raw_dict)
        self.assertIn("periods", raw_dict)
        self.assertIn("file_path", raw_dict)
        
        # Assert it does NOT have the OHADA structured keys
        self.assertNotIn("balance_sheet", raw_dict)
        self.assertNotIn("income_statement", raw_dict)
        self.assertNotIn("cashflow_statement", raw_dict)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_to_ohada_json_indent_parameter(self):
        """Test that to_ohada_json respects indent parameter."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Test with indent=0 (compact)
        compact_json = statement.to_ohada_json(indent=0)
        
        # Test with indent=4 (more spacing)
        spaced_json = statement.to_ohada_json(indent=4)
        
        # Spaced JSON should be longer due to indentation
        self.assertGreater(len(spaced_json), len(compact_json))

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_to_ohada_json_handles_nan(self):
        """Test that to_ohada_json handles NaN values correctly (converts to null)."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Get the JSON string
        ohada_json_str = statement.to_ohada_json()
        
        # Parse it back
        parsed = json.loads(ohada_json_str)
        
        # If there are any null values in the output, they should be valid JSON null
        # (json.loads will have converted them to Python None)
        # This test mainly ensures the JSON is valid and doesn't crash
        self.assertIsInstance(parsed, dict)


if __name__ == "__main__":
    unittest.main()
