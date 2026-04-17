import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils import get_account_label


def plot_ohada_tabs_dynamic(statement):
    """
    OHADA Dashboard with Tabs:
    - Assets
    - Liabilities
    - Income
    - Cashflow
    """

    years_dt = statement.years
    years_str = statement.years.year.astype(str).to_list()

    # ============================================================
    # 1) DEFINE COMPONENTS FOR EACH STATEMENT
    # ============================================================

    groups = [
        ("Assets", statement.asset.sel(valeur="Net"), ["AZ", "BK", "BT"], "BZ"),
        ("Liabilities", statement.liability, ["DF", "DP", "DT"], "DZ"),
        ("Income", statement.income, ["XE", "XF", "XH", "RS"], "XI"),
        ("Cashflow", statement.cashflow, ["ZB", "ZC", "ZE"], "ZF"),
    ]

    # ============================================================
    # 2) CREATE FIGURE WITH 1 PANEL (we will switch content)
    # ============================================================

    fig = make_subplots(
        rows=1,
        cols=1,
        specs=[[{"secondary_y": True}]],
        subplot_titles=["OHADA Dashboard"],
    )

    all_traces = []
    visibility_masks = []

    # ============================================================
    # 3) BUILD TRACES FOR EACH TAB
    # ============================================================

    for idx, (title, data_array, refs, total_ref) in enumerate(groups):

        component_data = data_array.sel(
            compte=pd.IndexSlice[:, refs], annee=years_dt
        )
        total_data = data_array.sel(
            compte=pd.IndexSlice[:, total_ref], annee=years_dt
        ).squeeze(drop=True)

        # % of total
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

        # YoY growth
        growth_data = {}
        for ref in refs:
            vals = (
                component_data.sel(compte=pd.IndexSlice[:, ref])
                .squeeze(drop=True)
                .values
            )
            growth = np.concatenate([[np.nan], (vals[1:] - vals[:-1]) / vals[:-1] * 100])
            growth_data[ref] = growth

        labels = {
            ref: get_account_label(statement, title.lower(), ref)
            for ref in refs
        }
        total_label = get_account_label(statement, title.lower(), total_ref)

        # Track which traces belong to this tab
        tab_trace_indices = []

        # ============================================================
        # STACKED BARS (ABSOLUTE VALUES) + % LABELS
        # ============================================================

        for ref in refs:
            series = (
                component_data.sel(compte=pd.IndexSlice[:, ref])
                .squeeze(drop=True)
                .values
            )

            trace = go.Bar(
                name=labels[ref],
                x=years_str,
                y=series,
                text=[f"{v:.1f}%" for v in pct_data[ref]],
                textposition="inside",
                legendgroup=f"{title}_stack",
                offsetgroup=f"{title}_stack",
                visible=False,
            )
            all_traces.append(trace)
            tab_trace_indices.append(len(all_traces) - 1)

        # ============================================================
        # TOTAL LINE
        # ============================================================

        trace = go.Scatter(
            name=f"{total_label} (Total)",
            x=years_str,
            y=total_data.values,
            mode="lines+markers",
            line=dict(color="black", width=2, dash="dot"),
            legendgroup=f"{title}_total",
            visible=False,
        )
        all_traces.append(trace)
        tab_trace_indices.append(len(all_traces) - 1)

        # ============================================================
        # GROWTH LINES (SECONDARY AXIS)
        # ============================================================

        for ref in refs:
            trace = go.Scatter(
                name=f"{labels[ref]} Growth (%)",
                x=years_str,
                y=growth_data[ref],
                mode="lines+markers",
                line=dict(width=2),
                legendgroup=f"{title}_growth",
                visible=False,
            )
            all_traces.append(trace)
            tab_trace_indices.append(len(all_traces) - 1)

        # Build visibility mask for this tab
        mask = [False] * len(all_traces)
        for i in tab_trace_indices:
            mask[i] = True
        visibility_masks.append(mask)

    # Add all traces to figure
    for trace in all_traces:
        fig.add_trace(trace, row=1, col=1)

    # ============================================================
    # 4) ADD TABS (BUTTONS)
    # ============================================================

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.5,
                y=1.15,
                showactive=True,
                buttons=[
                    dict(
                        label=title,
                        method="update",
                        args=[
                            {"visible": visibility_masks[i]},
                            {"title": f"{title} Summary"},
                        ],
                    )
                    for i, (title, _, _, _) in enumerate(groups)
                ],
            )
        ]
    )

    # Default tab = Assets
    for i, trace in enumerate(all_traces):
        trace.visible = visibility_masks[0][i]

    # ============================================================
    # 5) FINAL LAYOUT
    # ============================================================

    fig.update_layout(
        title_text="OHADA Dashboard (Tabbed View)",
        height=800,
        width=1400,
        template="plotly_white",
        hovermode="x unified",
        barmode="stack",
    )

    fig.update_yaxes(title_text="Value", secondary_y=False)
    fig.update_yaxes(title_text="Growth (%)", secondary_y=True)

    fig.show()
