"""
Static (matplotlib) plotting for all financial data types in a 2×2 grid.
"""

import matplotlib.pyplot as plt
import numpy as np

from ..utils import (
    prepare_data_for_plotting,
)


def plot_all_static(statement, style, period, value_type):
    """
    Create static 2×2 grid plot for all financial data types.

    Args:
        statement: FinancialStatement instance
        style: 'bar', 'line', 'area'
        period: 'all' or specific year
        value_type: 'Net', 'Gross', 'Amort' (assets only)
    """

    fig, axes = plt.subplots(2, 2, figsize=(20, 15))
    axes = axes.flatten()

    data_types = ["assets", "liabilities", "income", "cashflow"]

    for ax, data_type in zip(axes, data_types):

        data = prepare_data_for_plotting(statement, data_type, period, value_type)

        # Extract labels
        if isinstance(data.compte.values[0], tuple):
            labels = [item[0] for item in data.compte.values]
        else:
            labels = data.compte.values

        # -----------------------------
        # BAR PLOT
        # -----------------------------
        if style == "bar":
            if period == "all":
                x = np.arange(len(labels))
                width = 0.8 / len(data.annee)

                for idx, year in enumerate(data.annee.values):
                    ax.bar(
                        x + idx * width,
                        data.sel(annee=year),
                        width=width,
                        label=str(year)[:10],
                    )
            else:
                ax.bar(labels, data.values)

        # -----------------------------
        # LINE PLOT
        # -----------------------------
        elif style == "line":
            if period == "all":
                for year in data.annee.values:
                    ax.plot(
                        labels,
                        data.sel(annee=year),
                        marker="o",
                        label=str(year)[:10],
                    )
            else:
                ax.plot(labels, data.values, marker="o")

        # -----------------------------
        # AREA PLOT
        # -----------------------------
        elif style == "area":
            if period == "all":
                for year in data.annee.values:
                    ax.fill_between(
                        labels,
                        data.sel(annee=year),
                        alpha=0.3,
                        label=str(year)[:10],
                    )
            else:
                ax.fill_between(labels, data.values, alpha=0.5)

        # -----------------------------
        # Formatting
        # -----------------------------
        ax.set_title(f"{data_type.capitalize()} Analysis")
        ax.set_xlabel("Accounts")
        ax.set_ylabel("Values")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)
        ax.legend()

    plt.tight_layout()
    plt.show()
