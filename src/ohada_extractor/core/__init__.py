"""Core extraction and data structures."""

from .extractor import FinancialExtractor
from .schemas import (
    ASSETS_ACCOUNTS,
    CASHFLOW_ACCOUNTS,
    INCOME_ACCOUNTS,
    LIABILITIES_ACCOUNTS,
    OHADA_STATEMENTS,
)
from .statement import FinancialStatement

__all__ = [
    "FinancialExtractor",
    "FinancialStatement",
    "OHADA_STATEMENTS",
    "ASSETS_ACCOUNTS",
    "LIABILITIES_ACCOUNTS",
    "INCOME_ACCOUNTS",
    "CASHFLOW_ACCOUNTS",
]
