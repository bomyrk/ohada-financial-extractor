"""Static (matplotlib) plotting for all financial data types in a 2×2 grid."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import (
    get_account_label,
    prepare_data_for_plotting,
)


def plot_all_static(statement, style, period, value_type):
    """Create static 2×2 grid plot for all financial data types.

    Args:
        statement: FinancialStatement instance
        style: 'bar', 'line', 'area'
        period: 'all' or specific year
        value_type: 'Net', 'Gross', 'Amort' (assets only)
    """

    fig, axes = plt.subplots(2, 2, figsize=(22, 14))
    axes = axes.flatten()

    data_types = ["assets", "liabilities", "income", "cashflow"]

    for ax, data_type in zip(axes, data_types):

        data = prepare_data_for_plotting(
            statement, data_type, period, value_type
        )

        # --------------------------------------------------------
        # NETTOYAGE XARRAY : Nettoyage des lignes à zéro
        # --------------------------------------------------------
        dim_to_reduce = "annee" if "annee" in data.dims else None
        if dim_to_reduce:
            max_vals = np.abs(data.values).max(
                axis=data.dims.index(dim_to_reduce)
            )
        else:
            max_vals = np.abs(data.values)

        non_zero_indices = np.where(max_vals > 1e-2)[0]
        if len(non_zero_indices) > 0:
            data = data.isel(compte=non_zero_indices)

        # --------------------------------------------------------
        # EXTRACTION ROBUSTE DES LABELS
        # --------------------------------------------------------
        if "Reference" in data.coords:
            labels = [
                get_account_label(statement, data_type, ref)
                for ref in data.coords["Reference"].values
            ]
        elif (
            hasattr(data.compte, "values")
            and len(data.compte.values) > 0
            and isinstance(data.compte.values[0], tuple)
        ):
            labels = [item[0] for item in data.compte.values]
        else:
            labels = [str(c) for c in data.compte.values]

        # Résolution de la chaîne descriptive de la période
        period_label = (
            "All Periods"
            if period == "all"
            else str(pd.to_datetime(period).year)
        )

        # -----------------------------
        # BAR PLOT
        # -----------------------------
        if style == "bar":
            if period == "all":
                x = np.arange(len(labels))
                width = 0.8 / len(data.annee)

                for idx, year in enumerate(data.annee.values):
                    year_str = str(pd.to_datetime(year).year)
                    vals = data.sel(annee=year).values.flatten()
                    ax.bar(
                        x + idx * width,
                        vals,
                        width=width,
                        label=year_str,
                    )
                # Centrage correct des tics de l'axe X pour les barres groupées
                ax.set_xticks(x + width * (len(data.annee) - 1) / 2)
            else:
                vals = data.values.flatten()
                ax.bar(labels, vals, label=period_label)

        # -----------------------------
        # LINE PLOT
        # -----------------------------
        elif style == "line":
            if period == "all":
                for year in data.annee.values:
                    year_str = str(pd.to_datetime(year).year)
                    vals = data.sel(annee=year).values.flatten()
                    ax.plot(
                        labels,
                        vals,
                        marker="o",
                        label=year_str,
                    )
            else:
                vals = data.values.flatten()
                ax.plot(labels, vals, marker="o", label=period_label)

        # -----------------------------
        # AREA PLOT
        # -----------------------------
        elif style == "area":
            if period == "all":
                for year in data.annee.values:
                    year_str = str(pd.to_datetime(year).year)
                    vals = data.sel(annee=year).values.flatten()
                    ax.fill_between(
                        labels,
                        vals,
                        alpha=0.3,
                        label=year_str,
                    )
            else:
                vals = data.values.flatten()
                ax.fill_between(labels, vals, alpha=0.5, label=period_label)

        # -----------------------------
        # Formatting & Cleanup
        # -----------------------------
        title_context = (
            f" ({value_type})" if data_type == "assets" else " (Net)"
        )
        ax.set_title(
            f"{data_type.capitalize()}{title_context} - {period_label}",
            fontsize=12,
            fontweight="bold",
        )
        ax.set_xlabel("Accounts", fontsize=10)
        ax.set_ylabel("Values", fontsize=10)

        # Application propre des étiquettes sémantiques pivotées
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.5)

        # N'affiche la légende que s'il y a des éléments à distinguer
        if period == "all" or style != "bar":
            ax.legend(title="Periods", loc="upper right")

    # Titre global de la figure unifiée
    fig.suptitle(
        f"Comprehensive Financial Dashboard Evolution ({period_label})",
        fontsize=16,
        fontweight="bold",
        y=0.99,
    )

    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.001)