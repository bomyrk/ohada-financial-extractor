"""Static (matplotlib) plotting for a single financial data type."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import (
    get_account_label,
    prepare_data_for_plotting,
)


def plot_single_static(statement, data_type, style, period, value_type):
    """Create static plot for a single financial data type.

    Args:
        statement: FinancialStatement instance
        data_type: 'assets', 'liabilities', 'income', 'cashflow'
        style: 'bar', 'line', 'area', 'pie'
        period: 'all' or specific year
        value_type: 'Net', 'Gross', 'Amort' (assets only)
    """

    # Prepare xarray slice
    data = prepare_data_for_plotting(statement, data_type, period, value_type)

    # --------------------------------------------------------
    # NETTOYAGE XARRAY : Éliminer les comptes entièrement à zéro
    # --------------------------------------------------------
    dim_to_reduce = "annee" if "annee" in data.dims else None
    if dim_to_reduce:
        max_vals = np.abs(data.values).max(axis=data.dims.index(dim_to_reduce))
    else:
        max_vals = np.abs(data.values)

    non_zero_indices = np.where(max_vals > 1e-2)[0]
    if len(non_zero_indices) == 0:
        print(f"Aucune donnée non nulle à afficher pour '{data_type}'.")
        return

    data = data.isel(compte=non_zero_indices)

    # --------------------------------------------------------
    # EXTRACTION ROBUSTE DES LABELS (Nomenclature OHADA)
    # --------------------------------------------------------
    if "Reference" in data.coords:
        labels = [get_account_label(statement, data_type, ref) for ref in data.coords["Reference"].values]
    elif hasattr(data.compte, "values") and len(data.compte.values) > 0 and isinstance(data.compte.values[0], tuple):
        labels = [item[0] for item in data.compte.values]
    else:
        labels = [str(c) for c in data.compte.values]

    fig, ax = plt.subplots(figsize=(15, 8))

    # -----------------------------
    # BAR PLOT
    # -----------------------------
    if style == "bar":
        if period == "all":
            x = np.arange(len(labels))
            width = 0.8 / len(data.annee)

            for idx, year in enumerate(data.annee.values):
                year_label = str(pd.to_datetime(year).year)
                # .flatten() ou .values pour casser le conteneur xarray
                vals = data.sel(annee=year).values.flatten()
                ax.bar(
                    x + idx * width,
                    vals,
                    width=width,
                    label=year_label,
                )
            ax.set_xticks(x + width * (len(data.annee) - 1) / 2)
            ax.set_xticklabels(labels, rotation=45, ha="right")
        else:
            vals = data.values.flatten()
            ax.bar(labels, vals)
            ax.set_xticklabels(labels, rotation=45, ha="right")

    # -----------------------------
    # LINE PLOT
    # -----------------------------
    elif style == "line":
        if period == "all":
            for year in data.annee.values:
                year_label = str(pd.to_datetime(year).year)
                vals = data.sel(annee=year).values.flatten()
                ax.plot(
                    labels,
                    vals,
                    marker="o",
                    label=year_label,
                )
        else:
            vals = data.values.flatten()
            ax.plot(labels, vals, marker="o")
        ax.set_xticklabels(labels, rotation=45, ha="right")

    # -----------------------------
    # AREA PLOT
    # -----------------------------
    elif style == "area":
        if period == "all":
            for year in data.annee.values:
                year_label = str(pd.to_datetime(year).year)
                vals = data.sel(annee=year).values.flatten()
                ax.fill_between(
                    labels,
                    vals,
                    alpha=0.3,
                    label=year_label,
                )
        else:
            vals = data.values.flatten()
            ax.fill_between(labels, vals, alpha=0.5)
        ax.set_xticklabels(labels, rotation=45, ha="right")

    # -----------------------------
    # PIE PLOT (Sécurisé pour la finance)
    # -----------------------------
    elif style == "pie":
        if period == "all":
            raise ValueError("Les graphiques en secteurs (Pie charts) requièrent une seule période, pas 'all'.")

        vals = data.values.flatten()

        # Filtrage strict contre les valeurs négatives ou nulles (ex: pertes, cashflow négatif)
        positive_mask = vals > 0
        filtered_vals = vals[positive_mask]
        filtered_labels = [lab for lab, keep in zip(labels, positive_mask, strict=False) if keep]

        if len(filtered_vals) == 0:
            raise ValueError(
                f"Impossible de générer un Pie Chart : toutes" f"les valeurs pour {data_type} sont négatives ou nulles."
            )

        ax.pie(
            filtered_vals,
            labels=filtered_labels,
            autopct="%1.1f%%",
            startangle=140,
        )
        # Supprime les labels d'axes inutiles pour un Pie chart
        ax.set_xlabel("")
        ax.set_ylabel("")

    # -----------------------------
    # Formatting
    # -----------------------------
    title_value = f"Value Type: {value_type}" if data_type == "assets" else "Net Values"
    period_title = "All Periods" if period == "all" else str(pd.to_datetime(period).year)

    ax.set_title(
        f"{data_type.capitalize()} Structural Analysis ({period_title} -{title_value})",
        fontsize=14,
        fontweight="bold",
    )

    if style != "pie":
        ax.set_xlabel("Financial Accounts / Rubrics", fontsize=11)
        ax.set_ylabel("Amounts", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Periods")

    plt.tight_layout()
    plt.show()
