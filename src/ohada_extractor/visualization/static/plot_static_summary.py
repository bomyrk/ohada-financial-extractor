import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import get_account_label


def plot_asset_summary_static(statement, period="all"):
    """Static summary plots for Assets (clean version)."""

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    # --- Period selection ---
    if period != "all":
        period_dt = pd.Timestamp(period)
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [period_dt.strftime("%Y")]
        title_period = period_dt.strftime("%Y")
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    # --- Data selection ---
    asset_data = statement.asset.sel(valeur="Net")

    refs = ["AZ", "BK", "BT"]
    total_ref = "BZ"

    labels = {ref: get_account_label(statement, "assets", ref) for ref in refs}
    total_label = get_account_label(statement, "assets", total_ref)

    component_data = asset_data.sel(compte=pd.IndexSlice[:, refs], annee=years_to_plot_dt)
    total_data = asset_data.sel(compte=pd.IndexSlice[:, total_ref], annee=years_to_plot_dt).squeeze()

    # --- Remove zero-only components ---
    non_zero_mask = component_data.values.max(axis=0) != 0
    component_data = component_data[:, non_zero_mask]
    refs = [r for r, keep in zip(refs, non_zero_mask) if keep]
    labels = {ref: labels[ref] for ref in refs}

    # --- Compute % of total ---
    pct_data = {
        ref: (
            component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze().values
            / total_data.values * 100
        )
        for ref in refs
    }

    # --- Figure ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(f"Asset Summary Analysis ({title_period})", fontsize=16, y=1.02)

    # ============================================================
    #  SUBPLOT 1 — GROUPED BARS WITH VALUE LABELS
    # ============================================================

    ax1.set_title("Key Asset Components", fontsize=14)
    ax1.set_ylabel("Value")

    x = np.arange(len(years_to_plot_str))
    width = 0.8 / len(refs)

    for idx, ref in enumerate(refs):
        series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        ax1.bar(
            x + idx * width,
            series.values,
            width,
            label=labels[ref],
        )
        # Value labels
        for i, v in enumerate(series.values):
            ax1.text(
                x[i] + idx * width,
                v,
                f"{v:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax1.set_xticks(x + width * (len(refs) - 1) / 2)
    ax1.set_xticklabels(years_to_plot_str, rotation=45)
    ax1.legend()

    # ============================================================
    #  SUBPLOT 2 — STACKED BARS WITH % LABELS ABOVE
    # ============================================================

    ax2.set_title("Total Assets Breakdown", fontsize=14)
    ax2.set_ylabel("Value")

    bottom = np.zeros(len(years_to_plot_str))

    for ref in refs:
        series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        ax2.bar(
            years_to_plot_str,
            series.values,
            bottom=bottom,
            label=labels[ref],
        )
        # % labels above segment
        for i, (b, v, p) in enumerate(zip(bottom, series.values, pct_data[ref])):
            ax2.text(
                years_to_plot_str[i],
                b + v,
                f"{p:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )
        bottom += series.values

    ax2.set_xticklabels(years_to_plot_str, rotation=45)
    ax2.legend()

    ax1.grid(alpha=0.3)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_liability_summary_static(statement, period="all"):
    """Static summary plots for Liabilities (clean version)."""

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    # --- Period selection ---
    if period != "all":
        period_dt = pd.Timestamp(period)
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [period_dt.strftime("%Y")]
        title_period = period_dt.strftime("%Y")
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    # --- Data selection ---
    liab_data = statement.liability

    refs = ["DF", "DP", "DT"]
    total_ref = "DZ"

    labels = {ref: get_account_label(statement, "liabilities", ref) for ref in refs}
    total_label = get_account_label(statement, "liabilities", total_ref)

    component_data = liab_data.sel(compte=pd.IndexSlice[:, refs], annee=years_to_plot_dt)
    total_data = liab_data.sel(compte=pd.IndexSlice[:, total_ref], annee=years_to_plot_dt).squeeze()

    # --- Remove zero-only components ---
    non_zero_mask = component_data.values.max(axis=0) != 0
    component_data = component_data[:, non_zero_mask]
    refs = [r for r, keep in zip(refs, non_zero_mask) if keep]
    labels = {ref: labels[ref] for ref in refs}

    # --- Compute % of total ---
    pct_data = {
        ref: (
            component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze().values
            / total_data.values * 100
        )
        for ref in refs
    }

    # --- Figure ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(f"Liability Summary Analysis ({title_period})", fontsize=16, y=1.02)

    # ============================================================
    #  SUBPLOT 1 — GROUPED BARS WITH VALUE LABELS
    # ============================================================

    ax1.set_title("Key Liability/Equity Components", fontsize=14)
    ax1.set_ylabel("Value")

    x = np.arange(len(years_to_plot_str))
    width = 0.8 / len(refs)

    for idx, ref in enumerate(refs):
        series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        ax1.bar(
            x + idx * width,
            series.values,
            width,
            label=labels[ref],
        )
        # Value labels
        for i, v in enumerate(series.values):
            ax1.text(
                x[i] + idx * width,
                v,
                f"{v:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax1.set_xticks(x + width * (len(refs) - 1) / 2)
    ax1.set_xticklabels(years_to_plot_str, rotation=45)
    ax1.legend()

    # ============================================================
    #  SUBPLOT 2 — STACKED BARS WITH % LABELS ABOVE
    # ============================================================

    ax2.set_title("Total Liabilities & Equity Breakdown", fontsize=14)
    ax2.set_ylabel("Value")

    bottom = np.zeros(len(years_to_plot_str))

    for ref in refs:
        series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        ax2.bar(
            years_to_plot_str,
            series.values,
            bottom=bottom,
            label=labels[ref],
        )
        # % labels above segment
        for i, (b, v, p) in enumerate(zip(bottom, series.values, pct_data[ref])):
            ax2.text(
                years_to_plot_str[i],
                b + v,
                f"{p:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )
        bottom += series.values

    ax2.set_xticklabels(years_to_plot_str, rotation=45)
    ax2.legend()

    ax1.grid(alpha=0.3)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_income_summary_static(statement, period="all"):
    """Static summary plots for Income (grouped + waterfall)."""

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    # --- Period selection ---
    if period != "all":
        period_dt = pd.Timestamp(period)
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [period_dt.strftime("%Y")]
        title_period = period_dt.strftime("%Y")
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    # --- Data selection ---
    refs = ["XE", "XF", "XH", "RS", "XI"]
    labels = {ref: get_account_label(statement, "income", ref) for ref in refs}

    income_data = statement.income.sel(compte=pd.IndexSlice[:, refs], annee=years_to_plot_dt)

    # --- Remove zero-only components ---
    non_zero_mask = income_data.values.max(axis=0) != 0
    income_data = income_data[:, non_zero_mask]
    refs = [r for r, keep in zip(refs, non_zero_mask) if keep]
    labels = {ref: labels[ref] for ref in refs}

    # --- Figure ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(f"Income Summary Analysis ({title_period})", fontsize=16, y=1.02)

    # ============================================================
    #  SUBPLOT 1 — GROUPED BARS
    # ============================================================

    ax1.set_title("Income Components", fontsize=14)
    ax1.set_ylabel("Value")

    x = np.arange(len(years_to_plot_str))
    width = 0.8 / len(refs)

    for idx, ref in enumerate(refs):
        series = income_data.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        ax1.bar(
            x + idx * width,
            series.values,
            width,
            label=labels[ref],
        )
        # Value labels
        for i, v in enumerate(series.values):
            ax1.text(
                x[i] + idx * width,
                v,
                f"{v:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax1.set_xticks(x + width * (len(refs) - 1) / 2)
    ax1.set_xticklabels(years_to_plot_str, rotation=45)
    ax1.legend()

    # ============================================================
    #  SUBPLOT 2 — WATERFALL
    # ============================================================

    ax2.set_title("Income Waterfall", fontsize=14)
    ax2.set_ylabel("Value")

    for year in years_to_plot_dt:
        vals = income_data.sel(annee=year).squeeze().values
        steps = np.cumsum(vals)

        # Bars
        ax2.bar(labels.values(), vals, label=str(year.year))

        # Value labels
        for i, v in enumerate(vals):
            ax2.text(
                list(labels.values())[i],
                v,
                f"{v:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax2.set_xticklabels(labels.values(), rotation=45)
    ax2.legend()

    ax1.grid(alpha=0.3)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_cashflow_summary_static(statement, period="all"):
    """Static summary plots for Cashflow (grouped + waterfall)."""

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    # --- Period selection ---
    if period != "all":
        period_dt = pd.Timestamp(period)
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [period_dt.strftime("%Y")]
        title_period = period_dt.strftime("%Y")
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    # --- Data selection ---
    refs = ["ZB", "ZC", "ZF", "ZG"]
    labels = {ref: get_account_label(statement, "cashflow", ref) for ref in refs}

    cash_data = statement.cashflow.sel(compte=pd.IndexSlice[:, refs], annee=years_to_plot_dt)

    # --- Remove zero-only components ---
    non_zero_mask = cash_data.values.max(axis=0) != 0
    cash_data = cash_data[:, non_zero_mask]
    refs = [r for r, keep in zip(refs, non_zero_mask) if keep]
    labels = {ref: labels[ref] for ref in refs}

    # --- Figure ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(f"Cashflow Summary Analysis ({title_period})", fontsize=16, y=1.02)

    # ============================================================
    #  SUBPLOT 1 — GROUPED BARS
    # ============================================================

    ax1.set_title("Cashflow Components", fontsize=14)
    ax1.set_ylabel("Value")

    x = np.arange(len(years_to_plot_str))
    width = 0.8 / len(refs)

    for idx, ref in enumerate(refs):
        series = cash_data.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        ax1.bar(
            x + idx * width,
            series.values,
            width,
            label=labels[ref],
        )
        # Value labels
        for i, v in enumerate(series.values):
            ax1.text(
                x[i] + idx * width,
                v,
                f"{v:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax1.set_xticks(x + width * (len(refs) - 1) / 2)
    ax1.set_xticklabels(years_to_plot_str, rotation=45)
    ax1.legend()

    # ============================================================
    #  SUBPLOT 2 — WATERFALL
    # ============================================================

    ax2.set_title("Cashflow Waterfall", fontsize=14)
    ax2.set_ylabel("Value")

    for year in years_to_plot_dt:
        vals = cash_data.sel(annee=year).squeeze().values
        ax2.bar(labels.values(), vals, label=str(year.year))

        # Value labels
        for i, v in enumerate(vals):
            ax2.text(
                list(labels.values())[i],
                v,
                f"{v:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax2.set_xticklabels(labels.values(), rotation=45)
    ax2.legend()

    ax1.grid(alpha=0.3)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()
