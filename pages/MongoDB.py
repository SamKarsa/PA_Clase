import streamlit as st
import pandas as pd
from database import DatabaseClient
from dotenv import load_dotenv

load_dotenv()

st.title("💾 Datos en MongoDB")
st.markdown("### Consulta y Visualización de Datos Almacenados")
st.markdown("---")

@st.cache_resource
def get_db():
    db = DatabaseClient()
    if not db.conectar():
        return None
    return db

db = get_db()

if db is None:
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
    @st.cache_data(ttl=300)
    def cargar_valores_distintos():
        años = db.obtener_valores_distintos("a_o")
        nacionalidades = db.obtener_valores_distintos("nacionalidad")
        meses = db.obtener_valores_distintos("mes")
        ultima = db.obtener_ultima_insercion()
        return años, nacionalidades, meses, ultima

    años_distintos, nacionalidades_distintas, meses_distintos, ultima_insercion = cargar_valores_distintos()

    with col2:
        st.metric("📅 Años Únicos", len(años_distintos))

    with col3:
        st.metric("🌍 Nacionalidades", len(nacionalidades_distintas))

    with col4:
        if ultima_insercion:
            ultima_fecha_txt = pd.Timestamp(ultima_insercion).strftime("%Y-%m-%d %H:%M")
        else:
            ultima_fecha_txt = "N/A"
        st.metric("🕒 Última Actualización", ultima_fecha_txt)

    st.markdown("---")

    # -----------------------------
    # FILTROS
    # -----------------------------
    st.subheader("🔍 Filtros de Búsqueda")

    orden_meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        años_disponibles = ["Todos"] + sorted(años_distintos, reverse=True)
        año_seleccionado = st.selectbox("📅 Año:", años_disponibles)

    with col2:
        nacionalidades_disponibles = ["Todos"] + sorted(nacionalidades_distintas)
        nacionalidad_seleccionada = st.selectbox("🌍 Nacionalidad:", nacionalidades_disponibles)

    with col3:
        meses_disponibles = ["Todos"] + [m for m in orden_meses if m in meses_distintos]
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

st.markdown("---")
st.caption("💾 Datos almacenados en MongoDB Atlas")
