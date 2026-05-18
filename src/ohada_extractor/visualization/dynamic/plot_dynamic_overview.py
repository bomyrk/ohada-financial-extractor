import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils import get_account_label


def plot_overview_dashboard_clean(statement):
    """Clean 4‑Panel OHADA Overview Dashboard:

    - Assets (grouped + stacked)
    - Liabilities (grouped + stacked)
    - Income (grouped + waterfall)
    - Cashflow (grouped + waterfall)
    """

    # Use statement.years as the canonical time axis
    years_dt = statement.years
    years_str = years_dt.strftime("%Y")

    fig = make_subplots(
        rows=4,
        cols=2,
        subplot_titles=[
            "Assets – Grouped",
            "Assets – Stacked",
            "Liabilities – Grouped",
            "Liabilities – Stacked",
            "Income – Grouped",
            "Income – Waterfall",
            "Cashflow – Grouped",
            "Cashflow – Waterfall",
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

    asset_components = asset_data.sel(
        compte=pd.IndexSlice[:, asset_refs],
        annee=years_dt,
    )

    asset_total_data = asset_data.sel(
        compte=pd.IndexSlice[:, asset_total],
        annee=years_dt,
    ).values.flatten()

    asset_labels = {
        ref: get_account_label(statement, "assets", ref) for ref in asset_refs
    }

    # Grouped bars (left)
    for ref in asset_refs:
        series_vals = asset_components.sel(
            compte=pd.IndexSlice[:, ref]
        ).values.flatten()
        fig.add_trace(
            go.Bar(
                name=asset_labels[ref],
                x=years_str,
                y=series_vals,
                text=[f"{v:,.0f}" for v in series_vals],
                textposition="outside",
                offsetgroup=ref,
            ),
            row=1,
            col=1,
        )

    # Stacked bars (right)
    for ref in asset_refs:
        series_vals = asset_components.sel(
            compte=pd.IndexSlice[:, ref]
        ).values.flatten()

        # Safe division
        pct = np.zeros_like(series_vals, dtype=float)
        mask = asset_total_data != 0
        pct[mask] = series_vals[mask] / asset_total_data[mask] * 100

        fig.add_trace(
            go.Bar(
                name=asset_labels[ref],
                x=years_str,
                y=series_vals,
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
    ).values.flatten()

    liab_labels = {
        ref: get_account_label(statement, "liabilities", ref) for ref in liab_refs
    }

    # Grouped bars (left)
    for ref in liab_refs:
        series_vals = liab_components.sel(compte=pd.IndexSlice[:, ref]).values.flatten()
        fig.add_trace(
            go.Bar(
                name=liab_labels[ref],
                x=years_str,
                y=series_vals,
                text=[f"{v:,.0f}" for v in series_vals],
                textposition="outside",
                offsetgroup=ref,
            ),
            row=2,
            col=1,
        )

    # Stacked bars (right)
    for ref in liab_refs:
        series_vals = liab_components.sel(compte=pd.IndexSlice[:, ref]).values.flatten()

        # Safe division
        pct = np.zeros_like(series_vals, dtype=float)
        mask = liab_total_data != 0
        pct[mask] = series_vals[mask] / liab_total_data[mask] * 100

        fig.add_trace(
            go.Bar(
                name=liab_labels[ref],
                x=years_str,
                y=series_vals,
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

    income_labels = {
        ref: get_account_label(statement, "income", ref) for ref in income_refs
    }

    # Grouped bars (left)
    for ref in income_refs:
        series_vals = income_components.sel(
            compte=pd.IndexSlice[:, ref]
        ).values.flatten()
        fig.add_trace(
            go.Bar(
                name=income_labels[ref],
                x=years_str,
                y=series_vals,
                text=[f"{v:,.0f}" for v in series_vals],
                textposition="outside",
                offsetgroup=ref,
            ),
            row=3,
            col=1,
        )

    # Waterfall (right)
    for year in income_components.annee.values:
        # Sécurisation de l'alignement et de l'ordre des références
        year_vals = [
            float(
                income_components.sel(
                    compte=pd.IndexSlice[:, ref], annee=year
                ).values.item()
            )
            for ref in income_refs
        ]

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

    cash_labels = {
        ref: get_account_label(statement, "cashflow", ref) for ref in cash_refs
    }

    # Grouped bars (left)
    for ref in cash_refs:
        series_vals = cash_components.sel(compte=pd.IndexSlice[:, ref]).values.flatten()
        fig.add_trace(
            go.Bar(
                name=cash_labels[ref],
                x=years_str,
                y=series_vals,
                text=[f"{v:,.0f}" for v in series_vals],
                textposition="outside",
                offsetgroup=ref,
            ),
            row=4,
            col=1,
        )

    # Waterfall (right)
    for year in cash_components.annee.values:
        # Sécurisation de l'alignement et de l'ordre des références
        year_vals = [
            float(
                cash_components.sel(
                    compte=pd.IndexSlice[:, ref], annee=year
                ).values.item()
            )
            for ref in cash_refs
        ]

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
        showlegend=False,  # ← REMOVE LEGEND
        margin=dict(t=80, b=40),
    )

    fig.show()
