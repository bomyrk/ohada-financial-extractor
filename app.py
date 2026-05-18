import os
import tempfile

import streamlit as st

# Import your FinancialExtractor
from src.ohada_extractor import FinancialExtractor

# Import your visualization functions
from src.ohada_extractor.visualization.dynamic.plot_dynamic_overview import (
    plot_overview_dashboard_clean,
)
from src.ohada_extractor.visualization.dynamic.plot_dynamic_summary import (
    plot_asset_summary_dynamic,
    plot_cashflow_summary_dynamic,
    plot_income_summary_dynamic,
    plot_liability_summary_dynamic,
)
from src.ohada_extractor.visualization.dynamic.plot_dynamic_tabs import (
    plot_ohada_tabs_dynamic,
)

# ============================================================
#  STREAMLIT APP LAYOUT
# ============================================================

st.set_page_config(
    page_title="OHADA Financial Extractor — OHADA Financial Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 OHADA Financial Dashboard")
st.markdown("A clean, professional dashboard for OHADA financial statements.")
st.markdown("---")

# ============================================================
#  SESSION STATE INITIALIZATION (Mise en cache de l'état)
# ============================================================
# Évite de recalculer l'extraction lourde à chaque interaction utilisateur
if "statement" not in st.session_state:
    st.session_state.statement = None
if "current_files_processed" not in st.session_state:
    st.session_state.current_files_processed = None

# ============================================================
#  FILE UPLOAD
# ============================================================

st.sidebar.header("📁 Upload DSF Excel File(s)")

uploaded_excels = st.sidebar.file_uploader(
    "Upload one or multiple DSF Excel files",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
)

# Génération d'un identifiant unique basé sur les fichiers présents dans le uploader
files_identifier = (
    [(f.name, f.size) for f in uploaded_excels] if uploaded_excels else []
)

# Si l'utilisateur supprime ou change les fichiers, 
# on réinitialise l'état pour forcer un nouveau clic
if files_identifier != st.session_state.current_files_processed:
    st.session_state.statement = None

# Affichage du bouton de validation uniquement si des fichiers sont chargés
if uploaded_excels:
    st.sidebar.markdown("---")
    st.sidebar.write(f"📎 **{len(uploaded_excels)} file(s) ready.**")

    # Le bouton qui déclenche explicitement le chargement
    process_button = st.sidebar.button(
        "⚙️ Process & Load Data", type="primary", use_container_width=True
    )

    if process_button:
        extractor = FinancialExtractor()
        temp_paths = []

        try:
            with st.spinner(
                "Extracting and normalizing financial data from DSF tables..."
            ):
                # Écriture temporaire sur le disque
                for f in uploaded_excels:
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=f"_{f.name}"
                    ) as tmp:
                        tmp.write(f.getvalue())
                        temp_paths.append(tmp.name)

                # 1. Routage de l'extraction brute
                if len(temp_paths) == 1:
                    statement = extractor.extract_from_excel(temp_paths[0])
                else:
                    statement = extractor.extract_over_period(temp_paths)

                # Mise à jour sécurisée de l'index global des années du statement
                # if hasattr(statement, "periods"):
                #    statement.years = pd.DatetimeIndex(np.unique(statement.periods))
                # ============================================================

                # Stockage persistant dans la session
                st.session_state.statement = statement
                st.session_state.current_files_processed = files_identifier
                st.sidebar.success("Data loaded and cleaned successfully!")

        except Exception as e:
            st.error(
                f"Extraction Error: An error occurred while parsing the DSF files. Details: {e}"
            )
            st.stop()
        finally:
            # Nettoyage immédiat du disque
            for path in temp_paths:
                if os.path.exists(path):
                    os.remove(path)
else:
    st.session_state.statement = None
    st.session_state.current_files_processed = None
    st.warning("Please upload at least one DSF Excel file in the sidebar to continue.")
    st.stop()

# Si les fichiers sont là mais que l'utilisateur n'a pas encore cliqué sur le bouton
if st.session_state.statement is None:
    st.info(
        "ℹ️ Click on **'Process & Load Data'** in the sidebar to generate the dashboards."
    )
    st.stop()

statement = st.session_state.statement


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
    ],
)

# Extraction sécurisée des années disponibles depuis xarray
try:
    available_years = statement.years.year.values.tolist()
except Exception:
    # Fallback si l'index de dates est une liste de chaînes simples
    available_years = [str(y)[:4] for y in statement.periods]

# ============================================================
#  PAGE ROUTING & RENDERING
# ============================================================
if page == "Overview (4‑Panel)":
    st.subheader("📊 OHADA 4‑Panel Structural Overview")
    plot_overview_dashboard_clean(statement)

elif page == "Tabbed Dashboard":
    st.subheader("🗂️ Detailed Multi-Tab Financial Statements")
    plot_ohada_tabs_dynamic(statement)

elif page == "Assets Summary":
    st.subheader("🏛️ Balance Sheet: Assets Summary")
    period = st.selectbox("Select Target Period:", ["all"] + available_years)
    plot_asset_summary_dynamic(statement, period)

elif page == "Liabilities Summary":
    st.subheader("📘 Balance Sheet: Liabilities & Equity Summary")
    period = st.selectbox("Select Target Period:", ["all"] + available_years)
    plot_liability_summary_dynamic(statement, period)

elif page == "Income Summary":
    st.subheader("💰 Income Statement Summary (Compte de Résultat)")
    period = st.selectbox("Select Target Period:", ["all"] + available_years)
    plot_income_summary_dynamic(statement, period)

elif page == "Cashflow Summary":
    st.subheader("💵 Cash Flow Statement Summary (TFT)")
    period = st.selectbox("Select Target Period:", ["all"] + available_years)
    plot_cashflow_summary_dynamic(statement, period)
