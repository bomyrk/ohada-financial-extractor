"""
Static (matplotlib) plotting for a single financial data type.
"""

import matplotlib.pyplot as plt
import numpy as np

from ..utils import (
    prepare_data_for_plotting,
    get_account_label,
)


def plot_single_static(statement, data_type, style, period, value_type):
    """
    Create static plot for a single financial data type.

    Args:
        statement: FinancialStatement instance
        data_type: 'assets', 'liabilities', 'income', 'cashflow'
        style: 'bar', 'line', 'area', 'pie'
        period: 'all' or specific year
        value_type: 'Net', 'Gross', 'Amort' (assets only)
    """

    # Prepare xarray slice
    data = prepare_data_for_plotting(statement, data_type, period, value_type)

    # Extract labels from MultiIndex
    if isinstance(data.compte.values[0], tuple):
        labels = [item[0] for item in data.compte.values]
    else:
        labels = data.compte.values

    plt.figure(figsize=(15, 8))

    # -----------------------------
    # BAR PLOT
    # -----------------------------
    if style == "bar":
        if period == "all":
            x = np.arange(len(labels))
            width = 0.8 / len(data.annee)

            for idx, year in enumerate(data.annee.values):
                plt.bar(
                    x + idx * width,
                    data.sel(annee=year),
                    width=width,
                    label=str(year)[:10],
                )
        else:
            plt.bar(labels, data.values)

    # -----------------------------
    # LINE PLOT
    # -----------------------------
    elif style == "line":
        if period == "all":
            for year in data.annee.values:
                plt.plot(
                    labels,
                    data.sel(annee=year),
                    marker="o",
                    label=str(year)[:10],
                )
        else:
            plt.plot(labels, data.values, marker="o")

    # -----------------------------
    # AREA PLOT
    # -----------------------------
    elif style == "area":
        if period == "all":
            for year in data.annee.values:
                plt.fill_between(
                    labels,
                    data.sel(annee=year),
                    alpha=0.3,
                    label=str(year)[:10],
                )
        else:
            plt.fill_between(labels, data.values, alpha=0.5)

    # -----------------------------
    # PIE PLOT
    # -----------------------------
    elif style == "pie":
        if period == "all":
            raise ValueError("Pie charts require a single period, not 'all'.")
        plt.pie(data.values, labels=labels, autopct="%1.1f%%")

    # -----------------------------
    # Formatting
    # -----------------------------
    title_value = value_type if data_type == "assets" else "Net"
    plt.title(f"{data_type.capitalize()} Analysis ({title_value})")
    plt.xlabel("Accounts")
    plt.ylabel("Values")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.001)

