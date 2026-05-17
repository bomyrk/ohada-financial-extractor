import os
import tempfile
import streamlit as st
import pandas as pd
# Import your FinancialExtractor

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
if "processed_files_hash" not in st.session_state:
    st.session_state.processed_files_hash = None

# ============================================================
#  FILE UPLOAD
# ============================================================

st.sidebar.header("📁 Upload DSF Excel File(s)")

uploaded_excels = st.sidebar.file_uploader(
    "Upload one or multiple DSF Excel files",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

# Création d'une signature simple pour détecter si les fichiers téléversés ont changé
current_files_hash = (
    zip([f.name for f in uploaded_excels], [f.size for f in uploaded_excels])
    if uploaded_excels
    else None
)

if uploaded_excels:
    # Si les fichiers sont nouveaux ou ont changé, on déclenche l'extraction
    if st.session_state.processed_files_hash != current_files_hash:
        extractor = FinancialExtractor()
        temp_paths = []
        
        try:
            with st.spinner("Extracting and normalizing financial data from DSF tables..."):
                # Sauvegarde temporaire sécurisée
                for f in uploaded_excels:
                    # Utilisation d'un fichier temporaire qui s'auto-nettoie ou identifié proprement
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{f.name}") as tmp:
                        tmp.write(f.getvalue())
                        temp_paths.append(tmp.name)
                
                # Traitement selon le volume de fichiers
                if len(temp_paths) == 1:
                    statement = extractor.extract_from_excel(temp_paths[0])
                else:
                    statement = extractor.extract_over_period(temp_paths)
                
                # Sauvegarde dans le state de l'application
                st.session_state.statement = statement
                st.session_state.processed_files_hash = current_files_hash
                st.sidebar.success("Excel file(s) processed successfully!")
                
        except Exception as e:
            st.error(f"Extraction Error: An error occurred while parsing the DSF files. Details: {e}")
            st.stop()
        finally:
            # NETTOYAGE STRICT DU DISQUE : On efface les fichiers temporaires immédiatement après lecture
            for path in temp_paths:
                if os.path.exists(path):
                    os.remove(path)
else:
    # Réinitialisation si l'utilisateur vide sa sélection
    st.session_state.statement = None
    st.session_state.processed_files_hash = None
    st.warning("Please upload at least one DSF Excel file to generate the dashboard analysis.")
    st.stop()

# Sécurité si le statement est vide malgré tout
if st.session_state.statement is None:
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
    ]
)

# Extraction sécurisée des années disponibles depuis xarray
try:
    available_years = pd.to_datetime(statement.periods).year.astype(str).tolist()
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