"""
Data Cleaning Utilities for OHADA Financial Statements

Provides functions to clean, validate, and normalize extracted financial data.
"""

from typing import Any, Dict, List


def remove_empty(data: List[Dict]) -> List[Dict]:
    """
    Remove records with missing required fields.

    Filters out records that don't have both 'reference' and 'net' fields,
    ensuring data quality in the final output.

    Args:
        data: List of financial statement records

    Returns:
        List of records with all required fields present

    Example:
        >>> records = [
        ...     {'reference': 'AD', 'net': 1000},
        ...     {'reference': 'AE'},  # Missing 'net'
        ...     {'net': 500}  # Missing 'reference'
        ... ]
        >>> remove_empty(records)
        [{'reference': 'AD', 'net': 1000}]
    """
    resp = []
    for line in data:
        if "reference" in line.keys() and "net" in line.keys():
            resp.append(line)
    return resp


def remove_unnecessary(data: Any) -> Any:
    """
    Recursively remove non-financial keys from nested data structures.

    Keeps only: 'reference', 'range', 'rubriques', 'posts'
    Applies recursively to lists and dictionaries, removing metadata
    and temporary fields used during processing.

    Args:
        data: Data structure (dict, list, or scalar) to clean

    Returns:
        Cleaned data with only essential keys retained

    Example:
        >>> messy = {
        ...     'reference': 'AD',
        ...     'label': 'Intangible Assets',  # Removed
        ...     'temp_id': 123,  # Removed
        ...     'posts': [
        ...         {'reference': 'AE', 'label': 'Dev', 'net': 500}
        ...     ]
        ... }
        >>> remove_unnecessary(messy)
        {'reference': 'AD', 'posts': [{'reference': 'AE', 'net': 500}]}
    """
    if isinstance(data, list):
        resp = []
        for item in data:
            resp.append(remove_unnecessary(item))
        return resp
    elif isinstance(data, dict):
        resp = dict()
        for key in data.keys():
            if key in ["reference", "range", "rubriques", "posts"]:
                resp[key] = remove_unnecessary(data[key])
        return resp
    else:
        return data
