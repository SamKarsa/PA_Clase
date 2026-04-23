import streamlit as st
import pandas as pd
from database import DatabaseClient
from dotenv import load_dotenv

load_dotenv()

st.title("💾 Datos en MongoDB")
st.markdown("### Consulta y Visualización de Datos Almacenados")
st.markdown("---")

db = DatabaseClient()

if not db.conectar():
    st.error("❌ No se pudo conectar a MongoDB. Verifica tu configuración.")
    st.stop()

# -----------------------------
# MÉTRICAS GENERALES
# -----------------------------
st.subheader("📊 Resumen General")

col1, col2, col3, col4 = st.columns(4)

total_docs = db.contar_documentos()

with col1:
    st.metric("📦 Total Registros", f"{total_docs:,}")

if total_docs > 0:
    # Traer todos los datos necesarios para métricas
    datos_metricas = db.consultar_datos(limite=total_docs)
    df_metricas = pd.DataFrame(datos_metricas)

    with col2:
        años_unicos = df_metricas["a_o"].nunique() if "a_o" in df_metricas.columns else 0
        st.metric("📅 Años Únicos", años_unicos)

    with col3:
        nacionalidades = df_metricas["nacionalidad"].nunique() if "nacionalidad" in df_metricas.columns else 0
        st.metric("🌍 Nacionalidades", nacionalidades)

    with col4:
        if "_fecha_insercion" in df_metricas.columns:
            ultima_fecha = df_metricas["_fecha_insercion"].max()
            ultima_fecha_txt = ultima_fecha.strftime("%Y-%m-%d %H:%M") if pd.notnull(ultima_fecha) else "N/A"
        else:
            ultima_fecha_txt = "N/A"

        st.metric("🕒 Última Actualización", ultima_fecha_txt)

st.markdown("---")

# -----------------------------
# FILTROS
# -----------------------------
st.subheader("🔍 Filtros de Búsqueda")

if total_docs > 0:
    # Traer todos los datos solo para construir filtros
    df_filtros = df_metricas.copy()

    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        años_disponibles = ["Todos"] + sorted(df_filtros["a_o"].dropna().unique().tolist(), reverse=True)
        año_seleccionado = st.selectbox("📅 Año:", años_disponibles)

    with col2:
        nacionalidades_disponibles = ["Todos"] + sorted(df_filtros["nacionalidad"].dropna().unique().tolist())
        nacionalidad_seleccionada = st.selectbox("🌍 Nacionalidad:", nacionalidades_disponibles)

    with col3:
        orden_meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        meses_presentes = df_filtros["mes"].dropna().unique().tolist()
        meses_disponibles = ["Todos"] + [m for m in orden_meses if m in meses_presentes]
        mes_seleccionado = st.selectbox("📆 Mes:", meses_disponibles)

    with col4:
        st.write("")
        st.write("")
        if st.button("🔄 Limpiar", use_container_width=True):
            st.session_state.pagina = 1
            st.rerun()

    filtro_mongo = {}
    if año_seleccionado != "Todos":
        filtro_mongo["a_o"] = año_seleccionado
    if nacionalidad_seleccionada != "Todos":
        filtro_mongo["nacionalidad"] = nacionalidad_seleccionada
    if mes_seleccionado != "Todos":
        filtro_mongo["mes"] = mes_seleccionado

    st.markdown("---")

    # -----------------------------
    # PAGINACIÓN
    # -----------------------------
    st.subheader("📋 Datos")

    REGISTROS_POR_PAGINA = 100
    total_filtrado = db.contar_documentos(filtro=filtro_mongo)

    if total_filtrado > 0:
        total_paginas = (total_filtrado - 1) // REGISTROS_POR_PAGINA + 1

        if "pagina" not in st.session_state:
            st.session_state.pagina = 1

        st.session_state.pagina = min(st.session_state.pagina, total_paginas)

        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            st.info(f"📊 {total_filtrado:,} registros encontrados")

        with col2:
            pagina = st.number_input(
                "Página",
                min_value=1,
                max_value=total_paginas,
                value=st.session_state.pagina,
                step=1
            )
            st.session_state.pagina = pagina

        with col3:
            st.info(f"📄 Página {pagina} de {total_paginas}")

        offset = (pagina - 1) * REGISTROS_POR_PAGINA

        datos_pagina = db.consultar_datos(
            filtro=filtro_mongo,
            limite=REGISTROS_POR_PAGINA,
            skip=offset
        )

        df_pagina = pd.DataFrame(datos_pagina)

        if not df_pagina.empty:
            columnas_ocultar = ["_id", "_fecha_insercion"]
            df_pagina = df_pagina.drop(columns=columnas_ocultar, errors="ignore")

            st.dataframe(df_pagina, use_container_width=True, height=500)

            inicio = offset + 1
            fin = min(offset + len(df_pagina), total_filtrado)
            st.caption(f"Mostrando registros {inicio:,} - {fin:,} de {total_filtrado:,}")

else:
    st.info("ℹ️ No hay datos en MongoDB. Ve a la página de API para sincronizar datos.")

db.desconectar()

st.markdown("---")
st.caption("💾 Datos almacenados en MongoDB Atlas")