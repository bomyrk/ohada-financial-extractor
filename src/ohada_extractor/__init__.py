"""
OHADA Financial Statement Extractor

A Python library for extracting and normalizing financial data from
Excel files following OHADA (Organization for the Harmonization of
African Business Law) accounting standards.

Key Features:
- Extract Balance Sheets (Bilan Paysage [Asset and Liabilities]) with Gross/Amortization/Net values
- Extract Income Statements (Compte de Résultat)
- Extract Cash Flow Statements (Tableau des Flux de Trésorerie)
- Multi-file period aggregation
- JSON-serializable output
- Support for 18 OHADA zone countries

Example:
    >>> from ohada_extractor import FinancialExtractor
    >>> extractor = FinancialExtractor()
    >>> data = extractor.extract_from_excel('financial_statement.xlsx')
    >>> json_output = data.to_json()
"""

# __version__ = "0.2.0"

__author__ = "Kamguia Wabo Leonel B. "

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ohada-financial-extractor")
except PackageNotFoundError:
    # Package is being run directly from the source tree.
    __version__ = "0.0.0.dev0"

from .core.extractor import FinancialExtractor
from .core.schemas import ASSETS_ACCOUNTS, OHADA_STATEMENTS
from .validation import CoherenceCheckResult, CoherenceReport, CoherenceValidator

__all__ = [
    "FinancialExtractor",
    "CoherenceValidator",
    "CoherenceCheckResult",
    "CoherenceReport",
    "OHADA_STATEMENTS",
    "ASSETS_ACCOUNTS",
]
