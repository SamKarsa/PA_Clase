import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from api_client import APIClient
from database import DatabaseClient

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Datos Abiertos Colombia → MongoDB",
    page_icon="🇨🇴",
    layout="wide"
)

# Título principal
st.title("🇨🇴 Datos Abiertos Colombia → MongoDB")
st.markdown("---")

# ============================================
# SIDEBAR - Configuración
# ============================================
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # URL de la API
    st.subheader("1. API de Datos Abiertos")
    api_url = st.text_input(
        "URL del dataset:",
        value=os.getenv("API_URL", "https://www.datos.gov.co/resource/46yq-tz63.json"),
        help="Pega aquí la URL del dataset de datos.gov.co"
    )
    
    limite_registros = st.slider(
        "Límite de registros:",
        min_value=10,
        max_value=1000,
        value=100,
        step=10
    )
    
    st.markdown("---")
    
    # Configuración de MongoDB
    st.subheader("2. MongoDB Atlas")
    
    # Mostrar si las variables están configuradas
    mongo_user = os.getenv("MONGO_USER")
    mongo_host = os.getenv("MONGO_HOST")
    db_name = os.getenv("DATABASE_NAME", "datos_colombia")
    collection_name = os.getenv("DATABSE_COLLECTION", "datos_abiertos")
    
    if mongo_user and mongo_host:
        st.success("✅ Credenciales de MongoDB configuradas")
        st.text(f"Usuario: {mongo_user}")
        st.text(f"Host: {mongo_host}")
    else:
        st.error("❌ Faltan credenciales de MongoDB en .env")


    
# ============================================
# INTERFAZ PRINCIPAL
# ============================================
# Botones de acción
col1, col2 = st.columns(2)

with col1:
    btn_obtener = st.button(
        "📥 Obtener Datos de la API",
        type="primary",
        use_container_width=True
    )

with col2:
    btn_guardar = st.button(
        "💾 Guardar en MongoDB",
        type="secondary",
        use_container_width=True,
        disabled='datos' not in st.session_state
    )

# ============================================
# OBTENER DATOS DE LA API
# ============================================
if btn_obtener:
    if not api_url:
        st.warning("⚠️ Por favor ingresa la URL de la API")
    else:
        with st.spinner("📡 Obteniendo datos de la API..."):
            # Crear cliente de API
            api = APIClient(url=api_url)
            
            # Consultar datos
            datos = api.consultar(limite=limite_registros)
            
            if datos:
                # Guardar en session_state
                st.session_state['datos'] = datos
                st.session_state['df'] = pd.DataFrame(datos)
                
                st.success(f"✅ Se obtuvieron {len(datos)} registros exitosamente")
            else:
                st.error("❌ No se pudieron obtener datos de la API")

# ============================================
# VISUALIZAR DATOS
# ============================================
if 'datos' in st.session_state and st.session_state['datos']:
    st.markdown("---")
    st.header("📊 Visualización de Datos")
    
    df = st.session_state['df']
    
    # Tabs para diferentes visualizaciones
    tab1, tab2, tab3 = st.tabs(["📋 Tabla", "📈 Información", "🔍 JSON"])
    
    with tab1:
        st.subheader("Datos en formato tabla")
        st.dataframe(df, use_container_width=True, height=400)
        
        # Botón de descarga CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"datos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.subheader("Información del Dataset")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de registros", len(df))
        with col2:
            st.metric("Total de columnas", len(df.columns))
        with col3:
            memoria_kb = df.memory_usage(deep=True).sum() / 1024
            st.metric("Memoria (KB)", f"{memoria_kb:.2f}")
        
        st.subheader("Columnas disponibles")
        st.write(list(df.columns))
        
        st.subheader("Tipos de datos")
        st.write(df.dtypes)
        
        st.subheader("Primeros 5 registros")
        st.write(df.head())
    
    with tab3:
        st.subheader("Datos en formato JSON")
        st.json(st.session_state['datos'][:3])  # Mostrar solo 3 para no saturar

# ============================================
# GUARDAR EN MONGODB
# ============================================
if btn_guardar:
    if 'datos' not in st.session_state:
        st.warning("⚠️ Primero debes obtener datos de la API")
    else:
        with st.spinner("💾 Guardando en MongoDB..."):
            try:
                # Crear cliente de base de datos
                db = DatabaseClient()
                
                # Conectar
                if db.conectar():
                    # Insertar datos
                    cantidad = db.insertar_datos(st.session_state['datos'])
                    
                    if cantidad > 0:
                        st.success(f"✅ Se guardaron {cantidad} documentos en MongoDB")
                        
                        # Mostrar total en la base de datos
                        total = db.contar_documentos()
                        st.info(f"📊 Total de documentos en la colección: {total}")
                    else:
                        st.error("❌ No se pudieron guardar los datos")
                    
                    # Desconectar
                    db.desconectar()
                else:
                    st.error("❌ No se pudo conectar a MongoDB. Verifica tu .env")
                    
            except ValueError as e:
                st.error(f"❌ {str(e)}")
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit, Python y MongoDB")