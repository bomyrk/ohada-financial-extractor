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

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

__author__ = "Kamguia Wabo Leonel B. "

from .core.extractor import FinancialExtractor
from .core.schemas import ASSETS_ACCOUNTS, OHADA_STATEMENTS

__all__ = [
    "FinancialExtractor",
    "OHADA_STATEMENTS",
    "ASSETS_ACCOUNTS",
]
