import streamlit as st
import pandas as pd
from api_client import APIClient
from database import DatabaseClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Header
st.title("📡 Sincronización con API de Datos Abiertos")
st.markdown("### Entradas de Extranjeros a Colombia")
st.markdown("---")

# Mostrar configuración
st.subheader("⚙️ Configuración")
col1, col2 = st.columns(2)
 
with col1:
    api_url = os.getenv("API_URL", "https://www.datos.gov.co/resource/96sh-4v8d.json")
    st.text_input("URL de la API:", value=api_url, disabled=True)
 
with col2:
    db_name = os.getenv("DATABASE_NAME", "datos_colombia")
    collection_name = os.getenv("DATABASE_COLLECTION", "entradas_extranjeros")
    st.text_input("Colección MongoDB:", value=f"{db_name}.{collection_name}", disabled=True)
st.markdown("---")

# Botones de acción
col1, col2, col3 = st.columns([1, 1, 2])
 
with col1:
    btn_sincronizar = st.button("🔄 Sincronizar Ahora", type="primary", width='stretch')
 
with col2:
    btn_vista_previa = st.button("👁️ Vista Previa", width='stretch')
st.markdown("---")


# VISTA PREVIA (solo 10 registros)
if btn_vista_previa:
    with st.spinner("📡 Obteniendo vista previa de la API..."):
        api = APIClient()
        datos = api.consultar(limite=10)
        
        if datos:
            st.success(f"Vista previa obtenida: {len(datos)} registros")
             
            df = pd.DataFrame(datos)
            
            st.subheader("Preview de datos")
            st.dataframe(df, width='stretch', height=400)
            
            st.info(f"Mostrando solo 10 registros. La sincronización completa traerá ~173,000 registros.")
        else:
            st.error("No se pudo obtener la vista previa")


# SINCRONIZACIÓN COMPLETA
if btn_sincronizar:
    st.subheader("Proceso de Sincronización")
    
    # Advertencia
    st.warning("**Atención:** Este proceso eliminará todos los datos existentes y los reemplazará con los datos actuales de la API.")
    
    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # PASO 1: Obtener datos de la API
    status_text.text("Paso 1/4: Conectando a la API de Datos Abiertos...")
    progress_bar.progress(25)
    
    api = APIClient()
    datos_api = api.consultar(limite=500000)  # Obtener todos los datos disponibles
    
    if not datos_api:
        st.error("Error: No se pudieron obtener datos de la API")
        st.stop()
    
    status_text.text(f"Paso 1/4: {len(datos_api):,} registros obtenidos de la API")
    progress_bar.progress(50)
    
    # PASO 2: Conectar a MongoDB
    status_text.text("Paso 2/4: Conectando a MongoDB Atlas...")
    
    db = DatabaseClient()
    if not db.conectar():
        st.error("Error: No se pudo conectar con MongoDB")
        st.stop()
    
    status_text.text("Paso 2/4: Conectado a MongoDB exitosamente")
    progress_bar.progress(60)
    
    # PASO 3: Limpiar colección (borrar datos antiguos)
    status_text.text("Paso 3/4: Limpiando datos antiguos de MongoDB...")
    
    eliminados = db.limpiar_coleccion()
    
    status_text.text(f"Paso 3/4: {eliminados:,} registros antiguos eliminados")
    progress_bar.progress(75)
    
    # PASO 4: Insertar todos los datos nuevos
    status_text.text(f"Paso 4/4: Insertando {len(datos_api):,} registros en MongoDB...")
    
    cantidad_insertada = db.insertar_datos(datos_api)
    
    if cantidad_insertada > 0:
        progress_bar.progress(100)
        status_text.text(f"Sincronización completada: {cantidad_insertada:,} registros en MongoDB")
        
        # Mensaje de éxito
        st.success("🎉 ¡Sincronización completada exitosamente!")
        
        # Métricas del proceso
        st.subheader("Resumen de la Sincronización")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Obtenidos de API", f"{len(datos_api):,}")
        with col2:
            st.metric("Eliminados", f"{eliminados:,}")
        with col3:
            st.metric("Insertados", f"{cantidad_insertada:,}")
        
        # Preview de datos insertados
        st.subheader("Preview de datos sincronizados")
        df_preview = pd.DataFrame(datos_api[:20])
        st.dataframe(df_preview, width='stretch', height=400)
        
        # Información adicional
        st.info(f"""
                **Información de los datos:**
                - Total de registros: {len(datos_api):,}
                - Años disponibles: {', '.join(sorted(set(d.get('a_o', '') for d in datos_api[:100])))}
                - Última actualización: Ahora
                """)
        
    else:
        st.error("Error: No se pudieron insertar los datos en MongoDB")
    
    # Desconectar de MongoDB
    db.desconectar()
st.markdown("---")

# Tips
col1, col2 = st.columns(2)
 
with col1:
    st.info("💡 **Tip**: Usa 'Vista Previa' para verificar que la API funciona antes de sincronizar.")
 
with col2:
    st.success("**Recomendación**: Sincroniza los datos una vez al inicio, luego consulta desde MongoDB.")

st.markdown("""
### ⏰ Sincronización Automática

Además del botón manual, el sistema también sincroniza automáticamente cada **8 horas**.

- **Manual**: Usa el botón "Sincronizar Ahora"
- **Automática**: Se ejecuta cada 8 horas en segundo plano
- **Estado**: Verifica en la página Home

La sincronización automática funciona mientras la aplicación esté corriendo.
""")