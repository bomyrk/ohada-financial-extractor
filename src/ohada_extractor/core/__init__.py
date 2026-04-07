"""Core extraction and data structures."""

from .extractor import FinancialExtractor
from .statement import FinancialStatement
from .schemas import OHADA_STATEMENTS, ASSETS_ACCOUNTS, LIABILITIES_ACCOUNTS, INCOME_ACCOUNTS, CASHFLOW_ACCOUNTS

__all__ = [
    'FinancialExtractor',
    'FinancialStatement',
    'OHADA_STATEMENTS',
    'ASSETS_ACCOUNTS',
    'LIABILITIES_ACCOUNTS',
    'INCOME_ACCOUNTS',
    'CASHFLOW_ACCOUNTS',
]