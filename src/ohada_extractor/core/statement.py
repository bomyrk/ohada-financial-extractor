"""
Financial Statement Data Container

Represents extracted and structured financial data from OHADA Excel files.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
import numpy as np


@dataclass
class FinancialStatement:
    """
    Container for extracted financial statement data.
    
    Attributes:
        asset_data: NumPy array of balance sheet assets
        liability_data: NumPy array of balance sheet liabilities
        income_data: NumPy array of income statement data
        cashflow_data: NumPy array of cash flow statement data
        periods: List of period dates (e.g., ['2023-12-31', '2024-12-31'])
        file_path: Original Excel file path
    """
    asset_data: Optional[np.ndarray] = None
    liability_data: Optional[np.ndarray] = None
    income_data: Optional[np.ndarray] = None
    cashflow_data: Optional[np.ndarray] = None
    periods: List[str] = None
    file_path: str = None
    
    def __post_init__(self):
        if self.periods is None:
            self.periods = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert statement to dictionary format."""
        return {
            'assets': self.asset_data.tolist() if self.asset_data is not None else None,
            'liabilities': self.liability_data.tolist() if self.liability_data is not None else None,
            'income': self.income_data.tolist() if self.income_data is not None else None,
            'cashflow': self.cashflow_data.tolist() if self.cashflow_data is not None else None,
            'periods': self.periods,
            'file_path': self.file_path,
        }

    def get_asset(self, reference: str) -> Optional[np.ndarray]:
        """Get asset row by account reference code."""
        if self.asset_data is None:
            return None
        for i, row in enumerate(self.asset_data):
            if str(row[0]).strip().upper() == reference.upper():
                return row[1:]
        return None

    def get_liability(self, reference: str) -> Optional[np.ndarray]:
        """Get liability row by account reference code."""
        if self.liability_data is None:
            return None
        for i, row in enumerate(self.liability_data):
            if str(row[0]).strip().upper() == reference.upper():
                return row[1:]
        return None

    def get_income(self, reference: str) -> Optional[np.ndarray]:
        """Get income row by account reference code."""
        if self.income_data is None:
            return None
        for i, row in enumerate(self.income_data):
            if str(row[0]).strip().upper() == reference.upper():
                return row[1:]
        return None