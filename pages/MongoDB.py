import streamlit as st
import pandas as pd
from database import DatabaseClient
import os
from dotenv import load_dotenv
from datetime import datetime
 
load_dotenv()
 
st.set_page_config(
    page_title="MongoDB - Datos",
    page_icon="💾",
    layout="wide"
)

# Header
st.title("💾 Datos en MongoDB")
st.markdown("### Consulta y Visualización de Datos Almacenados")
st.markdown("---")

# Conectar a MongoDB
db = DatabaseClient()
 
if not db.conectar():
    st.error("❌ No se pudo conectar a MongoDB. Verifica tu configuración.")
    st.stop()


# MÉTRICAS GENERALES
st.subheader("📊 Resumen General")
 
col1, col2, col3, col4 = st.columns(4)

# Total de documentos
total_docs = db.contar_documentos()

with col1:
    st.metric("📦 Total Registros", f"{total_docs:,}")
 
# Obtener datos para calcular métricas
if total_docs > 0:
    datos_muestra = db.consultar_datos(limite=1000)
    df_muestra = pd.DataFrame(datos_muestra)
    
    with col2:
        if 'a_o' in df_muestra.columns:
            años_unicos = df_muestra['a_o'].nunique()
            st.metric("📅 Años Únicos", años_unicos)
        else:
            st.metric("📅 Años Únicos", "N/A")
    
    with col3:
        if 'nacionalidad' in df_muestra.columns:
            paises_unicos = df_muestra['nacionalidad'].nunique()
            st.metric("🌍 Nacionalidades", paises_unicos)
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


st.subheader("🔍 Filtros de Búsqueda")
 
if total_docs > 0:
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    # Obtener valores únicos para los filtros
    datos_filtros = db.consultar_datos(limite=10000)
    df_filtros = pd.DataFrame(datos_filtros)
    
    with col1:
        # Filtro de año
        años_disponibles = ["Todos"]
        if 'a_o' in df_filtros.columns:
            años_disponibles.extend(sorted(df_filtros['a_o'].unique(), reverse=True))
        año_seleccionado = st.selectbox("📅 Año:", años_disponibles)
    
    with col2:
        # Filtro de nacionalidad
        nacionalidades_disponibles = ["Todos"]
        if 'nacionalidad' in df_filtros.columns:
            nacionalidades_disponibles.extend(sorted(df_filtros['nacionalidad'].unique()))
        nacionalidad_seleccionada = st.selectbox("🌍 Nacionalidad:", nacionalidades_disponibles)
    
    with col3:
        # Filtro de mes
        meses_disponibles = ["Todos"]
        if 'mes' in df_filtros.columns:
            meses_unicos = df_filtros['mes'].unique()
            # Ordenar meses
            orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            meses_ordenados = [m for m in orden_meses if m in meses_unicos]
            meses_disponibles.extend(meses_ordenados)
        mes_seleccionado = st.selectbox("📆 Mes:", meses_disponibles)
    
    with col4:
        st.write("")  # Espaciado
        st.write("")  
        btn_limpiar = st.button("🔄 Limpiar", width='stretch')
    
    # Aplicar filtros
    filtro_mongo = {}
    
    if año_seleccionado != "Todos":
        filtro_mongo['a_o'] = año_seleccionado
    
    if nacionalidad_seleccionada != "Todos":
        filtro_mongo['nacionalidad'] = nacionalidad_seleccionada
    
    if mes_seleccionado != "Todos":
        filtro_mongo['mes'] = mes_seleccionado
    
    # Limpiar filtros
    if btn_limpiar:
        st.rerun()
    
    st.markdown("---")
    
    # PAGINACIÓN
    st.subheader("📋 Datos")
    
    # Configuración de paginación
    REGISTROS_POR_PAGINA = 100
    
    # Contar total con filtros
    total_filtrado = db.contar_documentos(filtro=filtro_mongo if filtro_mongo else None)
    
    if total_filtrado > 0:
        # Calcular número de páginas
        total_paginas = (total_filtrado + REGISTROS_POR_PAGINA - 1) // REGISTROS_POR_PAGINA
        
        # Selector de página
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            st.info(f"📊 Mostrando {total_filtrado:,} registros en total")
        
        with col2:
            pagina = st.number_input(
                f"Página (1-{total_paginas})",
                min_value=1,
                max_value=total_paginas,
                value=1,
                step=1
            )
        
        with col3:
            st.info(f"📄 Página {pagina} de {total_paginas}")
        
        # Calcular offset para la paginación
        offset = (pagina - 1) * REGISTROS_POR_PAGINA
        
        # Obtener datos con paginación (simulada)
        # MongoDB no tiene offset directo, así que obtenemos más datos y los cortamos
        datos_pagina = db.consultar_datos(
            filtro=filtro_mongo if filtro_mongo else None,
            limite=offset + REGISTROS_POR_PAGINA
        )
        
        # Cortar para la página actual
        datos_pagina = datos_pagina[offset:offset + REGISTROS_POR_PAGINA]
        
        if datos_pagina:
            # Convertir a DataFrame
            df = pd.DataFrame(datos_pagina)
            
            # Eliminar campos técnicos de MongoDB
            columnas_ocultar = ['_id', '_fecha_insercion']
            df_mostrar = df.drop(columns=[col for col in columnas_ocultar if col in df.columns], errors='ignore')
            
            # Mostrar tabla
            st.dataframe(df_mostrar, width='stretch', height=500)
            
            # Información de la página actual
            inicio = offset + 1
            fin = min(offset + len(datos_pagina), total_filtrado)
            st.caption(f"Mostrando registros {inicio:,} - {fin:,} de {total_filtrado:,}")
            
            # NAVEGACIÓN ENTRE PÁGINAS
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
 
# Desconectar
db.desconectar()

st.markdown("---")
st.caption("💾 Datos almacenados en MongoDB Atlas")