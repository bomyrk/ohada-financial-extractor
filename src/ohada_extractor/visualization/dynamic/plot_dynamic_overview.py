import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils import get_account_label


def plot_overview_dashboard_clean(statement):
    """
    Clean 4‑Panel OHADA Overview Dashboard:
    - Assets (grouped + stacked)
    - Liabilities (grouped + stacked)
    - Income (grouped + waterfall)
    - Cashflow (grouped + waterfall)
    """

    # Use statement.years as the canonical time axis
    years_dt = statement.years
    years_str = years_dt.year.astype(str).to_list()

    fig = make_subplots(
        rows=4,
        cols=2,
        subplot_titles=[
            "Assets – Grouped", "Assets – Stacked",
            "Liabilities – Grouped", "Liabilities – Stacked",
            "Income – Grouped", "Income – Waterfall",
            "Cashflow – Grouped", "Cashflow – Waterfall",
        ],
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
        ],
        horizontal_spacing=0.08,
        vertical_spacing=0.05,
    )

    # ============================================================
    # 1) ASSETS (AZ, BK, BT, BZ)
    # ============================================================

    asset_refs = ["AZ", "BK", "BT"]
    asset_total = "BZ"

    asset_data = statement.asset.sel(valeur="Net")

    # Select using the original years_dt (whatever type annee uses)
    asset_components = asset_data.sel(
        compte=pd.IndexSlice[:, asset_refs],
        annee=years_dt,
    )

    asset_total_data = asset_data.sel(
        compte=pd.IndexSlice[:, asset_total],
        annee=years_dt,
    ).squeeze()

    asset_labels = {ref: get_account_label(statement, "assets", ref) for ref in asset_refs}

    # Remove zero-only components
    asset_labels = {ref: asset_labels[ref] for ref in asset_refs}

    # Grouped bars (left)
    for ref in asset_refs:
        series = asset_components.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        fig.add_trace(
            go.Bar(
                name=asset_labels[ref],
                x=years_str,
                y=series.values,
                text=[f"{v:,.0f}" for v in series.values],
                textposition="outside",
                offsetgroup=ref,
            ),
            row=1,
            col=1,
        )

    # Stacked bars (right)
    for ref in asset_refs:
        series = asset_components.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        pct = series.values / asset_total_data.values * 100
        fig.add_trace(
            go.Bar(
                name=asset_labels[ref],
                x=years_str,
                y=series.values,
                text=[f"{p:.1f}%" for p in pct],
                textposition="outside",
                offsetgroup="stack",
            ),
            row=1,
            col=2,
        )

    # ============================================================
    # 2) LIABILITIES (DF, DP, DT, DZ)
    # ============================================================

    liab_refs = ["DF", "DP", "DT"]
    liab_total = "DZ"

    liab_data = statement.liability

    liab_components = liab_data.sel(
        compte=pd.IndexSlice[:, liab_refs],
        annee=years_dt,
    )

    liab_total_data = liab_data.sel(
        compte=pd.IndexSlice[:, liab_total],
        annee=years_dt,
    ).squeeze()

    liab_labels = {ref: get_account_label(statement, "liabilities", ref) for ref in liab_refs}

    # Remove zero-only components
    liab_labels = {ref: liab_labels[ref] for ref in liab_refs}

    # Grouped bars (left)
    for ref in liab_refs:
        series = liab_components.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        fig.add_trace(
            go.Bar(
                name=liab_labels[ref],
                x=years_str,
                y=series.values,
                text=[f"{v:,.0f}" for v in series.values],
                textposition="outside",
                offsetgroup=ref,
            ),
            row=2,
            col=1,
        )

    # Stacked bars (right)
    for ref in liab_refs:
        series = liab_components.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        pct = series.values / liab_total_data.values * 100
        fig.add_trace(
            go.Bar(
                name=liab_labels[ref],
                x=years_str,
                y=series.values,
                text=[f"{p:.1f}%" for p in pct],
                textposition="outside",
                offsetgroup="stack",
            ),
            row=2,
            col=2,
        )

    # ============================================================
    # 3) INCOME (XE, XF, XH, RS, XI)
    # ============================================================

    income_refs = ["XE", "XF", "XH", "RS", "XI"]
    income_data = statement.income

    income_components = income_data.sel(
        compte=pd.IndexSlice[:, income_refs],
        annee=years_dt,
    )

    income_labels = {ref: get_account_label(statement, "income", ref) for ref in income_refs}

    # Remove zero-only components

    income_labels = {ref: income_labels[ref] for ref in income_refs}

    # Grouped bars (left)
    for ref in income_refs:
        series = income_components.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        fig.add_trace(
            go.Bar(
                name=income_labels[ref],
                x=years_str,
                y=series.values,
                text=[f"{v:,.0f}" for v in series.values],
                textposition="outside",
                offsetgroup=ref,
            ),
            row=3,
            col=1,
        )

    # Waterfall (right)
    for year in income_components.annee.values:
        year_vals = income_components.sel(annee=year).squeeze().values
        fig.add_trace(
            go.Waterfall(
                name=str(pd.to_datetime(year).year),
                x=[income_labels[r] for r in income_refs],
                y=year_vals,
                measure=["relative"] * (len(income_refs) - 1) + ["total"],
                connector={"line": {"color": "gray"}},
            ),
            row=3,
            col=2,
        )

    # ============================================================
    # 4) CASHFLOW (ZB, ZC, ZF, ZG)
    # ============================================================

    cash_refs = ["ZB", "ZC", "ZF", "ZG"]
    cash_data = statement.cashflow

    cash_components = cash_data.sel(
        compte=pd.IndexSlice[:, cash_refs],
        annee=years_dt,
    )

    cash_labels = {ref: get_account_label(statement, "cashflow", ref) for ref in cash_refs}

    # Remove zero-only components

    cash_labels = {ref: cash_labels[ref] for ref in cash_refs}

    # Grouped bars (left)
    for ref in cash_refs:
        series = cash_components.sel(compte=pd.IndexSlice[:, ref]).squeeze()
        fig.add_trace(
            go.Bar(
                name=cash_labels[ref],
                x=years_str,
                y=series.values,
                text=[f"{v:,.0f}" for v in series.values],
                textposition="outside",
                offsetgroup=ref,
            ),
            row=4,
            col=1,
        )

    # Waterfall (right)
    for year in cash_components.annee.values:
        year_vals = cash_components.sel(annee=year).squeeze().values
        fig.add_trace(
            go.Waterfall(
                name=str(pd.to_datetime(year).year),
                x=[cash_labels[r] for r in cash_refs],
                y=year_vals,
                measure=["relative"] * (len(cash_refs) - 1) + ["total"],
                connector={"line": {"color": "gray"}},
            ),
            row=4,
            col=2,
        )

    # ============================================================
    # FINAL LAYOUT
    # ============================================================

    fig.update_layout(
        title={
            "text": "OHADA 4‑Panel Overview Dashboard (Clean Version)",
            "x": 0.5,
            "xanchor": "center",
        },
        height=1800,
        width=1300,
        template="plotly_white",
        hovermode="x unified",
        barmode="stack",
        showlegend=False,   # ← REMOVE LEGEND
        margin=dict(t=80, b=40)
    )

    fig.show()
