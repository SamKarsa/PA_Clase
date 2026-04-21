import streamlit as st
import pandas as pd
from database import DatabaseClient
import os
from dotenv import load_dotenv

load_dotenv()

st.title("💾 Datos en MongoDB")
st.markdown("### Consulta y Visualización de Datos Almacenados")
st.markdown("---")

db = DatabaseClient()

if not db.conectar():
    st.error("❌ No se pudo conectar a MongoDB. Verifica tu configuración.")
    st.stop()


# MÉTRICAS GENERALES
st.subheader("📊 Resumen General")

col1, col2, col3, col4 = st.columns(4)

total_docs = db.contar_documentos()

with col1:
    st.metric("📦 Total Registros", f"{total_docs:,}")

if total_docs > 0:
    datos_muestra = db.consultar_datos(limite=1000)
    df_muestra = pd.DataFrame(datos_muestra)

    with col2:
        if 'a_o' in df_muestra.columns:
            st.metric("📅 Años Únicos", df_muestra['a_o'].nunique())
        else:
            st.metric("📅 Años Únicos", "N/A")

    with col3:
        if 'nacionalidad' in df_muestra.columns:
            st.metric("🌍 Nacionalidades", df_muestra['nacionalidad'].nunique())
        else:
            st.metric("🌍 Nacionalidades", "N/A")

    with col4:
        if '_fecha_insercion' in df_muestra.columns and len(df_muestra) > 0:
            ultima_fecha = df_muestra['_fecha_insercion'].max()
            st.metric("🕒 Última Actualización", ultima_fecha.strftime("%Y-%m-%d %H:%M") if hasattr(ultima_fecha, 'strftime') else "N/A")
        else:
            st.metric("🕒 Última Actualización", "N/A")
else:
    with col2:
        st.metric("📅 Años Únicos", "0")
    with col3:
        st.metric("🌍 Nacionalidades", "0")
    with col4:
        st.metric("🕒 Última Actualización", "N/A")

st.markdown("---")


# FILTROS
st.subheader("🔍 Filtros de Búsqueda")

if total_docs > 0:
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    datos_filtros = db.consultar_datos(limite=10000)
    df_filtros = pd.DataFrame(datos_filtros)

    with col1:
        años_disponibles = ["Todos"]
        if 'a_o' in df_filtros.columns:
            años_disponibles.extend(sorted(df_filtros['a_o'].unique(), reverse=True))
        año_seleccionado = st.selectbox("📅 Año:", años_disponibles)

    with col2:
        nacionalidades_disponibles = ["Todos"]
        if 'nacionalidad' in df_filtros.columns:
            nacionalidades_disponibles.extend(sorted(df_filtros['nacionalidad'].unique()))
        nacionalidad_seleccionada = st.selectbox("🌍 Nacionalidad:", nacionalidades_disponibles)

    with col3:
        meses_disponibles = ["Todos"]
        if 'mes' in df_filtros.columns:
            orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                           "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            meses_ordenados = [m for m in orden_meses if m in df_filtros['mes'].unique()]
            meses_disponibles.extend(meses_ordenados)
        mes_seleccionado = st.selectbox("📆 Mes:", meses_disponibles)

    with col4:
        st.write("")
        st.write("")
        if st.button("🔄 Limpiar", width='stretch'):
            st.session_state.pagina = 1
            st.rerun()

    filtro_mongo = {}
    if año_seleccionado != "Todos":
        filtro_mongo['a_o'] = año_seleccionado
    if nacionalidad_seleccionada != "Todos":
        filtro_mongo['nacionalidad'] = nacionalidad_seleccionada
    if mes_seleccionado != "Todos":
        filtro_mongo['mes'] = mes_seleccionado

    st.markdown("---")

    # PAGINACIÓN
    st.subheader("📋 Datos")

    REGISTROS_POR_PAGINA = 100

    total_filtrado = db.contar_documentos(filtro=filtro_mongo if filtro_mongo else None)

    if total_filtrado > 0:
        total_paginas = max(1, (total_filtrado + REGISTROS_POR_PAGINA - 1) // REGISTROS_POR_PAGINA)

        if 'pagina' not in st.session_state:
            st.session_state.pagina = 1

        st.session_state.pagina = min(st.session_state.pagina, total_paginas)

        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            st.info(f"📊 {total_filtrado:,} registros en total")

        with col2:
            pagina = st.number_input(
                f"Página (1-{total_paginas})",
                min_value=1,
                max_value=total_paginas,
                value=st.session_state.pagina,
                step=1,
                key="pagina_input"
            )
            st.session_state.pagina = pagina

        with col3:
            st.info(f"📄 Página {pagina} de {total_paginas}")

        offset = (pagina - 1) * REGISTROS_POR_PAGINA

        datos_pagina = db.consultar_datos(
            filtro=filtro_mongo if filtro_mongo else None,
            limite=REGISTROS_POR_PAGINA,
            skip=offset
        )

        if datos_pagina:
            df = pd.DataFrame(datos_pagina)
            columnas_ocultar = ['_id', '_fecha_insercion']
            df_mostrar = df.drop(columns=[c for c in columnas_ocultar if c in df.columns], errors='ignore')

            st.dataframe(df_mostrar, width='stretch', height=500)

            inicio = offset + 1
            fin = min(offset + len(datos_pagina), total_filtrado)
            st.caption(f"Mostrando registros {inicio:,} - {fin:,} de {total_filtrado:,}")

            if total_paginas > 1:
                st.markdown("---")
                st.subheader("📖 Navegación")

                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    if st.button("⏮️ Primera", disabled=pagina == 1, width='stretch'):
                        st.session_state.pagina = 1
                        st.rerun()

                with col2:
                    if st.button("◀️ Anterior", disabled=pagina == 1, width='stretch'):
                        st.session_state.pagina = pagina - 1
                        st.rerun()

                with col3:
                    st.info(f"📄 {pagina} / {total_paginas}")

                with col4:
                    if st.button("▶️ Siguiente", disabled=pagina == total_paginas, width='stretch'):
                        st.session_state.pagina = pagina + 1
                        st.rerun()

                with col5:
                    if st.button("⏭️ Última", disabled=pagina == total_paginas, width='stretch'):
                        st.session_state.pagina = total_paginas
                        st.rerun()
        else:
            st.warning("⚠️ No hay datos en esta página")
    else:
        st.warning("⚠️ No se encontraron registros con los filtros aplicados")

else:
    st.info("ℹ️ No hay datos en MongoDB. Ve a la página de API para sincronizar datos.")

db.desconectar()

st.markdown("---")
st.caption("💾 Datos almacenados en MongoDB Atlas")
