"""
JSON Formatter for OHADA Financial Statements

Converts extracted arrays into JSON-serializable format.
"""

from typing import Dict, List, Any, Optional
import json
import numpy as np
from datetime import date, datetime

class OHADAJSONFormatter:
    """Convert financial statement arrays + notes + metadata to JSON-compatible format."""

    # ---------------------------------------------------------
    # GENERIC NUMPY SERIALIZER (with 2-decimal rounding)
    # ---------------------------------------------------------
    @staticmethod
    def numpy_to_serializable(obj: Any) -> Any:
        """Convert NumPy types to JSON-serializable types."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return round(float(obj), 2)
        elif isinstance(obj, np.ndarray):
            return [OHADAJSONFormatter.numpy_to_serializable(item) for item in obj.tolist()]
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: OHADAJSONFormatter.numpy_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [OHADAJSONFormatter.numpy_to_serializable(item) for item in obj]
        return obj

    # ---------------------------------------------------------
    # NOTES FORMATTER (NEW)
    # ---------------------------------------------------------
    @staticmethod
    def format_notes(notes_dict: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Format notes (annexes) into JSON-compatible structure.
        Handles:
            - raw_value arrays
            - preprocess_value arrays or tuples
            - multi-year merged notes
        """
        if notes_dict is None:
            return None

        formatted = {}

        for key, entry in notes_dict.items():
            formatted[key] = {
                "name": entry.get("name"),
                "raw_value": OHADAJSONFormatter.numpy_to_serializable(entry.get("raw_value")),
                "preprocess_value": OHADAJSONFormatter.numpy_to_serializable(entry.get("preprocess_value"))
            }

        return formatted

    # ---------------------------------------------------------
    # METADATA FORMATTER
    # ---------------------------------------------------------
    @staticmethod
    def format_metadata(metadata_obj) -> Optional[Dict[str, Any]]:
        if metadata_obj is None:
            return None
        return {
            "currency": metadata_obj.currency,
            "legal_form": metadata_obj.legal_form,
            "country": metadata_obj.country,
            "year_creation": metadata_obj.year_creation,
            "regime_fiscal": metadata_obj.regime_fiscal,
            "dividend": OHADAJSONFormatter.numpy_to_serializable(metadata_obj.dividend),
            "number_of_shares": OHADAJSONFormatter.numpy_to_serializable(metadata_obj.number_of_shares),
            "number_of_employees": OHADAJSONFormatter.numpy_to_serializable(metadata_obj.number_of_employees),
        }

    # ---------------------------------------------------------
    # ASSETS FORMATTER
    # ---------------------------------------------------------
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

                if value_idx != (len(row)-1):
                    record[gross_key] = OHADAJSONFormatter.numpy_to_serializable(row[value_idx])
                    record[amort_key] = OHADAJSONFormatter.numpy_to_serializable(row[value_idx + 1])
                    record[net_key] = OHADAJSONFormatter.numpy_to_serializable(row[value_idx + 2])
                else:
                    record[gross_key] = None
                    record[amort_key] = None
                    record[net_key] = OHADAJSONFormatter.numpy_to_serializable(row[value_idx])

                value_idx += 3

            result.append(record)

        return result

    # ---------------------------------------------------------
    # GENERIC STATEMENT FORMATTER
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # FULL STATEMENT FORMATTER (UPDATED)
    # ---------------------------------------------------------
    @staticmethod
    def format_statement_data(statement) -> Dict[str, Any]:
        """
        Format a FinancialStatement object into a JSON-ready dictionary.
        
        Returns:
            Dictionary with formatted statements ready for JSON serialization
        """
        from ..core.schemas import ASSETS_ACCOUNTS, LIABILITIES_ACCOUNTS, INCOME_ACCOUNTS, CASHFLOW_ACCOUNTS

        periods = statement.periods if len(statement.periods) >2 else statement.periods[::-1]
        return {
            "metadata": OHADAJSONFormatter.format_metadata(statement.metadata),
            'extraction_metadata': {
                'periods': periods,
                'statement_types': ['balance_sheet_assets', 'balance_sheet_liabilities', 'income_statement', 'cashflow',
                    'notes', 'metadata',],
            },
            'balance_sheet': {
                'assets': OHADAJSONFormatter.format_assets(statement.asset_data, periods, ASSETS_ACCOUNTS),
                'liabilities': OHADAJSONFormatter.format_statement(
                    statement.liability_data, periods, LIABILITIES_ACCOUNTS, 'liabilities'
                ),
            },
            'income_statement': OHADAJSONFormatter.format_statement(
                statement.income_data, periods, INCOME_ACCOUNTS, 'income'
            ),
            'cashflow_statement': OHADAJSONFormatter.format_statement(
                statement.cashflow_data, periods, CASHFLOW_ACCOUNTS, 'cashflow'
            ),
            'notes': OHADAJSONFormatter.format_notes(statement.notes)
        }

    # ---------------------------------------------------------
    # JSON STRING OUTPUT (UPDATED)
    # ---------------------------------------------------------
    @staticmethod
    def to_json(statement, indent: int = 2) -> str:
        """
        Convert all statements to JSON string.
        
        Args:
            indent: JSON indentation level (None for compact)
            
        Returns:
            JSON string
        """
        data = OHADAJSONFormatter.format_statement_data(statement)
        return json.dumps(data, indent=indent, default=OHADAJSONFormatter.numpy_to_serializable)