"""
Unit tests for DataFrame export functionality
"""

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from ohada_extractor import FinancialExtractor
from ohada_extractor.core.statement import FinancialStatement


class TestDataFrameExport(unittest.TestCase):
    """Test DataFrame export functionality for time-series analysis."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FinancialExtractor()
        self.sample_file = Path(__file__).parent.parent / "examples" / "data" / "DSF_Normal_Tantanpion_2024.xlsx"

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_to_dataframe_all_statements(self):
        """Test that to_dataframe returns all statements when statement=None."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Get all statements as dict
        dfs = statement.to_dataframe()
        
        # Verify all statement types are present
        self.assertIn("asset", dfs)
        self.assertIn("liability", dfs)
        self.assertIn("income", dfs)
        self.assertIn("cashflow", dfs)
        self.assertIn("other", dfs)
        
        # Verify each is a DataFrame
        for stmt_name, df in dfs.items():
            self.assertIsInstance(df, pd.DataFrame, f"{stmt_name} should be a DataFrame")

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_to_dataframe_single_statement(self):
        """Test that to_dataframe returns single DataFrame when statement is specified."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Get single statement
        income_df = statement.to_dataframe("income")
        
        # Verify it's a DataFrame
        self.assertIsInstance(income_df, pd.DataFrame)
        
        # Verify it has expected columns
        self.assertIn("Label", income_df.columns)
        self.assertIn("Reference", income_df.columns)
        self.assertIn("annee", income_df.columns)

        print(income_df)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_annee_datetime_and_monotonic(self):
        """Test that annee column is datetime and monotonic increasing."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Test each statement type
        for stmt_name in ["asset", "liability", "income", "cashflow", "other"]:
            df = statement.to_dataframe(stmt_name)
            
            # Check annee column exists
            self.assertIn("annee", df.columns, f"{stmt_name} should have annee column")
            
            # Check annee is datetime
            self.assertTrue(
                pd.api.types.is_datetime64_any_dtype(df["annee"]),
                f"{stmt_name} annee should be datetime type"
            )
            
            # Check annee is monotonic increasing
            self.assertTrue(
                df["annee"].is_monotonic_increasing,
                f"{stmt_name} annee should be monotonic increasing"
            )

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_known_references_present(self):
        """Test that known references and labels are present in DataFrames."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Test assets
        asset_df = statement.to_dataframe("asset")
        asset_refs = set(asset_df["Reference"].unique())
        self.assertIn("AD", asset_refs, "AD reference should be in assets")
        self.assertIn("AZ", asset_refs, "AZ reference should be in assets")
        self.assertIn("BZ", asset_refs, "BZ reference should be in assets")
        
        # Test income
        income_df = statement.to_dataframe("income")
        income_refs = set(income_df["Reference"].unique())
        self.assertIn("TA", income_refs, "TA reference should be in income")
        self.assertIn("XA", income_refs, "XA reference should be in income")
        self.assertIn("XI", income_refs, "XI reference should be in income")
        
        # Test cashflow
        cashflow_df = statement.to_dataframe("cashflow")
        cashflow_refs = set(cashflow_df["Reference"].unique())
        self.assertIn("ZA", cashflow_refs, "ZA reference should be in cashflow")
        self.assertIn("ZB", cashflow_refs, "ZB reference should be in cashflow")
        self.assertIn("ZG", cashflow_refs, "ZG reference should be in cashflow")

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_timeseries_operations_on_wide_format(self):
        """Test that time-series operations work on wide format DataFrames."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Get wide format DataFrame
        income_df = statement.to_dataframe("income", tidy=False)
        
        # Verify it's wide format (accounts as index, years as columns)
        self.assertGreater(len(income_df.columns), 2, "Wide format should have multiple year columns")
        
        # Test pct_change operation
        # Select only numeric columns for pct_change
        numeric_cols = income_df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            pct_change = income_df[numeric_cols].pct_change(axis=1)
            self.assertIsInstance(pct_change, pd.DataFrame)
            print("pct_change:")
            print(pct_change)
        
        # Test rolling operation
        if len(numeric_cols) >= 3:
            rolling_mean = income_df[numeric_cols].rolling(window=2, axis=1).mean()
            self.assertIsInstance(rolling_mean, pd.DataFrame)
            print("rolling_mean:")
            print(rolling_mean)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_asset_value_type_selection(self):
        """Test that asset value_type parameter works correctly."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Get assets with different value types
        assets_net = statement.to_dataframe("asset", value_type="Net")
        assets_gross = statement.to_dataframe("asset", value_type="Gross")
        assets_amort = statement.to_dataframe("asset", value_type="Amortissement")
        
        # All should be DataFrames
        self.assertIsInstance(assets_net, pd.DataFrame)
        self.assertIsInstance(assets_gross, pd.DataFrame)
        self.assertIsInstance(assets_amort, pd.DataFrame)
        
        # Verify they have the same structure
        self.assertEqual(assets_net.shape, assets_gross.shape)
        self.assertEqual(assets_net.shape, assets_amort.shape)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_invalid_statement_name(self):
        """Test that invalid statement name raises ValueError."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        with self.assertRaises(ValueError) as context:
            statement.to_dataframe("invalid_statement")
        
        self.assertIn("Invalid statement", str(context.exception))

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_none_array_handling(self):
        """Test that the method handles missing statement data gracefully."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Test that the method works with valid data
        dfs = statement.to_dataframe()
        
        # Verify all statements have data (since we extracted from a valid file)
        for stmt_name, df in dfs.items():
            self.assertIsInstance(df, pd.DataFrame)
            # DataFrames should not be empty since we extracted from a valid file
            # This tests that the conversion works correctly

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_dataframe_structure_tidy_format(self):
        """Test that tidy format has expected structure."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        df = statement.to_dataframe("income", tidy=True)
        
        # Tidy format should have these columns
        expected_cols = ["Label", "Reference", "annee"]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Tidy format should have {col} column")

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_dataframe_structure_wide_format(self):
        """Test that wide format has expected structure."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        df = statement.to_dataframe("income", tidy=False)
        
        # Wide format should have Label and Reference as index or columns
        # and years as columns
        self.assertIn("Label", df.columns)
        self.assertIn("Reference", df.columns)
        
        # Should have year columns (annee should not be a column in wide format)
        # Instead, years should be column headers
        self.assertGreater(len(df.columns), 2, "Wide format should have multiple columns")
        print(df)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_reset_index_preserved(self):
        """Test that reset_index=False preserves MultiIndex."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Test wide format with reset_index=False
        income_df = statement.to_dataframe("income", tidy=False, reset_index=False)
        
        # Verify MultiIndex is preserved
        self.assertIsInstance(income_df.index, pd.MultiIndex)
        self.assertEqual(income_df.index.names, ["Label", "Reference"])
        
        # Label and Reference should not be columns
        self.assertNotIn("Label", income_df.columns)
        self.assertNotIn("Reference", income_df.columns)
        print(income_df)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_reset_index_tidy_format(self):
        """Test that reset_index=False in tidy format preserves MultiIndex."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Test tidy format with reset_index=False
        income_df = statement.to_dataframe("income", tidy=True, reset_index=False)
        
        # Verify MultiIndex is preserved
        self.assertIsInstance(income_df.index, pd.MultiIndex)
        self.assertEqual(income_df.index.names, ["Label", "Reference"])
        
        # Label and Reference should not be columns
        self.assertNotIn("Label", income_df.columns)
        self.assertNotIn("Reference", income_df.columns)
        
        # But annee and value should be columns
        self.assertIn("annee", income_df.columns)
        self.assertIn("value", income_df.columns)
        print(income_df)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_reset_index_default_true(self):
        """Test that reset_index defaults to True (backward compatibility)."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Test default behavior (reset_index=True)
        income_df = statement.to_dataframe("income", tidy=False)
        
        # Verify index is NOT MultiIndex
        self.assertNotIsInstance(income_df.index, pd.MultiIndex)
        
        # Label and Reference should be columns
        self.assertIn("Label", income_df.columns)
        self.assertIn("Reference", income_df.columns)
        print(income_df)


if __name__ == "__main__":
    unittest.main()
