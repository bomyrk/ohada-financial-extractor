import streamlit as st
import json

from src.ohada_extractor import FinancialExtractor

# Import your visualization functions
from src.ohada_extractor.visualization.dynamic.plot_dynamic_overview import (
    plot_overview_dashboard_clean
)
from src.ohada_extractor.visualization.dynamic.plot_dynamic_tabs import (
    plot_ohada_tabs_dynamic
)
from src.ohada_extractor.visualization.dynamic.plot_dynamic_summary import (
    plot_asset_summary_dynamic,
    plot_liability_summary_dynamic,
)
from src.ohada_extractor.visualization.dynamic.plot_dynamic_summary import (
    plot_income_summary_dynamic
)
from src.ohada_extractor.visualization.dynamic.plot_dynamic_summary import (
    plot_cashflow_summary_dynamic
)


# ============================================================
#  STREAMLIT APP LAYOUT
# ============================================================

st.set_page_config(
    page_title="OHADA Financial Dashboard",
    layout="wide",
)

st.title("📊 OHADA Financial Dashboard")
st.markdown("A clean, professional dashboard for OHADA financial statements.")


# ============================================================
#  FILE UPLOAD
# ============================================================

st.sidebar.header("📁 Upload DSF Excel File(s)")

uploaded_excels = st.sidebar.file_uploader(
    "Upload one or multiple DSF Excel files",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded_excels:
    extractor = FinancialExtractor()

    with st.spinner("Extracting financial data from Excel..."):
        if len(uploaded_excels) == 1:
            # Save the uploaded file to a temporary path
            f = uploaded_excels[0]
            temp_path = f"temp_{f.name}"
            with open(temp_path, "wb") as tmp:
                tmp.write(f.read())

            # Extract using your real API
            statement = extractor.extract_from_excel(temp_path)

        else:
            # Multiple files → save each to disk
            file_list = []
            for f in uploaded_excels:
                temp_path = f"temp_{f.name}"
                with open(temp_path, "wb") as tmp:
                    tmp.write(f.read())
                file_list.append(temp_path)

            # Extract using your real API
            statement = extractor.extract_over_period(file_list)

    statement.to_xarray()
    st.sidebar.success("Excel file(s) processed successfully")

else:
    st.warning("Please upload at least one DSF Excel file to continue.")
    st.stop()




# ============================================================
#  SIDEBAR NAVIGATION
# ============================================================

st.sidebar.header("📌 Navigation")

page = st.sidebar.radio(
    "Choose a dashboard:",
    [
        "Overview (4‑Panel)",
        "Tabbed Dashboard",
        "Assets Summary",
        "Liabilities Summary",
        "Income Summary",
        "Cashflow Summary",
    ]
)


# ============================================================
#  PAGE ROUTING
# ============================================================

if page == "Overview (4‑Panel)":
    st.subheader("📊 OHADA 4‑Panel Overview (Clean Version)")
    plot_overview_dashboard_clean(statement)

elif page == "Tabbed Dashboard":
    st.subheader("🗂️ Tabbed Dashboard")
    plot_ohada_tabs_dynamic(statement)

elif page == "Assets Summary":
    st.subheader("🏛️ Assets Summary")
    period = st.selectbox("Select period:", ["all"] + statement.years.year.astype(str).tolist())
    plot_asset_summary_dynamic(statement, period)

elif page == "Liabilities Summary":
    st.subheader("📘 Liabilities Summary")
    period = st.selectbox("Select period:", ["all"] + statement.years.year.astype(str).tolist())
    plot_liability_summary_dynamic(statement, period)

elif page == "Income Summary":
    st.subheader("💰 Income Summary")
    period = st.selectbox("Select period:", ["all"] + statement.years.year.astype(str).tolist())
    plot_income_summary_dynamic(statement, period)

elif page == "Cashflow Summary":
    st.subheader("💵 Cashflow Summary")
    period = st.selectbox("Select period:", ["all"] + statement.years.year.astype(str).tolist())
    plot_cashflow_summary_dynamic(statement, period)
