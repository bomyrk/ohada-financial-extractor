"""
Dynamic (plotly) summary plots for Assets and Liabilities.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils import (
    get_account_label,
)


def plot_asset_summary_dynamic(statement, period="all"):
    """Dynamic summary plots for Assets (components + total breakdown)."""

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

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            f"Key Asset Components ({title_period})",
            f"Total Assets Breakdown ({title_period})",
        ),
    )

    # Plot 1: components
    if period == "all":
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)
            fig.add_trace(
                go.Bar(
                    name=component_labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    legendgroup="components",
                ),
                row=1,
                col=1,
            )
        fig.update_layout(barmode="group")
        fig.update_xaxes(title_text="Year", row=1, col=1)
    else:
        series = component_data.squeeze(drop=True)
        labels = [
            component_labels[ref]
            for ref in series["compte"].to_index().get_level_values(1)
        ]
        fig.add_trace(
            go.Bar(name="Value", x=labels, y=series.values, showlegend=False),
            row=1,
            col=1,
        )
        fig.update_xaxes(title_text="Asset Category", row=1, col=1)

    # Plot 2: stacked breakdown
    if period == "all":
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)
            fig.add_trace(
                go.Bar(
                    name=component_labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    legendgroup="stack",
                ),
                row=1,
                col=2,
            )
        total_series = total_assets_data.squeeze(drop=True)
        fig.add_trace(
            go.Scatter(
                name=f"{bz_label} (Actual Total)",
                x=years_to_plot_str,
                y=total_series.values,
                mode="lines+markers",
                line=dict(color="rgba(0,0,0,0.7)", width=2, dash="dot"),
                legendgroup="stack",
            ),
            row=1,
            col=2,
        )
        fig.update_layout(barmode="stack")
        fig.update_xaxes(title_text="Year", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2)
    else:
        series = component_data.squeeze(drop=True)
        total_arr = total_assets_data.values.flatten()
        total_value = total_arr[0] if total_arr.size == 1 else np.nan

        refs = series.to_series()
        if isinstance(refs.index, pd.MultiIndex):
            refs.index = refs.index.get_level_values("Reference")

        stack_refs, stack_values, stack_labels = [], [], []
        for ref in refs.index:
            stack_refs.append(ref)
            stack_values.append(float(refs.loc[ref]))
            stack_labels.append(component_labels.get(ref, ref))

        for i, ref in enumerate(stack_refs):
            fig.add_trace(
                go.Bar(
                    name=stack_labels[i],
                    x=[bz_label],
                    y=[stack_values[i]],
                    legendgroup="stack",
                    showlegend=(i == 0),
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
                font=dict(color="black"),
                align="center",
            )

        fig.update_layout(barmode="stack")
        fig.update_xaxes(title_text="Total Assets Category", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2)

    fig.update_layout(
        title_text=f"Asset Summary Analysis ({title_period})",
        height=600,
        width=1200,
        template="plotly_white",
        legend=dict(traceorder="grouped"),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.show()


def plot_liability_summary_dynamic(statement, period="all"):
    """Dynamic summary plots for Liabilities (components + total breakdown)."""

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

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            f"Key Liability/Equity Components ({title_period})",
            f"Total Liabilities & Equity Breakdown ({title_period})",
        ),
    )

    # Plot 1: components
    if period == "all":
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)
            fig.add_trace(
                go.Bar(
                    name=component_labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    legendgroup="components",
                ),
                row=1,
                col=1,
            )
        fig.update_layout(barmode="group")
        fig.update_xaxes(title_text="Year", row=1, col=1)
    else:
        series = component_data.squeeze(drop=True)
        labels = [
            component_labels[ref]
            for ref in series["compte"].to_index().get_level_values(1)
        ]
        fig.add_trace(
            go.Bar(name="Value", x=labels, y=series.values, showlegend=False),
            row=1,
            col=1,
        )
        fig.update_xaxes(title_text="Liability/Equity Category", row=1, col=1)

    # Plot 2: stacked breakdown
    if period == "all":
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)
            fig.add_trace(
                go.Bar(
                    name=component_labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    legendgroup="stack",
                ),
                row=1,
                col=2,
            )
        total_series = total_liab_data.squeeze(drop=True)
        fig.add_trace(
            go.Scatter(
                name=f"{dz_label} (Actual Total)",
                x=years_to_plot_str,
                y=total_series.values,
                mode="lines+markers",
                line=dict(color="rgba(0,0,0,0.7)", width=2, dash="dot"),
                legendgroup="stack",
            ),
            row=1,
            col=2,
        )
        fig.update_layout(barmode="stack")
        fig.update_xaxes(title_text="Year", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2)
    else:
        series = component_data.squeeze(drop=True)
        total_arr = total_liab_data.values.flatten()
        total_value = total_arr[0] if total_arr.size == 1 else np.nan

        refs = series.to_series()
        if isinstance(refs.index, pd.MultiIndex):
            refs.index = refs.index.get_level_values("Reference")

        stack_refs, stack_values, stack_labels = [], [], []
        for ref in refs.index:
            stack_refs.append(ref)
            stack_values.append(float(refs.loc[ref]))
            stack_labels.append(component_labels.get(ref, ref))

        for i, ref in enumerate(stack_refs):
            fig.add_trace(
                go.Bar(
                    name=stack_labels[i],
                    x=[dz_label],
                    y=[stack_values[i]],
                    legendgroup="stack",
                    showlegend=(i == 0),
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
                font=dict(color="black"),
                align="center",
            )

        fig.update_layout(barmode="stack")
        fig.update_xaxes(title_text="Total Liabilities & Equity Category", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2)

    fig.update_layout(
        title_text=f"Liability Summary Analysis ({title_period})",
        height=600,
        width=1200,
        template="plotly_white",
        legend=dict(traceorder="grouped"),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.show()
