import streamlit as st
from dotenv import load_dotenv
from sincronizador_auto import iniciar_scheduler

load_dotenv()

st.set_page_config(
    page_title="Entradas de Extranjeros a Colombia",
    page_icon="🇨🇴",
    layout="wide"
)

@st.cache_resource
def get_scheduler():
    return iniciar_scheduler()

if 'scheduler' not in st.session_state:
    st.session_state.scheduler = get_scheduler()

pg = st.navigation([
    st.Page("pages/Inicio.py",     title="Inicio",              icon="🏠"),
    st.Page("pages/API.py",        title="Sincronización API",  icon="📡"),
    st.Page("pages/MongoDB.py",    title="Base de Datos",       icon="💾"),
    st.Page("pages/Analisis.py",   title="Análisis",            icon="📊"),
])

pg.run()
