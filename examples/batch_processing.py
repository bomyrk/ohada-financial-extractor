"""
Batch Processing Example: Extract data from multiple years

This example demonstrates:
- Processing multiple Excel files
- Consolidating data across periods
- Exporting consolidated results
"""

import json
from pathlib import Path
from ohada_extractor import FinancialExtractor
from ohada_extractor.formatters import OHADAJSONFormatter


def process_multiple_files(file_list):
    """
    Process multiple OHADA financial statement files.
    
    Args:
        file_list: List of Excel file paths
        
    Returns:
        List of extracted FinancialStatement objects
    """
    extractor = FinancialExtractor()

    # Extract data
    statements = extractor.extract_over_period(file_list)

    print(f"\n✓ Extraction successful!")
    print(f"  Periods: {statements.periods}")
    print(f"  File: {statements.file_path}")

    # Convert to JSON
    json_output = OHADAJSONFormatter.to_json(
        assets=statements.asset_data,
        liabilities=statements.liability_data,
        income=statements.income_data,
        cashflow=statements.cashflow_data,
        periods=statements.periods,
        indent=2
    )

    # Save to file
    output_file = Path(__file__).parent.parent / 'output_extraction.json'
    with open(output_file, 'w') as f:
        f.write(json_output)

    print(f"\n✓ JSON output saved to: {output_file}")

    # Display sample
    data = json.loads(json_output)
    print(f"\nSample output structure:")
    print(f"  Assets count: {len(data['balance_sheet']['assets'])}")
    print(f"  Liabilities count: {len(data['balance_sheet']['liabilities'])}")
    print(f"  Income items count: {len(data['income_statement'])}")
    print(f"  Cashflow items count: {len(data['cashflow_statement'])}")

    return statements


def main():
    # Example: process files from a directory
    data_dir = Path(__file__).parent / 'data'
    
    # Find all Excel files
    excel_files = sorted(data_dir.glob('*.xlsx'))
    
    if not excel_files:
        print(f"No Excel files found in {data_dir}")
        print("Please add OHADA Excel files to the examples/data directory")
        return
    
    print(f"Found {len(excel_files)} Excel files")
    
    # Process
    process_multiple_files(excel_files)


if __name__ == '__main__':
    main()