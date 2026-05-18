"""
Utility functions for OHADA visualization module.
Shared helpers for static and dynamic plotting.
"""

import numpy as np

# ----------------------------------------------------------------------
#  INPUT VALIDATION
# ----------------------------------------------------------------------


def validate_plot_inputs(data_type, plot_type, style):
    valid_data_types = {"assets", "liabilities", "income", "cashflow", "all"}
    valid_plot_types = {"static", "dynamic"}
    valid_styles = {"bar", "line", "area", "pie"}

    if data_type not in valid_data_types:
        raise ValueError(f"Invalid data_type. Choose from {valid_data_types}")

    if plot_type not in valid_plot_types:
        raise ValueError(f"Invalid plot_type. Choose from {valid_plot_types}")

    if style not in valid_styles:
        raise ValueError(f"Invalid style. Choose from {valid_styles}")


# ----------------------------------------------------------------------
#  NORMALIZATION
# ----------------------------------------------------------------------


def normalize_data_type(data_type: str) -> str:
    """Normalize variations like 'liability' → 'liabilities'."""
    mapping = {
        "asset": "assets",
        "assets": "assets",
        "liability": "liabilities",
        "liabilities": "liabilities",
        "income": "income",
        "cashflow": "cashflow",
        "all": "all",
    }
    return mapping.get(data_type.lower(), data_type)


# ----------------------------------------------------------------------
#  DATA PREPARATION
# ----------------------------------------------------------------------


def prepare_data_for_plotting(statement, data_type, period="all", value_type="Net"):
    """
    Extract the correct xarray slice for plotting.
    Handles:
        - assets (Gross/Amort/Net)
        - liabilities/income/cashflow (Net only)
        - single period or all periods
    """

    # Map data_type → attribute name
    attr_map = {
        "assets": "asset",
        "liabilities": "liability",
        "income": "income",
        "cashflow": "cashflow",
    }

    data = getattr(statement, attr_map[data_type])

    # Assets have a 'valeur' dimension
    if data_type == "assets":
        if period == "all":
            return data.sel(valeur=value_type)
        else:
            return data.sel(valeur=value_type, annee=period)

    # Others: no valeur dimension
    else:
        if period == "all":
            return data
        else:
            return data.sel(annee=period)


# ----------------------------------------------------------------------
#  LABEL RESOLUTION
# ----------------------------------------------------------------------


def get_account_label(statement, data_type, ref_code):
    """
    Resolve the human-readable label for a given OHADA reference code.
    Works with MultiIndex accounts.
    """

    # Determine which MultiIndex to use, Mat data_type to 
    # the actuaal xarray DataArray attribute on the statement
    attr_map = {
        "assets": "asset",
        "liabilities": "liability",
        "income": "income",
        "cashflow": "cashflow",
    }

    # 2. Get the xarray DataArray (e.g., statement.asset)
    data_array = getattr(statement, attr_map[data_type])

    # 3. Retrieve the MultiIndex associated with the 'compte' coordinate
    # xarray maps MultiIndex levels onto both data coordinates and components
    try:
        # We find the specific position where the level 'Reference' matches our ref_code
        references = data_array.coords["Reference"].values
        libelles = data_array.coords["Label"].values

        # Look for the match index
        match_indices = np.where(references == ref_code)[0]
        if len(match_indices) > 0:
            # Return the label corresponding to the first match
            return str(libelles[match_indices[0]])

    except Exception:
        pass

    # Final fallback if nothing is found or coordinate extraction fails
    return ref_code
