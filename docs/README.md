# OHADA Financial Extractor

Extract and normalize financial data from OHADA-compliant Excel financial statements.


[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Overview


This library automates financial data extraction from Excel files following **OHADA** (Organization for the Harmonization of African Business Law) accounting standards, used by 18 African countries.


### What It Does



- **Extracts** Balance Sheets (Bilan Paysage), Income Statements (Compte de Résultat), and Cash Flow Statements (Tableau des Flux de Trésorerie)

- **Normalizes** data with Gross/Amortization/Net decomposition for fixed assets

- **Consolidates** multi-year financial data

- **Exports** to JSON for downstream analysis



### Why It Matters



Financial institutions across OHADA zone countries spend significant time:

- ✗ Manually retyping financial statement data

- ✗ Restructuring Excel files line-by-line

- ✗ Validating data integrity across years



This library eliminates those bottlenecks:

- ✓ Automated extraction from standard Excel formats

- ✓ Structured JSON output

- ✓ Multi-year period aggregation

- ✓ Data validation checks



## Quick Start



### Installation



```bash

pip install ohada-financial-extractor
```
Basic Usage

```python
from ohada_extractor import FinancialExtractor
from ohada_extractor.formatters import OHADAJSONFormatter
import json

# Extract from Excel
extractor = FinancialExtractor()
statement = extractor.extract_from_excel('financial_statement.xlsx')

# Convert to JSON
json_output = OHADAJSONFormatter.to_json(
    statement=statement,
    indent=2
)

# Use or save
data = json.loads(json_output)
print(f"Total Assets: {data['balance_sheet']['assets'][-1]}")
```
### **Supported Statements**

**Balance Sheet Asset (Bilan Paysage)**
- **29 accounts** (AD-BZ)
- Tracks: Gross, Amortization, Net values
- Assets split: Fixed assets, Current assets, Cash

**Balance Sheet Liability (Bilan Paysage)**
- **28 accounts** (CA-DZ)
- Tracks: Net values
- Liabilities split: Equity, Long-Term Debt, Current Liabilities, Short Term Debt

**Income Statement (Compte de Résultat)**
- **42 accounts** (TA-XI)
- Revenue, expenses, tax, net income
- Tracks: Operating, financial, and extraordinary results

**Cash Flow Statement (Tableau des Flux de Trésorerie)**
- 25 accounts (ZA-ZH)
- Operating, investing, financing activities
- Beginning and ending cash positions

### **Metadata Extraction (NEW)**

The extractor now automatically parses company metadata from DSF notes and headers, including:

- Legal form
- Fiscal regime
- Country (headquater)
- Year of creation
- Currency
- etc.

Metadata is available immediately after extraction:
````python
from ohada_extractor.core.extractor import FinancialExtractor
from ohada_extractor.core.metadata_extractor import CompanyMetadataExtractor

# Initialize extractor
extractor = FinancialExtractor()
    
# Extract data
statement = extractor.extract_from_excel("financial_statement.xlsx")

print("\n--- Building company metadata from statement ---")
statement.metadata = CompanyMetadataExtractor.extract_from_statement(statement)

metadata = statement.metadata

print(metadata.currency)
print(metadata.legal_form)
print(metadata.regime_fiscal)

````
Metadata is fully JSON‑serializable and can be exported:
````python
metadata_dict = metadata.to_dict()
````
This enables automated KYC, and regulatory reporting workflow.

### **Notes Extraction (NEW)**

The extractor now includes 23 OHADA Notes (Annexes) engine, parsing structured and unstructured notes such as:
- Fiche R2 — Company identity
- Note 31 — Repartition du résultat et autres elements sur les dernières années
- Accounting policies
- Commitments & guarantees
- Tax regime
- Share capital information
- Workforce details

Notes are extracted automatically:
````python
statement = extractor.extract_from_excel("financial_statement.xlsx")

# Retrieve by key
note = statement.get_note("note3a")

# Retrieve by human-readable name
note = statement.get_note_by_name("IMMOBILISATION BRUTE")

````
Each note includes:
- name
- raw_value
- preprocess_value

Notes can be exported to JSON for auditing or BI tools.


### **Features**
- ✅ Multi-file period aggregation (2-5 years)
- ✅ Automatic data validation
- ✅ JSON-serializable output
- ✅ Account code standardization (OHADA)
- ✅ Gross/Amort/Net decomposition for assets
- ✅ Support for 18 OHADA zone countries

### **📊 Visualization Layer (NEW)**

The library now includes a **visualization module** for OHADA financial statements.

**Static 4×2 Overview Dashboard**

Grouped, stacked, waterfall, and cashflow charts in a single figure:

````python
from ohada_extractor.visualization import plot_overview_dashboard_clean
plot_overview_dashboard_clean(statement)
````

**Dynamic Tabbed Dashboard**

Interactive dashboard with tabs for:
- Assets
- Liabilities
- Income
- Cashflow

````python
from ohada_extractor.visualization import plot_ohada_tabs_dynamic
plot_ohada_tabs_dynamic(statement)
````

**Streamlit Integration**

A ready‑to‑use Streamlit app is included:

````bash
streamlit run examples/example_visualization_streamlit.py
````
This enables instant deployment of dashboards for analysts, auditors, and credit officers.

### **Documentation**
- OHADA Standards — Account codes and structures for 18 countries
- Output Schema — JSON output format specification
- Examples — Sample extraction workflows

### **Example Output**

```json
{
  "extraction_metadata": {
    "periods": ["2023-12-31", "2024-12-31"],
    "statement_types": ["balance_sheet_assets", "income_statement", "cashflow", "notes"]
  },
  "balance_sheet": {
    "assets": [
      {
        "reference": "AD",
        "label": "Immobilisations incorporelles",
        "gross": 100000.0,
        "amort": 50000.0,
        "net": 50000.0,
        "gross1": 110000.0,
        "amort1": 55000.0,
        "net1": 55000.0
      }
    ]
  }
}
```


### **📁 Examples (New)**
The repository now includes a full *examples/* directory:

````Code
examples/
    example_metadata_extraction.py
    example_notes_usage.py
    example_visualization_streamlit.py
````
**Metadata Example**

Shows how to extract and export company metadata.

**Notes Example**

Demonstrates how to retrieve raw and processed OHADA notes.

**Visualization Example**

Runs static dashboards, dynamic dashboards, and a Streamlit UI.

These examples make onboarding fast for banks, auditors, fintechs, and researchers.


### **TESTING**

```python
python -m pytest tests/

# Use or save
data = json.loads(json_output)
print(f"Total Assets: {data['balance_sheet']['assets'][-1]}")
```

### **Use Cases**
1. Credit Processing
Accelerate loan analysis for SMEs by automating financial statement data entry.

2. Portfolio Management
Consolidate financials from multiple companies for real-time portfolio analytics.

3. Regulatory Reporting
Standardized extraction for compliance with OHADA zone banking regulations.

4. Financial Analytics
Feed cleaned, structured data into analytics and forecasting models.

### **OHADA Zone Coverage**

Supported in: Benin, Burkina Faso, Cameroon, Central African Republic, Chad, 
Comoros, Congo (DR), Congo, Côte d'Ivoire, Equatorial Guinea, Gabon, Guinea, 
Guinea-Bissau, Mali, Niger, Senegal, Togo.

**Contribution**

Contributions welcome! Areas for expansion:

- PDF extraction support
- Additional statement types
- Data validation rules repository
- Performance optimizations

License
MIT License — see LICENSE

###  Citation

If you use this library in your research or production system, please cite:

**Kamguia Wabo, L. B.**, & **Ndayou, R. V.** (2026). *OHADA Financial Extractor*. B.K. Research & Analytics. 
Retrieved from [https://github.com/bomyrk/ohada-financial-extractor](https://github.com/bomyrk/ohada-financial-extractor)

```
@software{ohada_extractor_2026,
  title={OHADA Financial Extractor},
  author={Kamguia Wabo, L. Bomyr},
  year={2026},
  url={https://github.com/bomyrk/ohada-financial-extractor}
}
```

### Author

Kamguia Wabo, L. B. \
B.K. Research & Analytics\
[bomyr.kamguia@bkresearchandanalytics.com](mailto:bomyr.kamguia@bkresearchandanalytics.com)

---
*Democratizing financial data extraction for African financial institutions.*