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
    statements = []
    
    for file_path in file_list:
        try:
            print(f"Processing: {file_path}")
            stmt = extractor.extract_from_excel(file_path)
            statements.append(stmt)
            print(f"  ✓ Extracted {len(stmt.periods)} periods")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    return statements


def consolidate_statements(statements):
    """
    Consolidate multiple statements (future enhancement).
    
    Args:
        statements: List of FinancialStatement objects
        
    Returns:
        Consolidated data
    """
    # TODO: Implement consolidation logic
    # For now, return all statements
    return {
        'count': len(statements),
        'periods': [p for stmt in statements for p in stmt.periods],
        'statements': [stmt.to_dict() for stmt in statements],
    }


def main():
    # Example: process files from a directory
    data_dir = Path(__file__).parent / 'data'
    
    # Find all Excel files
    excel_files = list(data_dir.glob('*.xlsx'))
    
    if not excel_files:
        print(f"No Excel files found in {data_dir}")
        print("Please add OHADA Excel files to the examples/data directory")
        return
    
    print(f"Found {len(excel_files)} Excel files")
    
    # Process
    statements = process_multiple_files(excel_files)
    
    if statements:
        # Consolidate
        consolidated = consolidate_statements(statements)
        
        # Save results
        output_file = data_dir.parent / 'batch_output.json'
        with open(output_file, 'w') as f:
            json.dump(consolidated, f, indent=2, default=str)
        
        print(f"\n✓ Consolidated output saved to: {output_file}")
    else:
        print("\n✗ No files processed successfully")


if __name__ == '__main__':
    main()