"""
Unit tests for hierarchical JSON formatting functionality
"""

import unittest
from pathlib import Path

import numpy as np

from ohada_extractor import FinancialExtractor
from ohada_extractor.formatters.json_formatter import OHADAJSONFormatter


class TestHierarchicalFormatter(unittest.TestCase):
    """Test hierarchical formatting functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FinancialExtractor()
        self.sample_file = Path(__file__).parent.parent / "examples" / "data" / "DSF_Normal_Tantanpion_2024.xlsx"

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_hierarchical_output_structure(self):
        """Test that hierarchical output has correct structure."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Get hierarchical output
        hierarchical_data = OHADAJSONFormatter.format_statement_data_hierarchical(statement)
        
        # Verify structure
        self.assertIn("metadata", hierarchical_data)
        self.assertIn("extraction_metadata", hierarchical_data)
        self.assertIn("balance_sheet", hierarchical_data)
        self.assertIn("income_statement", hierarchical_data)
        self.assertIn("cashflow_statement", hierarchical_data)
        self.assertIn("other_data", hierarchical_data)
        self.assertIn("notes", hierarchical_data)
        
        # Verify format marker
        self.assertEqual(hierarchical_data["extraction_metadata"]["format"], "hierarchical")

        print(hierarchical_data)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_assets_hierarchy(self):
        """Test assets hierarchy structure."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        hierarchical_data = OHADAJSONFormatter.format_statement_data_hierarchical(statement)
        
        assets = hierarchical_data["balance_sheet"]["assets"]
        
        # Should have root nodes (BZ is the ultimate root)
        root_refs = [node["reference"] for node in assets]
        self.assertIn("BZ", root_refs)
        
        # Find the BZ node
        bz_node = next(node for node in assets if node["reference"] == "BZ")
        
        # BZ should have children
        self.assertGreater(len(bz_node["children"]), 0)
        
        # Check that AZ is a child of BZ
        az_children_refs = [child["reference"] for child in bz_node["children"]]
        self.assertIn("AZ", az_children_refs)
        
        # Find AZ node and check its children
        az_node = next(child for child in bz_node["children"] if child["reference"] == "AZ")
        
        # AZ should have children AD, AI, AP, AQ
        az_children_refs = [child["reference"] for child in az_node["children"]]
        self.assertIn("AD", az_children_refs)
        self.assertIn("AI", az_children_refs)
        self.assertIn("AP", az_children_refs)
        self.assertIn("AQ", az_children_refs)
        
        # Find AD node and check its children
        ad_node = next(child for child in az_node["children"] if child["reference"] == "AD")
        ad_children_refs = [child["reference"] for child in ad_node["children"]]
        
        # AD should have children AE, AF, AG, AH
        self.assertIn("AE", ad_children_refs)
        self.assertIn("AF", ad_children_refs)
        self.assertIn("AG", ad_children_refs)
        self.assertIn("AH", ad_children_refs)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_income_hierarchy(self):
        """Test income statement hierarchy structure."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        hierarchical_data = OHADAJSONFormatter.format_statement_data_hierarchical(statement)
        
        income = hierarchical_data["income_statement"]
        
        # Should have root node XI
        root_refs = [node["reference"] for node in income]
        self.assertIn("XI", root_refs)
        
        # Find the XI node (Résultat Net)
        xi_node = next(node for node in income if node["reference"] == "XI")
        
        # XI should have children XG, XH, RQ, RS
        xi_children_refs = [child["reference"] for child in xi_node["children"]]
        self.assertIn("XG", xi_children_refs)
        self.assertIn("XH", xi_children_refs)
        self.assertIn("RQ", xi_children_refs)
        self.assertIn("RS", xi_children_refs)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_cashflow_hierarchy(self):
        """Test cash flow hierarchy structure."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        hierarchical_data = OHADAJSONFormatter.format_statement_data_hierarchical(statement)
        
        cashflow = hierarchical_data["cashflow_statement"]
        
        # Should have root nodes ZA, ZG, ZH (all have parent None)
        root_refs = [node["reference"] for node in cashflow]
        self.assertIn("ZA", root_refs)
        self.assertIn("ZG", root_refs)
        self.assertIn("ZH", root_refs)
        
        # Find ZG node and check its children
        zg_node = next(node for node in cashflow if node["reference"] == "ZG")
        zg_children_refs = [child["reference"] for child in zg_node["children"]]
        
        # ZG should have children ZB, ZC, ZF
        self.assertIn("ZB", zg_children_refs)
        self.assertIn("ZC", zg_children_refs)
        self.assertIn("ZF", zg_children_refs)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_no_orphan_references(self):
        """Test that all references are included in hierarchical output."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Get flat output for reference
        flat_data = OHADAJSONFormatter.format_statement_data(statement)
        flat_assets_refs = {item["reference"] for item in flat_data["balance_sheet"]["assets"]}
        flat_liabilities_refs = {item["reference"] for item in flat_data["balance_sheet"]["liabilities"]}
        flat_income_refs = {item["reference"] for item in flat_data["income_statement"]}
        flat_cashflow_refs = {item["reference"] for item in flat_data["cashflow_statement"]}
        
        # Get hierarchical output
        hierarchical_data = OHADAJSONFormatter.format_statement_data_hierarchical(statement)
        
        # Collect all references from hierarchical output
        def collect_refs(nodes):
            refs = set()
            for node in nodes:
                refs.add(node["reference"])
                refs.update(collect_refs(node["children"]))
            return refs
        
        hierarchical_assets_refs = collect_refs(hierarchical_data["balance_sheet"]["assets"])
        hierarchical_liabilities_refs = collect_refs(hierarchical_data["balance_sheet"]["liabilities"])
        hierarchical_income_refs = collect_refs(hierarchical_data["income_statement"])
        hierarchical_cashflow_refs = collect_refs(hierarchical_data["cashflow_statement"])
        
        # Verify no references are dropped
        self.assertEqual(flat_assets_refs, hierarchical_assets_refs)
        self.assertEqual(flat_liabilities_refs, hierarchical_liabilities_refs)
        self.assertEqual(flat_income_refs, hierarchical_income_refs)
        self.assertEqual(flat_cashflow_refs, hierarchical_cashflow_refs)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_flat_output_unchanged(self):
        """Test that flat output remains unchanged when hierarchical=False."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Get flat output
        flat_json = OHADAJSONFormatter.to_json(statement, hierarchical=False)
        flat_data = OHADAJSONFormatter.format_statement_data(statement)
        
        # Verify flat output structure is maintained
        self.assertIsInstance(flat_data["balance_sheet"]["assets"], list)
        self.assertIsInstance(flat_data["balance_sheet"]["liabilities"], list)
        self.assertIsInstance(flat_data["income_statement"], list)
        self.assertIsInstance(flat_data["cashflow_statement"], list)
        
        # Verify no children key in flat output
        for asset in flat_data["balance_sheet"]["assets"]:
            self.assertNotIn("children", asset)
        
        for liability in flat_data["balance_sheet"]["liabilities"]:
            self.assertNotIn("children", liability)
        
        for income_item in flat_data["income_statement"]:
            self.assertNotIn("children", income_item)
        
        for cashflow_item in flat_data["cashflow_statement"]:
            self.assertNotIn("children", cashflow_item)

    @unittest.skipIf(
        not Path("examples/data/DSF_Normal_Tantanpion_2024.xlsx").exists(),
        "Sample data not available",
    )
    def test_hierarchical_json_output(self):
        """Test that hierarchical JSON output is valid."""
        statement = self.extractor.extract_from_excel(self.sample_file)
        
        # Get hierarchical JSON
        hierarchical_json = OHADAJSONFormatter.to_json(statement, hierarchical=True)
        
        # Verify it's valid JSON
        import json
        parsed = json.loads(hierarchical_json)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["extraction_metadata"]["format"], "hierarchical")

    def test_build_hierarchy_with_orphans(self):
        """Test that build_hierarchy handles orphans gracefully."""
        from ohada_extractor.core.schemas import ASSETS_PARENTS
        
        # Create test records with an orphan (reference not in parent map)
        flat_records = [
            {"reference": "AD", "label": "Test AD", "net": 100},
            {"reference": "AE", "label": "Test AE", "net": 50},
            {"reference": "XX", "label": "Orphan", "net": 25},  # Not in parent map
        ]
        
        # Build hierarchy
        result = OHADAJSONFormatter.build_hierarchy(flat_records, ASSETS_PARENTS)
        
        # Orphan should be placed at root
        root_refs = [node["reference"] for node in result]
        self.assertIn("XX", root_refs)


if __name__ == "__main__":
    unittest.main()
