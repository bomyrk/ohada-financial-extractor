import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import get_account_label


def _extract_xarray_data(data_array, refs, years):
    """Sélectionne de manière robuste les données xarray pour une liste de références."""
    # Gestion du MultiIndex ou de l'index simple pour la dimension 'compte'
    if "Reference" in data_array.coords:
        # Si la coordonnée Reference existe explicitement
        sub_data = data_array.sel(annee=years)
        # Filtrage manuel sur l'axe compte pour éviter les pièges d'IndexSlice
        mask = [
            ref in refs for ref in sub_data.coords["Reference"].values
        ]
        return sub_data.isel(compte=mask)
    else:
        # Fallback classique si l'index est plat ou standard
        return data_array.sel(compte=refs, annee=years, method=None)


def plot_asset_summary_static(statement, period="all"):
    """Static summary plots for Assets (clean xarray version)."""

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    if period != "all":
        period_dt = pd.Timestamp(period)
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [str(period_dt.year)]
        title_period = str(period_dt.year)
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    # --- Data selection ---
    asset_data = statement.asset.sel(valeur="Net")
    refs = ["AZ", "BK", "BT"]
    total_ref = "BZ"

    labels = {
        ref: get_account_label(statement, "assets", ref) for ref in refs
    }

    component_data = _extract_xarray_data(
        asset_data, refs, years_to_plot_dt
    )
    
    # Extraction propre du total
    if "Reference" in asset_data.coords:
        total_mask = asset_data.coords["Reference"].values == total_ref
        total_data = asset_data.isel(compte=total_mask).sel(annee=years_to_plot_dt).values.flatten()
    else:
        total_data = asset_data.sel(compte=total_ref, annee=years_to_plot_dt).values.flatten()

    # --- Remove zero-only components ---
    max_vals = np.abs(component_data.values).max(axis=0) if component_data.values.ndim > 1 else np.abs(component_data.values)
    non_zero_mask = max_vals > 1e-2
    
    if int(non_zero_mask.sum()) == 0:
        print("Aucune donnée non nulle à afficher pour les Actifs.")
        return

    component_data = component_data.isel(compte=non_zero_mask)
    refs = [r for r, keep in zip(refs, non_zero_mask) if keep]
    labels = {ref: labels[ref] for ref in refs}

    # --- Figure ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(
        f"Asset Summary Analysis ({title_period})", fontsize=16, y=1.02
    )

    # ============================================================
    # SUBPLOT 1 — GROUPED BARS
    # ============================================================
    ax1.set_title("Key Asset Components", fontsize=14)
    ax1.set_ylabel("Value")

    x = np.arange(len(years_to_plot_str))
    width = 0.8 / len(refs)

    for idx, ref in enumerate(refs):
        if "Reference" in component_data.coords:
            ref_mask = component_data.coords["Reference"].values == ref
            series_vals = component_data.isel(compte=ref_mask).values.flatten()
        else:
            series_vals = component_data.sel(compte=ref).values.flatten()

        ax1.bar(
            x + idx * width,
            series_vals,
            width,
            label=labels[ref],
        )
        for i, v in enumerate(series_vals):
            ax1.text(
                x[i] + idx * width,
                v,
                f"{v:,.0f}",
                ha="center",
                va="bottom" if v >= 0 else "top",
                fontsize=9,
            )

    ax1.set_xticks(x + width * (len(refs) - 1) / 2)
    ax1.set_xticklabels(years_to_plot_str, rotation=45)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # ============================================================
    # SUBPLOT 2 — STACKED BARS WITH % LABELS
    # ============================================================
    ax2.set_title("Total Assets Breakdown", fontsize=14)
    ax2.set_ylabel("Value")

    bottom = np.zeros(len(years_to_plot_str))

    for ref in refs:
        if "Reference" in component_data.coords:
            ref_mask = component_data.coords["Reference"].values == ref
            series_vals = component_data.isel(compte=ref_mask).values.flatten()
        else:
            series_vals = component_data.sel(compte=ref).values.flatten()

        ax2.bar(
            years_to_plot_str,
            series_vals,
            bottom=bottom,
            label=labels[ref],
        )
        
        # Calcul du pourcentage sécurisé contre la division par zéro
        pcts = np.where(total_data != 0, (series_vals / total_data) * 100, 0)

        for i, (b, v, p) in enumerate(zip(bottom, series_vals, pcts)):
            if abs(v) > 0:
                ax2.text(
                    years_to_plot_str[i],
                    b + v / 2,  # Centre le texte au milieu du segment pour une meilleure lisibilité
                    f"{p:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white" if b+v > 1e6 else "black", # Petit trick visuel contrasté
                )
        bottom += series_vals

    ax2.set_xticklabels(years_to_plot_str, rotation=45)
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_liability_summary_static(statement, period="all"):
    """Static summary plots for Liabilities (clean xarray version)."""

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    if period != "all":
        period_dt = pd.Timestamp(period)
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [str(period_dt.year)]
        title_period = str(period_dt.year)
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    liab_data = statement.liability
    refs = ["DF", "DP", "DT"]
    total_ref = "DZ"

    labels = {
        ref: get_account_label(statement, "liabilities", ref) for ref in refs
    }

    component_data = _extract_xarray_data(
        liab_data, refs, years_to_plot_dt
    )
    
    if "Reference" in liab_data.coords:
        total_mask = liab_data.coords["Reference"].values == total_ref
        total_data = liab_data.isel(compte=total_mask).sel(annee=years_to_plot_dt).values.flatten()
    else:
        total_data = liab_data.sel(compte=total_ref, annee=years_to_plot_dt).values.flatten()

    max_vals = np.abs(component_data.values).max(axis=0) if component_data.values.ndim > 1 else np.abs(component_data.values)
    non_zero_mask = max_vals > 1e-2
    
    if int(non_zero_mask.sum()) == 0:
        print("Aucune donnée non nulle pour le Passif.")
        return

    component_data = component_data.isel(compte=non_zero_mask)
    refs = [r for r, keep in zip(refs, non_zero_mask) if keep]
    labels = {ref: labels[ref] for ref in refs}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(
        f"Liability Summary Analysis ({title_period})", fontsize=16, y=1.02
    )

    # Subplot 1 — Grouped Bars
    ax1.set_title("Key Liability/Equity Components", fontsize=14)
    ax1.set_ylabel("Value")
    x = np.arange(len(years_to_plot_str))
    width = 0.8 / len(refs)

    for idx, ref in enumerate(refs):
        if "Reference" in component_data.coords:
            ref_mask = component_data.coords["Reference"].values == ref
            series_vals = component_data.isel(compte=ref_mask).values.flatten()
        else:
            series_vals = component_data.sel(compte=ref).values.flatten()

        ax1.bar(x + idx * width, series_vals, width, label=labels[ref])
        for i, v in enumerate(series_vals):
            ax1.text(
                x[i] + idx * width,
                v,
                f"{v:,.0f}",
                ha="center",
                va="bottom" if v >= 0 else "top",
                fontsize=9,
            )

    ax1.set_xticks(x + width * (len(refs) - 1) / 2)
    ax1.set_xticklabels(years_to_plot_str, rotation=45)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Subplot 2 — Stacked Bars
    ax2.set_title("Total Liabilities & Equity Breakdown", fontsize=14)
    ax2.set_ylabel("Value")
    bottom = np.zeros(len(years_to_plot_str))

    for ref in refs:
        if "Reference" in component_data.coords:
            ref_mask = component_data.coords["Reference"].values == ref
            series_vals = component_data.isel(compte=ref_mask).values.flatten()
        else:
            series_vals = component_data.sel(compte=ref).values.flatten()

        ax2.bar(years_to_plot_str, series_vals, bottom=bottom, label=labels[ref])
        pcts = np.where(total_data != 0, (series_vals / total_data) * 100, 0)

        for i, (b, v, p) in enumerate(zip(bottom, series_vals, pcts)):
            if abs(v) > 0:
                ax2.text(
                    years_to_plot_str[i],
                    b + v / 2,
                    f"{p:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=9,
                )
        bottom += series_vals

    ax2.set_xticklabels(years_to_plot_str, rotation=45)
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_income_summary_static(statement, period="all"):
    """Static summary plots for Income (robust grouped + waterfall architecture)."""

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    if period != "all":
        period_dt = pd.Timestamp(period)
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [str(period_dt.year)]
        title_period = str(period_dt.year)
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    refs = ["XE", "XF", "XH", "RS", "XI"]
    labels = {
        ref: get_account_label(statement, "income", ref) for ref in refs
    }

    income_data = _extract_xarray_data(
        statement.income, refs, years_to_plot_dt
    )

    max_vals = np.abs(income_data.values).max(axis=0) if income_data.values.ndim > 1 else np.abs(income_data.values)
    non_zero_mask = max_vals > 1e-2
    income_data = income_data.isel(compte=non_zero_mask)
    refs = [r for r, keep in zip(refs, non_zero_mask) if keep]
    labels = {ref: labels[ref] for ref in refs}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(
        f"Income Summary Analysis ({title_period})", fontsize=16, y=1.02
    )

    # Subplot 1 — Grouped Bars
    ax1.set_title("Income Components Over Time", fontsize=14)
    x = np.arange(len(years_to_plot_str))
    width = 0.8 / len(refs)

    for idx, ref in enumerate(refs):
        if "Reference" in income_data.coords:
            ref_mask = income_data.coords["Reference"].values == ref
            series_vals = income_data.isel(compte=ref_mask).values.flatten()
        else:
            series_vals = income_data.sel(compte=ref).values.flatten()

        ax1.bar(x + idx * width, series_vals, width, label=labels[ref])
        for i, v in enumerate(series_vals):
            ax1.text(
                x[i] + idx * width,
                v,
                f"{v:,.0f}",
                ha="center",
                va="bottom" if v >= 0 else "top",
                fontsize=9,
            )

    ax1.set_xticks(x + width * (len(refs) - 1) / 2)
    ax1.set_xticklabels(years_to_plot_str, rotation=45)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # ============================================================
    # SUBPLOT 2 — TRUE WATERFALL OR MULTI-YEAR COMPARISON
    # ============================================================
    if len(years_to_plot_dt) == 1:
        # VRAI WATERFALL (Pour une année spécifique)
        ax2.set_title(f"Income Waterfall Evolution ({years_to_plot_str[0]})", fontsize=14)
        vals = income_data.values.flatten()
        
        # Construction des marches cumulatives
        cumulative = np.zeros(len(vals) + 1)
        cumulative[1:] = np.cumsum(vals)
        
        # Dessiner les blocs de cascade
        for i in range(len(vals)):
            color = "green" if vals[i] >= 0 else "red"
            ax2.bar(
                list(labels.values())[i],
                vals[i],
                bottom=cumulative[i],
                color=color,
                edgecolor="black"
            )
            ax2.text(
                i,
                cumulative[i] + vals[i],
                f"{vals[i]:+,.0f}",
                ha="center",
                va="bottom" if vals[i] >= 0 else "top",
                fontsize=9,
                weight="bold"
            )
    else:
        # Si multi-période : Graphique par année pour éviter les collisions destructrices
        ax2.set_title("Net Income Cascade Trends", fontsize=14)
        x_labels = list(labels.values())
        x_indices = np.arange(len(x_labels))
        year_width = 0.8 / len(years_to_plot_dt)
        
        for idx, year in enumerate(years_to_plot_dt):
            year_vals = income_data.sel(annee=year).values.flatten()
            ax2.bar(
                x_indices + idx * year_width,
                year_vals,
                year_width,
                label=str(pd.to_datetime(year).year)
            )
        ax2.set_xticks(x_indices + year_width * (len(years_to_plot_dt) - 1) / 2)
        ax2.set_xticklabels(x_labels, rotation=45, ha="right")

    ax2.legend()
    ax2.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_cashflow_summary_static(statement, period="all"):
    """Static summary plots for Cashflow (robust grouped + waterfall architecture)."""

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    if period != "all":
        period_dt = pd.Timestamp(period)
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [str(period_dt.year)]
        title_period = str(period_dt.year)
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    refs = ["ZB", "ZC", "ZF", "ZG"]
    labels = {
        ref: get_account_label(statement, "cashflow", ref) for ref in refs
    }

    cash_data = _extract_xarray_data(
        statement.cashflow, refs, years_to_plot_dt
    )

    max_vals = np.abs(cash_data.values).max(axis=0) if cash_data.values.ndim > 1 else np.abs(cash_data.values)
    non_zero_mask = max_vals > 1e-2
    cash_data = cash_data.isel(compte=non_zero_mask)
    refs = [r for r, keep in zip(refs, non_zero_mask) if keep]
    labels = {ref: labels[ref] for ref in refs}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(
        f"Cashflow Summary Analysis ({title_period})", fontsize=16, y=1.02
    )

    # Subplot 1 — Grouped Bars
    ax1.set_title("Cashflow Components", fontsize=14)
    x = np.arange(len(years_to_plot_str))
    width = 0.8 / len(refs)

    for idx, ref in enumerate(refs):
        if "Reference" in cash_data.coords:
            ref_mask = cash_data.coords["Reference"].values == ref
            series_vals = cash_data.isel(compte=ref_mask).values.flatten()
        else:
            series_vals = cash_data.sel(compte=ref).values.flatten()

        ax1.bar(x + idx * width, series_vals, width, label=labels[ref])
        for i, v in enumerate(series_vals):
            ax1.text(
                x[i] + idx * width,
                v,
                f"{v:,.0f}",
                ha="center",
                va="bottom" if v >= 0 else "top",
                fontsize=9,
            )

    ax1.set_xticks(x + width * (len(refs) - 1) / 2)
    ax1.set_xticklabels(years_to_plot_str, rotation=45)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Subplot 2 — Waterfall ou Multi-barres séquentiel
    if len(years_to_plot_dt) == 1:
        ax2.set_title(f"Cashflow Structural Change ({years_to_plot_str[0]})", fontsize=14)
        vals = cash_data.values.flatten()
        cumulative = np.zeros(len(vals) + 1)
        cumulative[1:] = np.cumsum(vals)

        for i in range(len(vals)):
            color = "skyblue" if vals[i] >= 0 else "coral"
            ax2.bar(
                list(labels.values())[i],
                vals[i],
                bottom=cumulative[i],
                color=color,
                edgecolor="black"
            )
            ax2.text(
                i,
                cumulative[i] + vals[i],
                f"{vals[i]:+,.0f}",
                ha="center",
                va="bottom" if vals[i] >= 0 else "top",
                fontsize=9,
            )
    else:
        ax2.set_title("Cashflow Dynamic Variance", fontsize=14)
        x_labels = list(labels.values())
        x_indices = np.arange(len(x_labels))
        year_width = 0.8 / len(years_to_plot_dt)

        for idx, year in enumerate(years_to_plot_dt):
            year_vals = cash_data.sel(annee=year).values.flatten()
            ax2.bar(
                x_indices + idx * year_width,
                year_vals,
                year_width,
                label=str(pd.to_datetime(year).year)
            )
        ax2.set_xticks(x_indices + year_width * (len(years_to_plot_dt) - 1) / 2)
        ax2.set_xticklabels(x_labels, rotation=45, ha="right")

    ax2.legend()
    ax2.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()