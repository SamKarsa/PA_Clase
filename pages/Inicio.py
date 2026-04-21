import streamlit as st
import os
from dotenv import load_dotenv
from database import DatabaseClient
from sincronizador_auto import obtener_info_scheduler

load_dotenv()

st.title("🇨🇴 Sistema de Análisis de Entradas de Extranjeros a Colombia")
st.markdown("### Datos Abiertos Colombia → MongoDB Atlas")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## 📖 Acerca del Proyecto

    Este sistema permite:

    - 📡 **Sincronizar** datos de la API de Datos Abiertos Colombia
    - 💾 **Almacenar** información en MongoDB Atlas
    - 📊 **Visualizar** estadísticas y gráficas interactivas
    - 🔍 **Consultar** datos históricos desde 2012

    ### 📊 Dataset: Entradas de Extranjeros a Colombia

    Consolidado de entradas de extranjeros a Colombia desde 2012,
    discriminado por **nacionalidad**, **género** y **periodo**.
    """)

with col2:
    st.markdown("""
    ## 🎯 Navegación

    👈 **Usa el menú lateral** para acceder a:

    - 📡 **Sincronización API**: Sincronizar datos
    - 💾 **Base de Datos**: Ver datos guardados
    - 📊 **Análisis**: Gráficas y estadísticas
    """)

st.markdown("---")

# Estado del sistema
st.subheader("📊 Estado del Sistema")

col1, col2, col3 = st.columns(3)

with col1:
    if os.getenv("API_URL"):
        st.success("✅ **API Configurada**")
        st.caption("Datos Abiertos Colombia")
    else:
        st.error("❌ **API No Configurada**")

with col2:
    if os.getenv("MONGO_USER"):
        st.success("✅ **MongoDB Configurado**")
        st.caption("Cluster en Atlas")
    else:
        st.error("❌ **MongoDB No Configurado**")

with col3:
    try:
        db = DatabaseClient()
        if db.conectar():
            total = db.contar_documentos()
            db.desconectar()
            st.info(f"📊 **{total:,} Registros**")
            st.caption("En MongoDB")
        else:
            st.warning("⚠️ **No conectado**")
            st.caption("Verifica configuración")
    except Exception:
        st.warning("⚠️ **Error al contar**")
        st.caption("Intenta sincronizar")

st.markdown("---")

# Flujo del sistema
st.subheader("🔄 Flujo de Datos")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 1️⃣ API
    📡 **Datos Abiertos Colombia**

    - Entradas de extranjeros
    - Desde 2012
    - Por nacionalidad y género
    """)

with col2:
    st.markdown("""
    ### 2️⃣ Sincronización
    🔄 **Proceso**

    - Obtener datos de API
    - Limpiar datos antiguos
    - Insertar en MongoDB
    """)

with col3:
    st.markdown("""
    ### 3️⃣ Visualización
    📊 **Análisis**

    - Gráficas interactivas
    - Estadísticas
    - Exportar datos
    """)

st.markdown("---")

# Estado del scheduler
st.subheader("⏰ Sincronización Automática")

info_scheduler = obtener_info_scheduler(st.session_state.scheduler)

col1, col2, col3 = st.columns(3)

with col1:
    if info_scheduler['activo']:
        st.success("✅ Activa")
    else:
        st.error("❌ Inactiva")

with col2:
    st.info(f"⏱️ Cada {info_scheduler['intervalo_horas']} horas")

with col3:
    if info_scheduler['proxima_ejecucion']:
        st.info(f"🕐 Próxima: {info_scheduler['proxima_ejecucion'].strftime('%H:%M')}")
    else:
        st.warning("⚠️ No programada")

st.markdown("---")

with st.expander("ℹ️ Información Técnica"):
    st.markdown("""
    ### 🛠️ Tecnologías Utilizadas

    - **Frontend**: Streamlit
    - **Base de datos**: MongoDB Atlas
    - **API**: Datos Abiertos Colombia (Socrata)
    - **Lenguaje**: Python 3.12
    - **Visualización**: Plotly, Pandas

    ### 📊 Dataset

    - **Fuente**: datos.gov.co
    - **ID**: jxkp-p4t4
    - **Registros**: ~173,000
    - **Periodo**: 2012 - 2024

    ### 🔐 Configuración

    Las credenciales se gestionan mediante variables de entorno (`.env`).
    """)
