# Output Schema Specification

JSON output schema for OHADA Financial Extractor.

## Root Structure

```json
{
    "extraction_metadata": { ... },
    "balance_sheet": { ... },
    "income_statement": [ ... ],
    "cashflow_statement": [ ... ]

}
````

**extraction_metadata**

````json
{
  "periods": ["2023-12-31", "2024-12-31", "2025-12-31"],
  "statement_types": [
    "balance_sheet_assets",
    "balance_sheet_liabilities",
    "income_statement",
    "cashflow"
  ]
}
````

Fields:

* periods: Array of fiscal period end dates (ISO 8601 format)
* statement_types: Available statement types in this extraction

**balance_sheet**
````json
{
  "assets": [ ... ],
  "liabilities": [ ... ]
}
````

Assets Array

Each asset account follows this structure:

````json
{
  "reference": "AD",
  "label": "Immobilisations incorporelles",
  "gross": 100000.0,
  "amort": 50000.0,
  "net": 50000.0,
  "gross1": 110000.0,
  "amort1": 55000.0,
  "net1": 55000.0,
  "gross2": 120000.0,
  "amort2": 60000.0,
  "net2": 60000.0
}
````

Fields:

* reference: Account code (e.g., "AD", "BZ")
* label: Account name in French
* gross: Gross value for most recent period
* amort: Amortization for most recent period
* net: Net (book) value for most recent period
* gross1, amort1, net1: Values for second-most recent period
* gross2, amort2, net2: Values for third-most recent period (if available)

**Pattern**: For N periods, there are N sets of (gross, amort, net) values:

* Period 0 (most recent): Keys without suffix
* Period 1: Keys with suffix "1"
* Period 2: Keys with suffix "2"
* etc.

Liabilities Array

````json
[
  {
    "reference": "CA",
    "label": "Capital",
    "net": 200000.0,
    "net1": 200000.0,
    "net2": 200000.0
  },
  {
    "reference": "CP",
    "label": "Capitaux Propres",
    "net": 300000.0,
    "net1": 310000.0,
    "net2": 320000.0
  }
]
````
Fields:

* reference: Account code
* label: Account name
* net: Most recent period value
* net1, net2: Prior period values

**income_statement**

Array of income statement accounts:

````json
[
  {
    "reference": "TA",
    "label": "Ventes de marchandises",
    "net": 1000000.0,
    "net1": 950000.0,
    "net2": 900000.0
  },
  {
    "reference": "XI",
    "label": "Résultat Net",
    "net": 50000.0,
    "net1": 55000.0,
    "net2": 60000.0
  }
]
````

Fields: Same as liabilities (only net values, no amortization)

**cashflow_statement**

Array of cash flow statement accounts:

````json
[
  {
    "reference": "ZA",
    "label": "Trésorerie nette au 1er janvier",
    "net": 50000.0,
    "net1": 40000.0,
    "net2": 30000.0
  },
  {
    "reference": "ZB",
    "label": "Flux opérationnel",
    "net": 100000.0,
    "net1": 95000.0,
    "net2": 90000.0
  },
  {
    "reference": "ZH",
    "label": "Trésorerie nette au 31 décembre",
    "net": 150000.0,
    "net1": 135000.0,
    "net2": 120000.0
  }
]
````

**Example: Complete Multi-Period Output**
````json
{
  "extraction_metadata": {
    "periods": ["2023-12-31", "2024-12-31", "2025-12-31"],
    "statement_types": [
      "balance_sheet_assets",
      "balance_sheet_liabilities",
      "income_statement",
      "cashflow"
    ]
  },
  "balance_sheet": {
    "assets": [
      {
        "reference": "AD",
        "label": "Immobilisations incorporelles",
        "gross": 100000.0,
        "amort": 50000.0,
        "net": 50000.0,
        "gross1": 95000.0,
        "amort1": 45000.0,
        "net1": 50000.0,
        "gross2": 80000.0,
        "amort2": 40000.0,
        "net2": 40000.0
      },
      {
        "reference": "BZ",
        "label": "Total Actif",
        "gross": 5000000.0,
        "amort": 1000000.0,
        "net": 4000000.0,
        "gross1": 4800000.0,
        "amort1": 950000.0,
        "net1": 3850000.0,
        "gross2": 4500000.0,
        "amort2": 900000.0,
        "net2": 3600000.0
      }
    ],
    "liabilities": [
      {
        "reference": "CA",
        "label": "Capital",
        "net": 2000000.0,
        "net1": 2000000.0,
        "net2": 2000000.0
      },
      {
        "reference": "DZ",
        "label": "Total Passif",
        "net": 4000000.0,
        "net1": 3850000.0,
        "net2": 3600000.0
      }
    ]
  },
  "income_statement": [
    {
      "reference": "XB",
      "label": "Chiffre d'affaires",
      "net": 5000000.0,
      "net1": 4800000.0,
      "net2": 4500000.0
    },
    {
      "reference": "XI",
      "label": "Résultat Net",
      "net": 150000.0,
      "net1": 140000.0,
      "net2": 125000.0
    }
  ],
  "cashflow_statement": [
    {
      "reference": "ZB",
      "label": "Flux opérationnel",
      "net": 250000.0,
      "net1": 230000.0,
      "net2": 200000.0
    },
    {
      "reference": "ZH",
      "label": "Trésorerie nette au 31 décembre",
      "net": 500000.0,
      "net1": 480000.0,
      "net2": 450000.0
    }
  ]
}
````

**Numeric Values**
* Type: Float (JSON number)
* -NaN Handling: NaN values are converted to null
* Infinity: Not supported; should be replaced with maximum representable float
* Currency: Values are unitless; currency should be inferred from country or metadata

**Date Format**

* Format: ISO 8601 (YYYY-MM-DD)
* Example: "2024-12-31"
* Timezone: Always UTC


**Account Ordering**

Accounts appear in the array in the order they appear in the original Excel file (top to bottom), which corresponds to OHADA chart of accounts order.

**Encoding**

* Character Encoding: UTF-8
* Locale: French (account labels in French)

**Validation**

Valid output JSON should satisfy:


1. All reference values match OHADA account codes
2. Assets (BZ) = Liabilities (DZ) for each period
3. Net Income (XI) matches Balance Sheet retained earnings (CJ) for each period
4. Internal validation [e.g "AD=AE+AF+AG+AH"] (NEW)
4. All numeric values are valid JSON numbers