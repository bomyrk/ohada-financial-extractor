"""
Example: Extracting Company Metadata from an OHADA DSF Excel File
=================================================================

This example demonstrates how to:

1. Load a DSF Excel file
2. Run the FinancialExtractor
3. Access the CompanyMetadata object
4. Print metadata fields (legal form, fiscal regime, country, etc.)
5. Export metadata to a dictionary or JSON

"""

import json
from pathlib import Path
from ohada_extractor.core.extractor import FinancialExtractor
from ohada_extractor.core.metadata_extractor import CompanyMetadataExtractor

def to_python_value(value):
    """Convert numpy values to JSON‑friendly Python types."""
    import numpy as np

    if isinstance(value, np.ndarray):
        if value.size == 1:
            return value.item()
        return value.tolist()

    if isinstance(value, np.generic):
        return value.item()

    return value

def main():
    # -------------------------------------------------------------------
    # 1. Load a DSF Excel file
    # -------------------------------------------------------------------

    # Replace with your own DSF file path
    sample_file = Path(__file__).parent / 'data' / 'DSF_Normal_Tantanpion_2024.xlsx'

    if not sample_file.exists():
        print(f"Error: Sample file not found at {sample_file}")
        print("Please run: python scripts/generate_sample_data.py")
        return

    extractor = FinancialExtractor()

    print("\n--- Extracting metadata from DSF Excel file ---")
    statement = extractor.extract_from_excel(sample_file)

    # Ensure xarray is built (optional but recommended)
    statement.to_xarray()

    # -------------------------------------------------------------------
    # 2. Build metadata from the statement
    # -------------------------------------------------------------------

    print("\n--- Building company metadata from statement ---")
    statement.metadata = CompanyMetadataExtractor.extract_from_statement(statement)

    metadata = statement.metadata

    if metadata is None:
        raise RuntimeError("Metadata extraction failed: statement.metadata is None")

    # -------------------------------------------------------------------
    # 3. Inspect metadata fields
    # -------------------------------------------------------------------

    print("\n--- Company Metadata ---")
    print(f"Legal Form:          {metadata.legal_form}")
    print(f"Country:             {metadata.country}")
    #print(f"Sector:              {metadata.activity_sector}")
    print(f"Fiscal Regime:       {metadata.regime_fiscal}")
    print(f"Currency:            {metadata.currency}")
    print(f"Year of Creation:    {metadata.year_creation}")
    print(f"Number of Employees: {metadata.number_of_employees}")
    print(f"Number of Shares:    {metadata.number_of_shares}")
    print(f"Dividend:            {metadata.dividend}")

    # -------------------------------------------------------------------
    # 4. Check for missing metadata fields
    # -------------------------------------------------------------------

    print("\n--- Missing Metadata Fields ---")
    if hasattr(metadata, "missing_fields"):
        missing = metadata.missing_fields()
        if missing:
            for field in missing:
                print(f"⚠️  Missing: {field}")
        else:
            print("All metadata fields are present.")
    else:
        print("No `missing_fields` method defined on metadata object.")

    # -------------------------------------------------------------------
    # 5. Export metadata to dict / JSON
    # -------------------------------------------------------------------

    metadata_dict = {
        field: to_python_value(value)
        for field, value in metadata.__dict__.items()
    }

    metadata_json = json.dumps(metadata_dict, indent=4, ensure_ascii=False)

    print("\n--- Metadata as JSON ---")
    print(metadata_json)

    # -------------------------------------------------------------------
    # 6. Save metadata to a JSON file
    # -------------------------------------------------------------------

    import os
    os.makedirs("output", exist_ok=True)
    output_path = sample_file.parent.parent / "output"/ "company_metadata.json"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(metadata_json)

    print(f"\nMetadata saved to: {output_path}")

if __name__ == '__main__':
    main()