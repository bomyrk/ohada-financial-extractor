"""
JSON Formatter for OHADA Financial Statements

Converts extracted arrays into JSON-serializable format.
"""

import json
import logging
import math
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class OHADAJSONFormatter:
    """Convert financial statement arrays + other data + notes + metadata to JSON-compatible format."""

    # ---------------------------------------------------------
    # GENERIC NUMPY SERIALIZER (with 2-decimal rounding)
    # ---------------------------------------------------------
    @staticmethod
    def numpy_to_serializable(obj: Any) -> Any:
        """Convert NumPy types to JSON-serializable types."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            if not np.isfinite(obj):
                return None
            return round(float(obj), 2)
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
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
    # YEAR/PERIOD PARSER
    # ---------------------------------------------------------
    @staticmethod
    def parse_years(datetime_index: Union[pd.DatetimeIndex, List]) -> Dict[str, str]:
        """
        Convert a DatetimeIndex or list of dates to a dictionary with standardized period keys.

        Maps periods to 'net', 'net1', 'net2', etc., where 'net' is the most recent period.
        This ensures consistent year labeling across multi-period financial statements.

        Args:
            datetime_index: pd.DatetimeIndex or list of dates/strings

        Returns:
            Dictionary with keys like {'net': '2023-12-31', 'net1': '2022-12-31', ...}

        Raises:
            ValueError: If fewer than 2 dates provided

        Example:
            >>> dates = pd.DatetimeIndex(['2021-12-31', '2022-12-31', '2023-12-31'])
            >>> OHADAJSONFormatter.parse_years(dates)
            {'net2': '2021-12-31', 'net1': '2022-12-31', 'net': '2023-12-31'}
        """
        # Convert to list if necessary
        if isinstance(datetime_index, pd.DatetimeIndex):
            dates = datetime_index.tolist()
        elif isinstance(datetime_index, list):
            # Try to convert strings to datetime if needed
            dates = [pd.Timestamp(d) if isinstance(d, str) else d for d in datetime_index]
        else:
            raise TypeError(f"Expected pd.DatetimeIndex or list, got {type(datetime_index)}")

        if len(dates) < 2:
            raise ValueError("Date index must contain at least two dates.")

        # Create dictionary with net, net1, net2, ... keys
        date_dict = {f"net{len(dates) - 1 - idx}": dates[idx].isoformat() for idx in range(len(dates) - 1)}
        date_dict["net"] = dates[-1].isoformat()  # Most recent as 'net'

        return date_dict

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
                "preprocess_value": OHADAJSONFormatter.numpy_to_serializable(entry.get("preprocess_value")),
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
            "number_of_units": metadata_obj.number_of_units,
            "owned": metadata_obj.owned,
            "dividend": OHADAJSONFormatter.numpy_to_serializable(metadata_obj.dividend),
            "number_of_shares": OHADAJSONFormatter.numpy_to_serializable(metadata_obj.number_of_shares),
            "number_of_employees": OHADAJSONFormatter.numpy_to_serializable(metadata_obj.number_of_employees),
        }

    # ---------------------------------------------------------
    # ASSETS FORMATTER
    # ---------------------------------------------------------
    @staticmethod
    def format_assets(asset_data: np.ndarray, periods: List[str], accounts: List[tuple]) -> List[Dict[str, Any]]:
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
                "reference": reference,
                "label": label,
            }

            # Assets have 3 value types per period (Gross, Amort, Net)
            num_periods = len(periods)
            value_idx = 1

            for period_idx, _period in enumerate(periods):
                period_key = "" if period_idx == 0 else str(num_periods - period_idx)

                gross_key = f"gross{period_key}" if period_key else "gross"
                amort_key = f"amort{period_key}" if period_key else "amort"
                net_key = f"net{period_key}" if period_key else "net"

                if value_idx != (len(row) - 1):
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
        statement_type: str = "statement",
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
                "reference": reference,
                "label": label,
            }

            num_periods = len(periods)

            for period_idx, _period in enumerate(periods):
                period_key = "" if period_idx == 0 else str(num_periods - period_idx)
                net_key = f"net{period_key}" if period_key else "net"

                value_idx = period_idx + 1
                record[net_key] = OHADAJSONFormatter.numpy_to_serializable(row[value_idx])

            result.append(record)

        return result

    # ---------------------------------------------------------
    # HIERARCHICAL FORMATTING
    # ---------------------------------------------------------
    @staticmethod
    def build_hierarchy(flat_records: List[Dict[str, Any]], parent_map: Dict[str, Optional[str]]) -> List[Dict[str, Any]]:
        """
        Build a hierarchical tree from flat records using parent-child relationships.

        Args:
            flat_records: List of flat records from format_assets or format_statement
            parent_map: Dictionary mapping reference -> parent_reference (None for roots)

        Returns:
            List of root nodes with nested children structure
        """
        # Build a lookup by reference
        records_by_ref = {record["reference"]: record.copy() for record in flat_records}
        
        # Initialize children lists for all records
        for record in records_by_ref.values():
            record["children"] = []
        
        # Track orphans
        orphans = []
        
        # Build the tree structure
        roots = []
        for ref, record in records_by_ref.items():
            parent_ref = parent_map.get(ref)
            
            if parent_ref is None:
                # This is a root node
                roots.append(record)
            elif parent_ref in records_by_ref:
                # Add to parent's children
                records_by_ref[parent_ref]["children"].append(record)
            else:
                # Orphan: parent not found in records
                logger.warning(f"Orphan reference '{ref}' has parent '{parent_ref}' not found in records. Placing at root.")
                orphans.append(record)
                roots.append(record)
        
        # Add orphans to roots if they weren't already added
        for orphan in orphans:
            if orphan not in roots:
                roots.append(orphan)
        
        return roots

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
        from ..core.schemas import (
            ASSETS_ACCOUNTS,
            CASHFLOW_ACCOUNTS,
            INCOME_ACCOUNTS,
            LIABILITIES_ACCOUNTS,
            OTHER_ACCOUNTS,
        )

        periods = statement.periods if len(statement.periods) > 2 else statement.periods[::-1]
        return {
            "metadata": OHADAJSONFormatter.format_metadata(statement.metadata),
            "extraction_metadata": {
                "periods": periods,
                "statement_types": [
                    "balance_sheet_assets",
                    "balance_sheet_liabilities",
                    "income",
                    "cashflow",
                    "other_data",
                    "notes",
                    "metadata",
                ],
            },
            "balance_sheet": {
                "assets": OHADAJSONFormatter.format_assets(statement._asset_data, periods, ASSETS_ACCOUNTS),
                "liabilities": OHADAJSONFormatter.format_statement(
                    statement._liability_data,
                    periods,
                    LIABILITIES_ACCOUNTS,
                    "liabilities",
                ),
            },
            "income_statement": OHADAJSONFormatter.format_statement(
                statement._income_data, periods, INCOME_ACCOUNTS, "income"
            ),
            "cashflow_statement": OHADAJSONFormatter.format_statement(
                statement._cashflow_data, periods, CASHFLOW_ACCOUNTS, "cashflow"
            ),
            "other_data": OHADAJSONFormatter.format_statement(
                statement._other_data, periods, OTHER_ACCOUNTS, "other_data"
            ),
            "notes": OHADAJSONFormatter.format_notes(statement.notes),
        }

    @staticmethod
    def format_statement_data_hierarchical(statement) -> Dict[str, Any]:
        """
        Format a FinancialStatement object into a hierarchical JSON-ready dictionary.

        Returns:
            Dictionary with formatted statements in hierarchical tree structure
        """
        from ..core.schemas import (
            ASSETS_ACCOUNTS,
            ASSETS_PARENTS,
            CASHFLOW_ACCOUNTS,
            CASHFLOW_PARENTS,
            INCOME_ACCOUNTS,
            INCOME_PARENTS,
            LIABILITIES_ACCOUNTS,
            LIABILITIES_PARENTS,
            OTHER_ACCOUNTS,
        )

        periods = statement.periods if len(statement.periods) > 2 else statement.periods[::-1]
        
        # Generate flat records using existing formatters
        flat_assets = OHADAJSONFormatter.format_assets(statement._asset_data, periods, ASSETS_ACCOUNTS)
        flat_liabilities = OHADAJSONFormatter.format_statement(
            statement._liability_data,
            periods,
            LIABILITIES_ACCOUNTS,
            "liabilities",
        )
        flat_income = OHADAJSONFormatter.format_statement(
            statement._income_data, periods, INCOME_ACCOUNTS, "income"
        )
        flat_cashflow = OHADAJSONFormatter.format_statement(
            statement._cashflow_data, periods, CASHFLOW_ACCOUNTS, "cashflow"
        )
        flat_other = OHADAJSONFormatter.format_statement(
            statement._other_data, periods, OTHER_ACCOUNTS, "other_data"
        )
        
        # Build hierarchical trees
        hierarchical_assets = OHADAJSONFormatter.build_hierarchy(flat_assets, ASSETS_PARENTS)
        hierarchical_liabilities = OHADAJSONFormatter.build_hierarchy(flat_liabilities, LIABILITIES_PARENTS)
        hierarchical_income = OHADAJSONFormatter.build_hierarchy(flat_income, INCOME_PARENTS)
        hierarchical_cashflow = OHADAJSONFormatter.build_hierarchy(flat_cashflow, CASHFLOW_PARENTS)
        
        return {
            "metadata": OHADAJSONFormatter.format_metadata(statement.metadata),
            "extraction_metadata": {
                "periods": periods,
                "statement_types": [
                    "balance_sheet_assets",
                    "balance_sheet_liabilities",
                    "income",
                    "cashflow",
                    "other_data",
                    "notes",
                    "metadata",
                ],
                "format": "hierarchical",
            },
            "balance_sheet": {
                "assets": hierarchical_assets,
                "liabilities": hierarchical_liabilities,
            },
            "income_statement": hierarchical_income,
            "cashflow_statement": hierarchical_cashflow,
            "other_data": flat_other,  # other_data has no parent mapping, keep flat
            "notes": OHADAJSONFormatter.format_notes(statement.notes),
        }

    # ---------------------------------------------------------
    # JSON STRING OUTPUT (UPDATED)
    # ---------------------------------------------------------
    @staticmethod
    def to_json(statement, indent: int = 2, hierarchical: bool = False) -> str:
        """
        Convert all statements to JSON string.

        Args:
            indent: JSON indentation level (None for compact)
            hierarchical: If True, output hierarchical tree structure; if False, output flat lists

        Returns:
            JSON string
        """
        if hierarchical:
            data = OHADAJSONFormatter.format_statement_data_hierarchical(statement)
        else:
            data = OHADAJSONFormatter.format_statement_data(statement)
        return json.dumps(data, indent=indent, default=OHADAJSONFormatter.numpy_to_serializable)
