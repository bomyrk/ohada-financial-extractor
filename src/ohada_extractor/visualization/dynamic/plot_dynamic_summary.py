"""
Dynamic (plotly) summary plots for Assets and Liabilities.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils import get_account_label


def plot_asset_summary_dynamic(statement, period="all"):
    """Dynamic summary plots for Assets with clean labels and centered title."""

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

    # --- Compute % of total ---
    total_vals = total_assets_data.squeeze(drop=True).values
    pct_data = {
        ref: (
            component_data.sel(compte=pd.IndexSlice[:, ref])
            .squeeze(drop=True)
            .values
            / total_vals
            * 100
        )
        for ref in component_refs
    }

    # --- Figure ---
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            f"Key Asset Components ({title_period})",
            f"Total Assets Breakdown ({title_period})",
        ),
    )

    # ============================================================
    #  SUBPLOT 1 — GROUPED BARS WITH VALUE LABELS ABOVE
    # ============================================================

    if period == "all":
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)

            fig.add_trace(
                go.Bar(
                    name=component_labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    text=[f"{v:,.0f}" for v in series.values],
                    textposition="outside",
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
                text=[f"{v:,.0f}" for v in series.values],
                textposition="outside",
                legendgroup="components",
                offsetgroup="single",
            ),
            row=1,
            col=1,
        )
        fig.update_xaxes(title_text="Asset Category", row=1, col=1)

    # ============================================================
    #  SUBPLOT 2 — STACKED BARS WITH % LABELS ABOVE
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
                    textposition="outside",
                    legendgroup="stack",
                    offsetgroup="stack",
                ),
                row=1,
                col=2,
            )

        # Total line removed (cleaner)

        fig.update_xaxes(title_text="Year", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2)

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
                    textposition="outside",
                    legendgroup="stack",
                    offsetgroup="stack",
                ),
                row=1,
                col=2,
            )

        fig.update_xaxes(title_text="Total Assets Category", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2)

    # ============================================================
    #  FINAL LAYOUT — CENTER TITLE
    # ============================================================

    fig.update_layout(
        title={
            "text": f"Asset Summary Analysis ({title_period})",
            "x": 0.5,
            "xanchor": "center",
        },
        height=650,
        width=1300,
        template="plotly_white",
        hovermode="x unified",
        barmode="stack",
    )

    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.show()




def plot_liability_summary_dynamic(statement, period="all"):
    """Dynamic summary plots for Liabilities with clean labels and centered title."""

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

    # --- Compute % of total ---
    total_vals = total_liab_data.squeeze(drop=True).values
    pct_data = {
        ref: (
            component_data.sel(compte=pd.IndexSlice[:, ref])
            .squeeze(drop=True)
            .values
            / total_vals
            * 100
        )
        for ref in component_refs
    }

    # --- Figure ---
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            f"Key Liability/Equity Components ({title_period})",
            f"Total Liabilities & Equity Breakdown ({title_period})",
        ),
    )

    # ============================================================
    #  SUBPLOT 1 — GROUPED BARS WITH VALUE LABELS ABOVE
    # ============================================================

    if period == "all":
        for ref in component_refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)

            fig.add_trace(
                go.Bar(
                    name=component_labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    text=[f"{v:,.0f}" for v in series.values],
                    textposition="outside",
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
                text=[f"{v:,.0f}" for v in series.values],
                textposition="outside",
                legendgroup="components",
                offsetgroup="single",
            ),
            row=1,
            col=1,
        )
        fig.update_xaxes(title_text="Liability/Equity Category", row=1, col=1)

    # ============================================================
    #  SUBPLOT 2 — STACKED BARS WITH % LABELS ABOVE
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
                    textposition="outside",
                    legendgroup="stack",
                    offsetgroup="stack",
                ),
                row=1,
                col=2,
            )

        fig.update_xaxes(title_text="Year", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2)

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
                    textposition="outside",
                    legendgroup="stack",
                    offsetgroup="stack",
                ),
                row=1,
                col=2,
            )

        fig.update_xaxes(title_text="Total Liabilities & Equity Category", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=1, col=2)

    # ============================================================
    #  FINAL LAYOUT — CENTER TITLE
    # ============================================================

    fig.update_layout(
        title={
            "text": f"Liability Summary Analysis ({title_period})",
            "x": 0.5,
            "xanchor": "center",
        },
        height=650,
        width=1300,
        template="plotly_white",
        hovermode="x unified",
        barmode="stack",
    )

    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.show()

def plot_income_summary_dynamic(statement, period="all"):
    """Dynamic summary plots for Income with grouped bars + waterfall."""

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
    income_data = statement.income

    refs = ["XE", "XF", "XH", "RS", "XI"]
    labels = {ref: get_account_label(statement, "income", ref) for ref in refs}

    component_data = income_data.sel(
        compte=pd.IndexSlice[:, refs], annee=years_to_plot_dt
    )

    # --- Figure ---
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            f"Income Components ({title_period})",
            f"Income Waterfall ({title_period})",
        ),
    )

    # ============================================================
    #  SUBPLOT 1 — GROUPED BARS WITH VALUE LABELS
    # ============================================================

    if period == "all":
        for ref in refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)

            fig.add_trace(
                go.Bar(
                    name=labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    text=[f"{v:,.0f}" for v in series.values],
                    textposition="outside",
                    offsetgroup=ref,
                    legendgroup="income",
                ),
                row=1,
                col=1,
            )

        fig.update_xaxes(title_text="Year", row=1, col=1)

    else:
        series = component_data.squeeze(drop=True)
        fig.add_trace(
            go.Bar(
                name="Income Components",
                x=[labels[ref] for ref in refs],
                y=series.values,
                text=[f"{v:,.0f}" for v in series.values],
                textposition="outside",
            ),
            row=1,
            col=1,
        )
        fig.update_xaxes(title_text="Income Categories", row=1, col=1)

    # ============================================================
    #  SUBPLOT 2 — WATERFALL CHART
    # ============================================================

    if period == "all":
        # One waterfall per year
        for i, year in enumerate(years_to_plot_dt):
            year_data = component_data.sel(annee=year).squeeze(drop=True).values

            fig.add_trace(
                go.Waterfall(
                    name=str(year.year),
                    x=[labels[ref] for ref in refs],
                    y=year_data,
                    measure=["relative", "relative", "relative", "relative", "total"],
                    connector={"line": {"color": "gray"}},
                ),
                row=1,
                col=2,
            )

        fig.update_xaxes(title_text="Income Flow", row=1, col=2)

    else:
        year_data = component_data.squeeze(drop=True).values

        fig.add_trace(
            go.Waterfall(
                name=str(period_dt.year),
                x=[labels[ref] for ref in refs],
                y=year_data,
                measure=["relative", "relative", "relative", "relative", "total"],
                connector={"line": {"color": "gray"}},
            ),
            row=1,
            col=2,
        )

        fig.update_xaxes(title_text="Income Flow", row=1, col=2)

    # ============================================================
    #  FINAL LAYOUT — CENTER TITLE
    # ============================================================

    fig.update_layout(
        title={
            "text": f"Income Summary Analysis ({title_period})",
            "x": 0.5,
            "xanchor": "center",
        },
        height=650,
        width=1300,
        template="plotly_white",
        hovermode="x unified",
    )

    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.update_yaxes(title_text="Value", row=1, col=2)

    fig.show()

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils import get_account_label


def plot_cashflow_summary_dynamic(statement, period="all"):
    """Dynamic summary plots for Cashflow with grouped bars + waterfall."""

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
    cash_data = statement.cashflow

    refs = ["ZB", "ZC", "ZF", "ZG"]
    labels = {ref: get_account_label(statement, "cashflow", ref) for ref in refs}

    component_data = cash_data.sel(
        compte=pd.IndexSlice[:, refs], annee=years_to_plot_dt
    )

    # --- Figure ---
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            f"Cashflow Components ({title_period})",
            f"Cashflow Waterfall ({title_period})",
        ),
    )

    # ============================================================
    #  SUBPLOT 1 — GROUPED BARS WITH VALUE LABELS
    # ============================================================

    if period == "all":
        for ref in refs:
            series = component_data.sel(compte=pd.IndexSlice[:, ref]).squeeze(drop=True)

            fig.add_trace(
                go.Bar(
                    name=labels[ref],
                    x=years_to_plot_str,
                    y=series.values,
                    text=[f"{v:,.0f}" for v in series.values],
                    textposition="outside",
                    offsetgroup=ref,
                    legendgroup="cashflow",
                ),
                row=1,
                col=1,
            )

        fig.update_xaxes(title_text="Year", row=1, col=1)

    else:
        series = component_data.squeeze(drop=True)
        fig.add_trace(
            go.Bar(
                name="Cashflow Components",
                x=[labels[ref] for ref in refs],
                y=series.values,
                text=[f"{v:,.0f}" for v in series.values],
                textposition="outside",
            ),
            row=1,
            col=1,
        )
        fig.update_xaxes(title_text="Cashflow Categories", row=1, col=1)

    # ============================================================
    #  SUBPLOT 2 — WATERFALL CHART
    # ============================================================

    if period == "all":
        for year in years_to_plot_dt:
            year_data = component_data.sel(annee=year).squeeze(drop=True).values

            fig.add_trace(
                go.Waterfall(
                    name=str(year.year),
                    x=[labels[ref] for ref in refs],
                    y=year_data,
                    measure=["relative", "relative", "relative", "total"],
                    connector={"line": {"color": "gray"}},
                ),
                row=1,
                col=2,
            )

        fig.update_xaxes(title_text="Cashflow Flow", row=1, col=2)

    else:
        year_data = component_data.squeeze(drop=True).values

        fig.add_trace(
            go.Waterfall(
                name=str(period_dt.year),
                x=[labels[ref] for ref in refs],
                y=year_data,
                measure=["relative", "relative", "relative", "total"],
                connector={"line": {"color": "gray"}},
            ),
            row=1,
            col=2,
        )

        fig.update_xaxes(title_text="Cashflow Flow", row=1, col=2)

    # ============================================================
    #  FINAL LAYOUT — CENTER TITLE
    # ============================================================

    fig.update_layout(
        title={
            "text": f"Cashflow Summary Analysis ({title_period})",
            "x": 0.5,
            "xanchor": "center",
        },
        height=650,
        width=1300,
        template="plotly_white",
        hovermode="x unified",
    )

    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.update_yaxes(title_text="Value", row=1, col=2)

    fig.show()
