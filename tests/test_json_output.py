"""
Tests for JSON formatting
"""

import unittest
import json
import numpy as np
from src.ohada_extractor.formatters import OHADAJSONFormatter


class TestJSONFormatter(unittest.TestCase):
    """Test OHADAJSONFormatter class."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample arrays
        self.periods = ['2023-12-31', '2024-12-31']
        
        # Sample assets data (label, gross1, amort1, net1, gross2, amort2, net2)
        self.assets = np.array([
            ['AD', 100000, 50000, 50000, 110000, 55000, 55000],
            ['AE', 0, 0, 0, 0, 0, 0],
            ['BZ', 500000, 100000, 400000, 550000, 110000, 440000],
        ])
        
        # Sample liabilities data (label, net1, net2)
        self.liabilities = np.array([
            ['CA', 200000, 200000],
            ['CP', 300000, 350000],
            ['DZ', 500000, 550000],
        ])
        
        # Sample income data (label, net1, net2)
        self.income = np.array([
            ['TA', 1000000, 1100000],
            ['XI', 50000, 60000],
        ])
        
        # Sample cashflow data (label, net1, net2)
        self.cashflow = np.array([
            ['ZA', 50000, 60000],
            ['ZH', 60000, 70000],
        ])

    def test_numpy_to_serializable(self):
        """Test NumPy type conversion."""
        int_val = OHADAJSONFormatter.numpy_to_serializable(np.int64(42))
        self.assertEqual(int_val, 42)
        self.assertIsInstance(int_val, int)
        
        float_val = OHADAJSONFormatter.numpy_to_serializable(np.float64(3.14))
        self.assertAlmostEqual(float_val, 3.14)
        self.assertIsInstance(float_val, float)

    def test_format_assets(self):
        """Test asset formatting."""
        from src.ohada_extractor.core.schemas import ASSETS_ACCOUNTS
        
        result = OHADAJSONFormatter.format_assets(
            self.assets,
            self.periods,
            ASSETS_ACCOUNTS
        )
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['reference'], 'AD')
        self.assertIn('gross', result[0])
        self.assertIn('amort', result[0])
        self.assertIn('net', result[0])
        self.assertIn('gross1', result[0])
        self.assertIn('amort1', result[0])
        self.assertIn('net1', result[0])

    def test_json_serializable(self):
        """Test that formatted output is JSON serializable."""
        data = OHADAJSONFormatter.format_statement_data(
            self.assets,
            self.liabilities,
            self.income,
            self.cashflow,
            self.periods
        )
        
        # Should not raise exception
        json_str = json.dumps(data, default=OHADAJSONFormatter.numpy_to_serializable)
        self.assertIsInstance(json_str, str)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        self.assertIn('balance_sheet', parsed)
        self.assertIn('income_statement', parsed)
        self.assertIn('cashflow_statement', parsed)


if __name__ == '__main__':
    unittest.main()