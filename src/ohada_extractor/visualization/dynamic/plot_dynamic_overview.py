import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils import get_account_label


def plot_overview_dashboard_dynamic(statement):
    """
    4‑Panel OHADA Overview Dashboard:
    - Panel 1: Asset Summary (stacked + YoY growth)
    - Panel 2: Liability Summary (stacked + YoY growth)
    - Panel 3: Income Summary (stacked + YoY growth)
    - Panel 4: Cashflow Summary (stacked + YoY growth)
    """

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    # ============================================================
    # 1) DEFINE COMPONENTS FOR EACH STATEMENT
    # ============================================================

    # Assets
    asset_refs = ["AZ", "BK", "BT"]
    asset_total = "BZ"

    # Liabilities
    liab_refs = ["DF", "DP", "DT"]
    liab_total = "DZ"

    # Income
    income_refs = ["XE", "XF", "XH", "RS"]
    income_total = "XI"

    # Cashflow
    cash_refs = ["ZB", "ZC", "ZE"]
    cash_total = "ZF"

    groups = [
        ("Assets", statement.asset.sel(valeur="Net"), asset_refs, asset_total),
        ("Liabilities", statement.liability, liab_refs, liab_total),
        ("Income", statement.income, income_refs, income_total),
        ("Cashflow", statement.cashflow, cash_refs, cash_total),
    ]

    # ============================================================
    # 2) CREATE FIGURE WITH 4 PANELS
    # ============================================================

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[
            [{"secondary_y": True}, {"secondary_y": True}],
            [{"secondary_y": True}, {"secondary_y": True}],
        ],
        subplot_titles=[
            "Assets Summary",
            "Liabilities Summary",
            "Income Summary",
            "Cashflow Summary",
        ],
    )

    # ============================================================
    # 3) LOOP THROUGH EACH PANEL
    # ============================================================

    for idx, (title, data_array, refs, total_ref) in enumerate(groups, start=1):

        row = 1 if idx <= 2 else 2
        col = 1 if idx in (1, 3) else 2

        # Extract data
        component_data = data_array.sel(
            compte=pd.IndexSlice[:, refs], annee=years_dt
        )
        total_data = data_array.sel(
            compte=pd.IndexSlice[:, total_ref], annee=years_dt
        ).squeeze(drop=True)

        # Compute % of total
        pct_data = {
            ref: (
                component_data.sel(compte=pd.IndexSlice[:, ref])
                .squeeze(drop=True)
                .values
                / total_data.values
                * 100
            )
            for ref in refs
        }

        # Compute YoY growth
        growth_data = {}
        for ref in refs:
            vals = (
                component_data.sel(compte=pd.IndexSlice[:, ref])
                .squeeze(drop=True)
                .values
            )
            growth = np.concatenate([[np.nan], (vals[1:] - vals[:-1]) / vals[:-1] * 100])
            growth_data[ref] = growth

        # Labels
        labels = {
            ref: get_account_label(statement, title.lower(), ref)
            for ref in refs
        }
        total_label = get_account_label(statement, title.lower(), total_ref)

        # ============================================================
        # STACKED BARS (ABSOLUTE VALUES) + % LABELS
        # ============================================================

        for ref in refs:
            series = (
                component_data.sel(compte=pd.IndexSlice[:, ref])
                .squeeze(drop=True)
                .values
            )

            fig.add_trace(
                go.Bar(
                    name=labels[ref],
                    x=years_str,
                    y=series,
                    text=[f"{v:.1f}%" for v in pct_data[ref]],
                    textposition="inside",
                    legendgroup=f"{title}_stack",
                    offsetgroup=f"{title}_stack",
                ),
                row=row,
                col=col,
                secondary_y=False,
            )

        # ============================================================
        # TOTAL LINE
        # ============================================================

        fig.add_trace(
            go.Scatter(
                name=f"{total_label} (Total)",
                x=years_str,
                y=total_data.values,
                mode="lines+markers",
                line=dict(color="black", width=2, dash="dot"),
                legendgroup=f"{title}_total",
            ),
            row=row,
            col=col,
            secondary_y=False,
        )

        # ============================================================
        # GROWTH LINES (SECONDARY AXIS)
        # ============================================================

        for ref in refs:
            fig.add_trace(
                go.Scatter(
                    name=f"{labels[ref]} Growth (%)",
                    x=years_str,
                    y=growth_data[ref],
                    mode="lines+markers",
                    line=dict(width=2),
                    legendgroup=f"{title}_growth",
                ),
                row=row,
                col=col,
                secondary_y=True,
            )

        # Axis labels
        fig.update_xaxes(title_text="Year", row=row, col=col)
        fig.update_yaxes(title_text="Value", row=row, col=col, secondary_y=False)
        fig.update_yaxes(title_text="Growth (%)", row=row, col=col, secondary_y=True)

    # ============================================================
    # 4) FINAL LAYOUT
    # ============================================================

    fig.update_layout(
        title_text="OHADA 4‑Panel Overview Dashboard",
        height=1200,
        width=1600,
        template="plotly_white",
        hovermode="x unified",
        barmode="stack",
    )

    fig.show()
