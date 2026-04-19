"""
Base Plotter Router for OHADA Financial Visualization

This module provides a single entry point for all visualization calls.
It dispatches to:
    - static plots (matplotlib)
    - dynamic plots (plotly)
    - summary dashboards
"""

from .utils import (
    normalize_data_type,
    validate_plot_inputs,
    prepare_data_for_plotting,
    get_account_label,
)

# Static plot modules
from .static.plot_static_single import plot_single_static
from .static.plot_static_all import plot_all_static
from .static.plot_static_summary import (
    plot_asset_summary_static,
    plot_liability_summary_static,
)

# Dynamic plot modules
from .dynamic.plot_dynamic_single import plot_single_dynamic
from .dynamic.plot_dynamic_all import plot_all_dynamic
from .dynamic.plot_dynamic_summary import (
    plot_asset_summary_dynamic,
    plot_liability_summary_dynamic,
    plot_income_summary_dynamic,
    plot_cashflow_summary_dynamic,
)


# ----------------------------------------------------------------------
#  MAIN ROUTER
# ----------------------------------------------------------------------

def plot_router(statement, data_type="assets", plot_type="static",
                style="bar", period="all", value_type="Net", summary=False):
    """
    Central router for all visualization calls.

    Args:
        statement: FinancialStatement instance
        data_type: 'assets', 'liabilities', 'income', 'cashflow', 'all'
        plot_type: 'static' or 'dynamic'
        style: 'bar', 'line', 'area', 'pie'
        period: 'all' or specific year
        value_type: 'Net', 'Gross', 'Amort' (assets only)
        summary: if True → summary dashboards instead of raw plots
    """

    # Validate inputs
    validate_plot_inputs(data_type, plot_type, style)

    # Normalize data_type (e.g., "liability" → "liabilities")
    data_type = normalize_data_type(data_type)

    # Summary dashboards override everything
    if summary:
        return _route_summary(statement, data_type, plot_type, period)

    # Dispatch to static or dynamic
    if plot_type == "static":
        return _route_static(statement, data_type, style, period, value_type)

    elif plot_type == "dynamic":
        return _route_dynamic(statement, data_type, style, period, value_type)

    else:
        raise ValueError(f"Unknown plot_type: {plot_type}")


# ----------------------------------------------------------------------
#  STATIC ROUTING
# ----------------------------------------------------------------------

def _route_static(statement, data_type, style, period, value_type):
    if data_type == "all":
        return plot_all_static(statement, style, period, value_type)
    else:
        return plot_single_static(statement, data_type, style, period, value_type)


# ----------------------------------------------------------------------
#  DYNAMIC ROUTING
# ----------------------------------------------------------------------

def _route_dynamic(statement, data_type, style, period, value_type):
    if data_type == "all":
        return plot_all_dynamic(statement, style, period, value_type)
    else:
        return plot_single_dynamic(statement, data_type, style, period, value_type)


# ----------------------------------------------------------------------
#  SUMMARY ROUTING
# ----------------------------------------------------------------------

def _route_summary(statement, data_type, plot_type, period):
    if data_type == "assets":
        return (
            plot_asset_summary_dynamic(statement, period)
            if plot_type == "dynamic"
            else plot_asset_summary_static(statement, period)
        )

    elif data_type == "liabilities":
        return (
            plot_liability_summary_dynamic(statement, period)
            if plot_type == "dynamic"
            else plot_liability_summary_static(statement, period)
        )

    elif data_type == "income":
        return (
            plot_income_summary_dynamic(statement, period)
            if plot_type == "dynamic"
            else plot_income_summary_static(statement, period)
        )

    elif data_type == "cashflow":
        return (
            plot_cashflow_summary_dynamic(statement, period)
            if plot_type == "dynamic"
            else plot_liability_summary_static(statement, period)
        )

    else:
        raise ValueError("Summary plots are only available for assets or liabilities.")
