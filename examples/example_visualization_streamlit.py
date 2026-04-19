"""
Example: OHADA Visualization & Streamlit Dashboard
==================================================

This example demonstrates how to:

1. Load a DSF Excel file
2. Extract the OHADA statement
3. Display static dashboards (assets, liabilities, income, cashflow)
4. Display the dynamic tabbed dashboard
5. Launch the Streamlit dashboard

Run:
    python examples/example_visualization_streamlit.py

To run Streamlit:
    streamlit run examples/example_visualization_streamlit.py
"""

from pathlib import Path
import streamlit as st

from ohada_extractor.core.extractor import FinancialExtractor

# Visualization functions
from ohada_extractor.visualization.dynamic.plot_dynamic_overview import (
    plot_overview_dashboard_clean,
)
from ohada_extractor.visualization.dynamic.plot_dynamic_tabs import (
    plot_ohada_tabs_dynamic,
)


def load_statement():
    """Load the sample DSF file and extract the OHADA statement."""
    sample_file = Path(__file__).parent / "data" / "DSF_Normal_Tantanpion_2024.xlsx"

    extractor = FinancialExtractor()
    statement = extractor.extract_from_excel(sample_file)

    # Build xarray (recommended)
    statement.to_xarray()

    return statement


def run_static_dashboards(statement):
    """Display the 4×2 static overview dashboard."""
    st.subheader("📊 OHADA Overview Dashboard (Static)")
    st.write("This dashboard shows grouped, stacked, waterfall, and cashflow charts.")

    plot_overview_dashboard_clean(statement)


def run_dynamic_tabs(statement):
    """Display the dynamic tabbed dashboard."""
    st.subheader("🗂️ OHADA Dashboard (Dynamic Tabs)")
    st.write("Switch between Assets, Liabilities, Income, and Cashflow.")

    plot_ohada_tabs_dynamic(statement)


def main():
    st.title("OHADA Financial Visualization Example")
    st.write(
        """
        This example demonstrates how to visualize OHADA DSF statements using:

        - Static dashboards (4×2 layout)
        - Dynamic tabbed dashboards
        - Streamlit integration
        """
    )

    # ---------------------------------------------------------------
    # Load statement
    # ---------------------------------------------------------------
    st.header("1. Load DSF File")
    statement = load_statement()
    st.success("DSF file loaded and statement extracted successfully.")

    # ---------------------------------------------------------------
    # Choose visualization mode
    # ---------------------------------------------------------------
    st.header("2. Choose Visualization Mode")

    mode = st.radio(
        "Select a dashboard:",
        [
            "Static Overview Dashboard",
            "Dynamic Tabbed Dashboard",
        ],
    )

    if mode == "Static Overview Dashboard":
        run_static_dashboards(statement)

    elif mode == "Dynamic Tabbed Dashboard":
        run_dynamic_tabs(statement)


if __name__ == "__main__":
    main()
