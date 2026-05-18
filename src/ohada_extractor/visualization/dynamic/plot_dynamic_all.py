"""Dynamic (plotly) plotting for all financial data types in a 2×2 grid."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils import get_account_label, prepare_data_for_plotting


def plot_all_dynamic(statement, style, period="all", value_type="Net"):
    """Create dynamic plot for all financial data types using plotly.

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
        vertical_spacing=0.15,  # Augmenté légèrement pour laisser de la place aux étiquettes inclinées
        horizontal_spacing=0.1,
    )

    for idx, (data_type, color) in enumerate(zip(data_types, colors), 1):
        row = (idx - 1) // 2 + 1
        col = (idx - 1) % 2 + 1

        data = prepare_data_for_plotting(statement, data_type, period, value_type)

        # --------------------------------------------------------
        # NETTOYAGE XARRAY : Éliminer les comptes entièrement à zéro
        # --------------------------------------------------------
        # Calcule la valeur absolue maximale sur l'axe du temps ('annee') ou globalement
        dim_to_reduce = "annee" if "annee" in data.dims else None
        if dim_to_reduce:
            max_vals = np.abs(data.values).max(axis=data.dims.index(dim_to_reduce))
        else:
            max_vals = np.abs(data.values)

        non_zero_indices = np.where(max_vals > 1e-2)[0]
        if len(non_zero_indices) > 0:
            data = data.isel(compte=non_zero_indices)

        # --------------------------------------------------------
        # EXTRACTION ROBUSTE DES LABELS (Nomenclature OHADA)
        # --------------------------------------------------------
        if "Reference" in data.coords:
            labels = [
                get_account_label(statement, data_type, ref)
                for ref in data.coords["Reference"].values
            ]
        elif (
            hasattr(data.compte, "values")
            and len(data.compte.values) > 0
            and isinstance(data.compte.values[0], tuple)
        ):
            labels = [item[0] for item in data.compte.values]
        else:
            # Fallback de secours si l'index est aplati
            labels = [str(c) for c in data.compte.values]

        # --------------------------------------------------------
        # SÉLECTION ET AJOUT DES TRACES
        # --------------------------------------------------------
        if period == "all":
            for year in data.annee.values:
                year_data = data.sel(annee=year)
                # Conversion sécurisée en chaîne propre (ex: "2026")
                year_label = str(pd.to_datetime(year).year)
                trace_vals = year_data.values.flatten()

                if style == "bar":
                    fig.add_trace(
                        go.Bar(
                            name=f"{data_type.capitalize()} {year_label}",
                            x=labels,
                            y=trace_vals,
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
                            y=trace_vals,
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
                            y=trace_vals,
                            fill="tozeroy",
                            line=dict(color=color),
                            legendgroup=data_type,
                        ),
                        row=row,
                        col=col,
                    )
        else:
            period_label = str(pd.to_datetime(period).year)
            trace_vals = data.values.flatten()

            if style == "bar":
                fig.add_trace(
                    go.Bar(
                        name=f"{data_type.capitalize()} {period_label}",
                        x=labels,
                        y=trace_vals,
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
                        y=trace_vals,
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
                        y=trace_vals,
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
        height=900,  # Légèrement augmenté pour éviter la superposition des titres d'axes
        width=1300,
        title_text=f"Financial Data Analysis ({'All Periods' if period == 'all' else period})",
        showlegend=True,
        template="plotly_white",
        title_x=0.5,
        legend_title_text="Data Type / Year",
        margin=dict(b=120, t=100),
    )

    fig.show()
