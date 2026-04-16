"""
Dynamic (plotly) plotting for a single financial data type.
"""

import plotly.graph_objects as go

from ..utils import prepare_data_for_plotting


def plot_single_dynamic(statement, data_type, style, period, value_type):
    """
    Create dynamic plot for a single financial data type using plotly.

    Args:
        statement: FinancialStatement instance
        data_type: 'assets', 'liabilities', 'income', 'cashflow'
        style: 'bar', 'line', 'area'
        period: 'all' or specific year
        value_type: 'Net', 'Gross', 'Amort' (assets only)
    """

    data = prepare_data_for_plotting(statement, data_type, period, value_type)

    if isinstance(data.compte.values[0], tuple):
        labels = [item[0] for item in data.compte.values]
    else:
        labels = data.compte.values

    fig = go.Figure()

    if period == "all":
        for year in data.annee.values:
            year_data = data.sel(annee=year)
            year_label = str(year)[:10]

            if style == "bar":
                fig.add_trace(
                    go.Bar(name=year_label, x=labels, y=year_data.values)
                )
            elif style == "line":
                fig.add_trace(
                    go.Scatter(
                        name=year_label,
                        x=labels,
                        y=year_data.values,
                        mode="lines+markers",
                    )
                )
            elif style == "area":
                fig.add_trace(
                    go.Scatter(
                        name=year_label,
                        x=labels,
                        y=year_data.values,
                        fill="tozeroy",
                    )
                )
    else:
        if style == "bar":
            fig.add_trace(go.Bar(x=labels, y=data.values))
        elif style == "line":
            fig.add_trace(
                go.Scatter(x=labels, y=data.values, mode="lines+markers")
            )
        elif style == "area":
            fig.add_trace(
                go.Scatter(x=labels, y=data.values, fill="tozeroy")
            )

    title_value = value_type if data_type == "assets" else "Net"

    fig.update_layout(
        title=f"{data_type.capitalize()} Analysis ({title_value})",
        xaxis_title="Accounts",
        yaxis_title="Values",
        template="plotly_white",
        xaxis_tickangle=-45,
        showlegend=True,
    )
    fig.show()
