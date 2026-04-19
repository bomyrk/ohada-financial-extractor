"""
Dynamic (plotly) plotting for all financial data types in a 2×2 grid.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils import prepare_data_for_plotting


def plot_all_dynamic(statement, style, period="all", value_type="Net"):
    """
    Create dynamic plot for all financial data types using plotly.

    Args:
        statement: FinancialStatement instance
        style: 'bar', 'line', 'area'
        period: 'all' or specific year
        value_type: 'Net', 'Gross', 'Amort' (assets only)
    """

    data_types = ["assets", "liabilities", "income", "cashflow"]
    colors = ["skyblue", "salmon", "lightgreen", "orange"]

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("Assets", "Liabilities", "Income", "Cash Flow"),
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
    )

    for idx, (data_type, color) in enumerate(zip(data_types, colors), 1):
        row = (idx - 1) // 2 + 1
        col = (idx - 1) % 2 + 1

        data = prepare_data_for_plotting(statement, data_type, period, value_type)

        # Remove accounts that are zero for all periods
        #non_zero_mask = data.values.max(axis=0) != 0
        #data = data[:, non_zero_mask]

        if isinstance(data.compte.values[0], tuple):
            labels = [item[0] for item in data.compte.values]
        else:
            labels = data.compte.values

        if period == "all":
            for year in data.annee.values:
                year_data = data.sel(annee=year)
                year_label = str(year)[:10]

                if style == "bar":
                    fig.add_trace(
                        go.Bar(
                            name=f"{data_type.capitalize()} {year_label}",
                            x=labels,
                            y=year_data.values,
                            marker_color=color,
                            legendgroup=data_type,
                        ),
                        row=row,
                        col=col,
                    )
                elif style == "line":
                    fig.add_trace(
                        go.Scatter(
                            name=f"{data_type.capitalize()} {year_label}",
                            x=labels,
                            y=year_data.values,
                            mode="lines+markers",
                            line=dict(color=color),
                            legendgroup=data_type,
                        ),
                        row=row,
                        col=col,
                    )
                elif style == "area":
                    fig.add_trace(
                        go.Scatter(
                            name=f"{data_type.capitalize()} {year_label}",
                            x=labels,
                            y=year_data.values,
                            fill="tozeroy",
                            line=dict(color=color),
                            legendgroup=data_type,
                        ),
                        row=row,
                        col=col,
                    )
        else:
            period_label = str(period)[:10]
            if style == "bar":
                fig.add_trace(
                    go.Bar(
                        name=f"{data_type.capitalize()} {period_label}",
                        x=labels,
                        y=data.values,
                        marker_color=color,
                    ),
                    row=row,
                    col=col,
                )
            elif style == "line":
                fig.add_trace(
                    go.Scatter(
                        name=f"{data_type.capitalize()} {period_label}",
                        x=labels,
                        y=data.values,
                        mode="lines+markers",
                        line=dict(color=color),
                    ),
                    row=row,
                    col=col,
                )
            elif style == "area":
                fig.add_trace(
                    go.Scatter(
                        name=f"{data_type.capitalize()} {period_label}",
                        x=labels,
                        y=data.values,
                        fill="tozeroy",
                        line=dict(color=color),
                    ),
                    row=row,
                    col=col,
                )

        fig.update_xaxes(title_text="Accounts", row=row, col=col, tickangle=45)
        fig.update_yaxes(title_text="Values", row=row, col=col)

    if style == "bar" and period == "all":
        fig.update_layout(barmode="group")

    fig.update_layout(
        height=800,
        width=1200,
        title_text=f"Financial Data Analysis ({'All Periods' if period == 'all' else period})",
        showlegend=True,
        template="plotly_white",
        title_x=0.5,
        legend_title_text="Data Type / Year",
        margin=dict(b=100),
    )

    fig.show()
