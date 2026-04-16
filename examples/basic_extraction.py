"""
Basic Example: Extract financial data from a single OHADA Excel file

This example demonstrates:
- Loading an Excel file
- Extracting financial statements
- Converting to JSON
"""

import json
from pathlib import Path
from ohada_extractor import FinancialExtractor
from ohada_extractor.formatters import OHADAJSONFormatter


def main():
    # Path to sample Excel file
    sample_file = Path(__file__).parent / 'data' / 'DSF_Normal_Tantanpion_2024.xlsx'
    
    if not sample_file.exists():
        print(f"Error: Sample file not found at {sample_file}")
        print("Please run: python scripts/generate_sample_data.py")
        return

    print(f"Extracting financial data from: {sample_file}")
    
    # Initialize extractor
    extractor = FinancialExtractor()
    
    # Extract data
    statement = extractor.extract_from_excel(sample_file)
    
    print(f"\n✓ Extraction successful!")
    print(f"  Periods: {statement.periods}")
    print(f"  File: {statement.file_path}")
    
    # Convert to JSON
    json_output = OHADAJSONFormatter.to_json(
        statement=statement,
        indent=2
    )
    
    # Save to file
    output_file = sample_file.parent.parent / 'output_extraction.json'
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

    statement = extractor.extract_from_excel('examples/data/DSF_Normal_Tantanpion_2024.xlsx')
    from ohada_extractor.validation.coherence_validator import CoherenceValidator

    validator = CoherenceValidator.from_financial_statement(statement)
    validator.validate()

    statement_2 = extractor.extract_over_period(
        ['examples/data/DSF_Normal_Tantanpion_2024.xlsx', 'examples/data/DSF_Normal_Tantanpion_2025.xlsx'])
    validator_2 = CoherenceValidator.from_financial_statement(statement_2)
    from ohada_extractor.core.metadata_extractor import CompanyMetadataExtractor

    statement.metadata = CompanyMetadataExtractor.extract_from_statement(statement)

    from ohada_extractor.visualization.themes.styles import apply_ohada_style

    apply_ohada_style()
    statement.plot("assets", plot_type="static")

    from ohada_extractor.visualization.themes.templates import register_ohada_template
    import plotly.io as pio

    register_ohada_template()
    pio.templates.default = "ohada"

    statement.plot("assets", plot_type="dynamic")


if __name__ == '__main__':
    main()