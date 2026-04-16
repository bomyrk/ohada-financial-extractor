"""
Matplotlib style presets for OHADA visualization.
"""

import matplotlib.pyplot as plt
from .colors import PRIMARY_BLUE, LIGHT_GRAY, TEAL, ORANGE

def apply_ohada_style():
    """Apply a clean, modern style for static OHADA plots."""
    plt.style.use("default")

    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": LIGHT_GRAY,
        "axes.edgecolor": PRIMARY_BLUE,
        "axes.labelcolor": PRIMARY_BLUE,
        "axes.titleweight": "bold",
        "axes.titlesize": 14,
        "axes.grid": True,
        "grid.color": "#CCCCCC",
        "grid.alpha": 0.4,
        "xtick.color": PRIMARY_BLUE,
        "ytick.color": PRIMARY_BLUE,
        "font.size": 11,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "lines.linewidth": 2,
        "lines.markersize": 6,
    })


def apply_dark_style():
    """Optional dark theme."""
    plt.style.use("dark_background")

    plt.rcParams.update({
        "axes.facecolor": "#222222",
        "figure.facecolor": "#111111",
        "axes.edgecolor": TEAL,
        "axes.labelcolor": TEAL,
        "xtick.color": TEAL,
        "ytick.color": TEAL,
        "grid.color": "#444444",
        "grid.alpha": 0.3,
        "lines.linewidth": 2,
        "lines.markersize": 6,
        "legend.frameon": False,
    })
