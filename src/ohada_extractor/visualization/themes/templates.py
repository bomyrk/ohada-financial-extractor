"""
Plotly templates for OHADA visualization.
"""

import plotly.io as pio
from .colors import PRIMARY_BLUE, TEAL, LIGHT_GRAY, ORANGE

def register_ohada_template():
    """Register a clean white template for OHADA dynamic plots."""

    ohada_template = pio.templates["plotly_white"]

    ohada_template.layout.update(
        font=dict(family="Arial", size=12, color=PRIMARY_BLUE),
        title=dict(font=dict(size=18, color=PRIMARY_BLUE)),
        xaxis=dict(
            gridcolor=LIGHT_GRAY,
            zerolinecolor=LIGHT_GRAY,
            linecolor=PRIMARY_BLUE,
        ),
        yaxis=dict(
            gridcolor=LIGHT_GRAY,
            zerolinecolor=LIGHT_GRAY,
            linecolor=PRIMARY_BLUE,
        ),
        colorway=[PRIMARY_BLUE, TEAL, ORANGE],
    )

    pio.templates["ohada"] = ohada_template


def register_dark_template():
    """Optional dark theme for plotly."""

    dark_template = pio.templates["plotly_dark"]

    dark_template.layout.update(
        font=dict(family="Arial", size=12, color="#EEEEEE"),
        title=dict(font=dict(size=18, color="#FFFFFF")),
        colorway=["#2CA6A4", "#F28C28", "#4CAF50"],
    )

    pio.templates["ohada_dark"] = dark_template
