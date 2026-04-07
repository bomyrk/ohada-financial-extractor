"""
JSON Formatter for OHADA Financial Statements

Converts extracted arrays into JSON-serializable format.
"""

from typing import Dict, List, Any, Optional
import json
import numpy as np
from datetime import date, datetime

from ..core.schemas import OHADA_STATEMENTS


class OHADAJSONFormatter:
    """Convert financial statement arrays to JSON-compatible format."""

    @staticmethod
    def numpy_to_serializable(obj: Any) -> Any:
        """Convert NumPy types to JSON-serializable types."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: OHADAJSONFormatter.numpy_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [OHADAJSONFormatter.numpy_to_serializable(item) for item in obj]
        return obj

    @staticmethod
    def format_assets(
        asset_data: np.ndarray,
        periods: List[str],
        accounts: List[tuple]
    ) -> List[Dict[str, Any]]:
        """
        Format balance sheet assets to JSON structure.
        
        Assets have Gross, Amortization, and Net columns per period.
        """
        result = []
        account_map = {acc[1]: acc[0] for acc in accounts}

        for row in asset_data:
            reference = str(row[0]).strip()
            label = account_map.get(reference, reference)
            
            record = {
                'reference': reference,
                'label': label,
            }

            # Assets have 3 value types per period (Gross, Amort, Net)
            num_periods = len(periods)
            value_idx = 1
            
            for period_idx, period in enumerate(periods):
                period_key = '' if period_idx == 0 else str(num_periods - period_idx)
                
                gross_key = f'gross{period_key}' if period_key else 'gross'
                amort_key = f'amort{period_key}' if period_key else 'amort'
                net_key = f'net{period_key}' if period_key else 'net'
                
                record[gross_key] = OHADAJSONFormatter.numpy_to_serializable(row[value_idx])
                record[amort_key] = OHADAJSONFormatter.numpy_to_serializable(row[value_idx + 1])
                record[net_key] = OHADAJSONFormatter.numpy_to_serializable(row[value_idx + 2])
                
                value_idx += 3

            result.append(record)

        return result

    @staticmethod
    def format_statement(
        statement_data: np.ndarray,
        periods: List[str],
        accounts: List[tuple],
        statement_type: str = 'statement'
    ) -> List[Dict[str, Any]]:
        """
        Format non-asset statements (income, liabilities, cashflow) to JSON.
        
        These have only Net values per period.
        """
        result = []
        account_map = {acc[1]: acc[0] for acc in accounts}

        for row in statement_data:
            reference = str(row[0]).strip()
            label = account_map.get(reference, reference)
            
            record = {
                'reference': reference,
                'label': label,
            }

            num_periods = len(periods)
            
            for period_idx, period in enumerate(periods):
                period_key = '' if period_idx == 0 else str(num_periods - period_idx)
                net_key = f'net{period_key}' if period_key else 'net'
                
                value_idx = period_idx + 1
                record[net_key] = OHADAJSONFormatter.numpy_to_serializable(row[value_idx])

            result.append(record)

        return result

    @staticmethod
    def format_statement_data(
        assets: np.ndarray,
        liabilities: np.ndarray,
        income: np.ndarray,
        cashflow: np.ndarray,
        periods: List[str]
    ) -> Dict[str, Any]:
        """
        Format all financial statements to complete JSON structure.
        
        Returns:
            Dictionary with formatted statements ready for JSON serialization
        """
        from ..core.schemas import ASSETS_ACCOUNTS, LIABILITIES_ACCOUNTS, INCOME_ACCOUNTS, CASHFLOW_ACCOUNTS

        return {
            'extraction_metadata': {
                'periods': periods,
                'statement_types': ['balance_sheet_assets', 'balance_sheet_liabilities', 'income_statement', 'cashflow'],
            },
            'balance_sheet': {
                'assets': OHADAJSONFormatter.format_assets(assets, periods, ASSETS_ACCOUNTS),
                'liabilities': OHADAJSONFormatter.format_statement(
                    liabilities, periods, LIABILITIES_ACCOUNTS, 'liabilities'
                ),
            },
            'income_statement': OHADAJSONFormatter.format_statement(
                income, periods, INCOME_ACCOUNTS, 'income'
            ),
            'cashflow_statement': OHADAJSONFormatter.format_statement(
                cashflow, periods, CASHFLOW_ACCOUNTS, 'cashflow'
            ),
        }

    @staticmethod
    def to_json(
        assets: np.ndarray,
        liabilities: np.ndarray,
        income: np.ndarray,
        cashflow: np.ndarray,
        periods: List[str],
        indent: int = 2
    ) -> str:
        """
        Convert all statements to JSON string.
        
        Args:
            indent: JSON indentation level (None for compact)
            
        Returns:
            JSON string
        """
        data = OHADAJSONFormatter.format_statement_data(
            assets, liabilities, income, cashflow, periods
        )
        return json.dumps(data, indent=indent, default=OHADAJSONFormatter.numpy_to_serializable)