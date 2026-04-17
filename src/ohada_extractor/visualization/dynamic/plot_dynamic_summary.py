"""
Dynamic (plotly) summary plots for Assets and Liabilities.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils import get_account_label


# ============================================================
#  ASSET SUMMARY (DYNAMIC)
# ============================================================

def plot_asset_summary_dynamic(statement, period="all"):
    """Dynamic summary plots for Assets with % labels + growth lines."""

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    # --- Period selection ---
    if period != "all":
        period_dt = pd.Timestamp(period)
        if period_dt not in years_dt:
            raise ValueError(f"Period {period} not found. Available: {years_str}")
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [str(period_dt.year)]
        title_period = str(period_dt.year)
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    # --- Data selection ---
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

    # --- Compute percentages ---
    total_vals = total_assets_data.squeeze(drop=True).values
    pct_data = {
        ref: (component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True).values / total_vals * 100)
        for ref in component_refs
    }

    # --- Compute growth rates ---
    growth_data = {}
    if len(years_to_plot_dt) > 1:
        for ref in component_refs:
            vals = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True).values
            growth = np.concatenate([[np.nan], (vals[1:] - vals[:-1]) / vals[:-1] * 100])
            growth_data[ref] = growth

    # --- Figure ---
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"secondary_y": False}, {"secondary_y": True}]],
        subplot_titles=(
            f"Key Asset Components ({title_period})",
            f"Total Assets Breakdown ({title_period})",
        ),
    )

    # ============================================================
    #  SUBPLOT 1 — GROUPED BARS
    # ============================================================

    if period == "all":
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)

            fig.add_trace(
                go.Bar(
                    name=component_labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    legendgroup="components",
                    offsetgroup=ref,
                ),
                row=1,
                col=1,
            )

        fig.update_xaxes(title_text="Year", row=1, col=1)

    else:
        series = component_data.squeeze(drop=True)
        labels = [
            component_labels[ref]
            for ref in series["compte"].to_index().get_level_values(1)
        ]

        fig.add_trace(
            go.Bar(
                name="Value",
                x=labels,
                y=series.values,
                legendgroup="components",
                offsetgroup="single",
            ),
            row=1,
            col=1,
        )
        fig.update_xaxes(title_text="Asset Category", row=1, col=1)

    # ============================================================
    #  SUBPLOT 2 — STACKED BARS + % LABELS + TOTAL LINE + GROWTH LINES
    # ============================================================

    if period == "all":
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)

            fig.add_trace(
                go.Bar(
                    name=component_labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    text=[f"{v:.1f}%" for v in pct_data[ref]],
                    textposition="inside",
                    legendgroup="stack",
                    offsetgroup="stack",
                ),
                row=1,
                col=2,
            )

        # Total line
        total_series = total_assets_data.squeeze(drop=True)
        fig.add_trace(
            go.Scatter(
                name=f"{bz_label} (Total)",
                x=years_to_plot_str,
                y=total_series.values,
                mode="lines+markers",
                line=dict(color="black", width=2, dash="dot"),
                legendgroup="stack",
            ),
            row=1,
            col=2,
            secondary_y=False,
        )

        # Growth lines (secondary axis)
        for ref in component_refs:
            fig.add_trace(
                go.Scatter(
                    name=f"{component_labels[ref]} Growth (%)",
                    x=years_to_plot_str,
                    y=growth_data[ref],
                    mode="lines+markers",
                    line=dict(width=2),
                    legendgroup="growth",
                ),
                row=1,
                col=2,
                secondary_y=True,
            )

        fig.update_xaxes(title_text="Year", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2, secondary_y=False)
        fig.update_yaxes(title_text="Growth (%)", row=1, col=2, secondary_y=True)

    else:
        # Single period stacked bar
        series = component_data.squeeze(drop=True)
        total_arr = total_assets_data.values.flatten()
        total_value = total_arr[0] if total_arr.size == 1 else np.nan

        refs = series.to_series()
        if isinstance(refs.index, pd.MultiIndex):
            refs.index = refs.index.get_level_values("Reference")

        for ref in refs.index:
            val = float(refs.loc[ref])
            pct = val / total_value * 100

            fig.add_trace(
                go.Bar(
                    name=component_labels.get(ref, ref),
                    x=[bz_label],
                    y=[val],
                    text=[f"{pct:.1f}%"],
                    textposition="inside",
                    legendgroup="stack",
                    offsetgroup="stack",
                ),
                row=1,
                col=2,
            )

        if not np.isnan(total_value):
            fig.add_annotation(
                x=bz_label,
                y=total_value,
                text=f"Total: {total_value:,.0f}",
                showarrow=True,
                arrowhead=4,
                ax=0,
                ay=-40,
                row=1,
                col=2,
            )

        fig.update_xaxes(title_text="Total Assets Category", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2)

    # ============================================================
    #  FINAL LAYOUT
    # ============================================================

    fig.update_layout(
        title_text=f"Asset Summary Analysis ({title_period})",
        height=650,
        width=1300,
        template="plotly_white",
        hovermode="x unified",
        barmode="stack",
    )

    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.show()



# ============================================================
#  LIABILITY SUMMARY (DYNAMIC)
# ============================================================

def plot_liability_summary_dynamic(statement, period="all"):
    """Dynamic summary plots for Liabilities with % labels + growth lines."""

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    # --- Period selection ---
    if period != "all":
        period_dt = pd.Timestamp(period)
        if period_dt not in years_dt:
            raise ValueError(f"Period {period} not found. Available: {years_str}")
        years_to_plot_dt = [period_dt]
        years_to_plot_str = [str(period_dt.year)]
        title_period = str(period_dt.year)
    else:
        years_to_plot_dt = years_dt
        years_to_plot_str = years_str
        title_period = "All Periods"

    # --- Data selection ---
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

    # --- Compute percentages ---
    total_vals = total_liab_data.squeeze(drop=True).values
    pct_data = {
        ref: (component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True).values / total_vals * 100)
        for ref in component_refs
    }

    # --- Compute growth rates ---
    growth_data = {}
    if len(years_to_plot_dt) > 1:
        for ref in component_refs:
            vals = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True).values
            growth = np.concatenate([[np.nan], (vals[1:] - vals[:-1]) / vals[:-1] * 100])
            growth_data[ref] = growth

    # --- Figure ---
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"secondary_y": False}, {"secondary_y": True}]],
        subplot_titles=(
            f"Key Liability/Equity Components ({title_period})",
            f"Total Liabilities & Equity Breakdown ({title_period})",
        ),
    )

    # ============================================================
    #  SUBPLOT 1 — GROUPED BARS
    # ============================================================

    if period == "all":
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)

            fig.add_trace(
                go.Bar(
                    name=component_labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    legendgroup="components",
                    offsetgroup=ref,
                ),
                row=1,
                col=1,
            )

        fig.update_xaxes(title_text="Year", row=1, col=1)

    else:
        series = component_data.squeeze(drop=True)
        labels = [
            component_labels[ref]
            for ref in series["compte"].to_index().get_level_values(1)
        ]

        fig.add_trace(
            go.Bar(
                name="Value",
                x=labels,
                y=series.values,
                legendgroup="components",
                offsetgroup="single",
            ),
            row=1,
            col=1,
        )
        fig.update_xaxes(title_text="Liability/Equity Category", row=1, col=1)

    # ============================================================
    #  SUBPLOT 2 — STACKED BARS + % LABELS + TOTAL LINE + GROWTH LINES
    # ============================================================

    if period == "all":
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)

            fig.add_trace(
                go.Bar(
                    name=component_labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    text=[f"{v:.1f}%" for v in pct_data[ref]],
                    textposition="inside",
                    legendgroup="stack",
                    offsetgroup="stack",
                ),
                row=1,
                col=2,
            )

        # Total line
        total_series = total_liab_data.squeeze(drop=True)
        fig.add_trace(
            go.Scatter(
                name=f"{dz_label} (Total)",
                x=years_to_plot_str,
                y=total_series.values,
                mode="lines+markers",
                line=dict(color="black", width=2, dash="dot"),
                legendgroup="stack",
            ),
            row=1,
            col=2,
            secondary_y=False,
        )

        # Growth lines (secondary axis)
        for ref in component_refs:
            fig.add_trace(
                go.Scatter(
                    name=f"{component_labels[ref]} Growth (%)",
                    x=years_to_plot_str,
                    y=growth_data[ref],
                    mode="lines+markers",
                    line=dict(width=2),
                    legendgroup="growth",
                ),
                row=1,
                col=2,
                secondary_y=True,
            )

        fig.update_xaxes(title_text="Year", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2, secondary_y=False)
        fig.update_yaxes(title_text="Growth (%)", row=1, col=2, secondary_y=True)

    else:
        # Single period stacked bar
        series = component_data.squeeze(drop=True)
        total_arr = total_liab_data.values.flatten()
        total_value = total_arr[0] if total_arr.size == 1 else np.nan

        refs = series.to_series()
        if isinstance(refs.index, pd.MultiIndex):
            refs.index = refs.index.get_level_values("Reference")

        for ref in refs.index:
            val = float(refs.loc[ref])
            pct = val / total_value * 100

            fig.add_trace(
                go.Bar(
                    name=component_labels.get(ref, ref),
                    x=[dz_label],
                    y=[val],
                    text=[f"{pct:.1f}%"],
                    textposition="inside",
                    legendgroup="stack",
                    offsetgroup="stack",
                ),
                row=1,
                col=2,
            )

        if not np.isnan(total_value):
            fig.add_annotation(
                x=dz_label,
                y=total_value,
                text=f"Total: {total_value:,.0f}",
                showarrow=True,
                arrowhead=4,
                ax=0,
                ay=-40,
                row=1,
                col=2,
            )

        fig.update_xaxes(title_text="Total Liabilities & Equity Category", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2)

    # ============================================================
    #  FINAL LAYOUT
    # ============================================================

    fig.update_layout(
        title_text=f"Liability Summary Analysis ({title_period})",
        height=650,
        width=1300,
        template="plotly_white",
        hovermode="x unified",
        barmode="stack",
    )

    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.show()