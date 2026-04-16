"""
Static (matplotlib) summary plots for Assets and Liabilities.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import (
    prepare_data_for_plotting,
    get_account_label,
)


def plot_asset_summary_static(statement, period="all"):
    """Static summary plots for Assets (components + total breakdown)."""

    years_dt = statement.years
    years_str = statement.years.strftime("%Y-%m-%d").to_list()

    if period != "all":
        period_dt = pd.Timestamp(period)
        if period_dt not in years_dt:
            raise ValueError(f"Period {period} not found. Available: {years_str}")
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [period_dt.strftime("%Y-%m-%d")]
        title_period = period_dt.strftime("%Y-%m-%d")
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    asset_data = statement.asset.sel(valeur="Net")

    az_ref, bk_ref, bt_ref = "AZ", "BK", "BT"
    bz_ref = "BZ"
    component_refs = [az_ref, bk_ref, bt_ref]
    component_labels = {
        ref: get_account_label(statement, "assets", ref) for ref in component_refs
    }
    bz_label = get_account_label(statement, "assets", bz_ref)

    component_data = asset_data.sel(
        compte=pd.IndexSlice[:, component_refs], annee=years_to_plot_dt
    )
    total_assets_data = asset_data.sel(
        compte=pd.IndexSlice[:, bz_ref], annee=years_to_plot_dt
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(f"Asset Summary Analysis ({title_period})", fontsize=16)

    # Plot 1: Key components
    ax1.set_title("Key Asset Components")
    ax1.set_ylabel("Value")

    if period == "all":
        x = np.arange(len(years_to_plot_str))
        width = 0.8 / len(component_refs)
        for idx, ref in enumerate(component_refs):
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)
            ax1.bar(
                x + idx * width,
                series.values,
                width,
                label=component_labels[ref],
            )
        ax1.set_xlabel("Year")
        ax1.set_xticks(x + width * (len(component_refs) - 1) / 2)
        ax1.set_xticklabels(years_to_plot_str, rotation=45, ha="right")
        ax1.legend(title="Components")
    else:
        series = component_data.squeeze(drop=True)
        labels = [
            component_labels[ref]
            for ref in series["compte"].to_index().get_level_values(1)
        ]
        ax1.bar(labels, series.values)
        ax1.set_xlabel("Asset Category")
        ax1.tick_params(axis="x", rotation=45)

    # Plot 2: Stacked total breakdown
    ax2.set_title("Total Assets Breakdown")
    ax2.set_ylabel("Value")

    if period == "all":
        bottom = np.zeros(len(years_to_plot_str))
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)
            ax2.bar(
                years_to_plot_str,
                series.values,
                label=component_labels[ref],
                bottom=bottom,
            )
            bottom += series.values
        total_series = total_assets_data.squeeze(drop=True)
        ax2.plot(
            years_to_plot_str,
            total_series.values,
            label=f"{bz_label} (Actual Total)",
            marker="o",
            linestyle="--",
            color="black",
        )
        ax2.set_xlabel("Year")
        ax2.tick_params(axis="x", rotation=45)
        ax2.legend()
    else:
        series = component_data.squeeze(drop=True)
        total_arr = total_assets_data.values.flatten()
        total_value = total_arr[0] if total_arr.size == 1 else np.nan

        refs = series.to_series()
        if isinstance(refs.index, pd.MultiIndex):
            refs.index = refs.index.get_level_values("Reference")

        bottom = 0
        for ref in refs.index:
            val = float(refs.loc[ref])
            ax2.bar(bz_label, val, label=component_labels.get(ref, ref), bottom=bottom)
            bottom += val

        if not np.isnan(total_value):
            ax2.text(
                bz_label,
                max(bottom, total_value),
                f"Total: {total_value:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        ax2.set_xlabel("Total Assets Category")
        ax2.legend()

    ax1.grid(True, alpha=0.3)
    ax2.grid(True, alpha=0.3)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


def plot_liability_summary_static(statement, period="all"):
    """Static summary plots for Liabilities (components + total breakdown)."""

    years_dt = statement.years
    years_str = statement.years.strftime("%Y-%m-%d").to_list()

    if period != "all":
        period_dt = pd.Timestamp(period)
        if period_dt not in years_dt:
            raise ValueError(f"Period {period} not found. Available: {years_str}")
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [period_dt.strftime("%Y-%m-%d")]
        title_period = period_dt.strftime("%Y-%m-%d")
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    liability_data = statement.liability

    df_ref, dp_ref, dt_ref = "DF", "DP", "DT"
    dz_ref = "DZ"
    component_refs = [df_ref, dp_ref, dt_ref]
    component_labels = {
        ref: get_account_label(statement, "liabilities", ref) for ref in component_refs
    }
    dz_label = get_account_label(statement, "liabilities", dz_ref)

    component_data = liability_data.sel(
        compte=pd.IndexSlice[:, component_refs], annee=years_to_plot_dt
    )
    total_liab_data = liability_data.sel(
        compte=pd.IndexSlice[:, dz_ref], annee=years_to_plot_dt
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(f"Liability Summary Analysis ({title_period})", fontsize=16)

    # Plot 1: Key components
    ax1.set_title("Key Liability/Equity Components")
    ax1.set_ylabel("Value")

    if period == "all":
        x = np.arange(len(years_to_plot_str))
        width = 0.8 / len(component_refs)
        for idx, ref in enumerate(component_refs):
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)
            ax1.bar(
                x + idx * width,
                series.values,
                width,
                label=component_labels[ref],
            )
        ax1.set_xlabel("Year")
        ax1.set_xticks(x + width * (len(component_refs) - 1) / 2)
        ax1.set_xticklabels(years_to_plot_str, rotation=45, ha="right")
        ax1.legend(title="Components")
    else:
        series = component_data.squeeze(drop=True)
        labels = [
            component_labels[ref]
            for ref in series["compte"].to_index().get_level_values(1)
        ]
        ax1.bar(labels, series.values)
        ax1.set_xlabel("Liability/Equity Category")
        ax1.tick_params(axis="x", rotation=45)

    # Plot 2: Stacked total breakdown
    ax2.set_title("Total Liabilities & Equity Breakdown")
    ax2.set_ylabel("Value")

    if period == "all":
        bottom = np.zeros(len(years_to_plot_str))
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)
            ax2.bar(
                years_to_plot_str,
                series.values,
                label=component_labels[ref],
                bottom=bottom,
            )
            bottom += series.values
        total_series = total_liab_data.squeeze(drop=True)
        ax2.plot(
            years_to_plot_str,
            total_series.values,
            label=f"{dz_label} (Actual Total)",
            marker="o",
            linestyle="--",
            color="black",
        )
        ax2.set_xlabel("Year")
        ax2.tick_params(axis="x", rotation=45)
        ax2.legend()
    else:
        series = component_data.squeeze(drop=True)
        total_arr = total_liab_data.values.flatten()
        total_value = total_arr[0] if total_arr.size == 1 else np.nan

        refs = series.to_series()
        if isinstance(refs.index, pd.MultiIndex):
            refs.index = refs.index.get_level_values("Reference")

        bottom = 0
        for ref in refs.index:
            val = float(refs.loc[ref])
            ax2.bar(dz_label, val, label=component_labels.get(ref, ref), bottom=bottom)
            bottom += val

        if not np.isnan(total_value):
            ax2.text(
                dz_label,
                max(bottom, total_value),
                f"Total: {total_value:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        ax2.set_xlabel("Total Liabilities & Equity Category")
        ax2.legend()

    ax1.grid(True, alpha=0.3)
    ax2.grid(True, alpha=0.3)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()
