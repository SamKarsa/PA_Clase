# 🇨🇴 Sistema de Análisis de Entradas de Extranjeros a Colombia

Aplicación web interactiva construida con **Streamlit** que sincroniza, almacena y visualiza datos de entradas de extranjeros a Colombia desde la API de Datos Abiertos del gobierno colombiano.

## Características

- 📡 **Sincronización con API** — consume el dataset público de Datos Abiertos Colombia
- 💾 **Almacenamiento en MongoDB Atlas** — persiste los datos con soporte de filtros y paginación eficiente
- 📊 **Análisis interactivo** — gráficas de tendencia, nacionalidades, género, estacionalidad y mapa mundial
- ⏰ **Sincronización automática** — scheduler en segundo plano cada 8 horas

## Tecnologías

| Capa          | Tecnología                        |
| ------------- | --------------------------------- |
| Frontend      | Streamlit 1.56                    |
| Base de datos | MongoDB Atlas (pymongo)           |
| Visualización | Plotly                            |
| API fuente    | Datos Abiertos Colombia (Socrata) |
| Scheduler     | APScheduler                       |
| Lenguaje      | Python 3.12                       |

## Dataset

- **Fuente:** [datos.gov.co](https://www.datos.gov.co/resource/96sh-4v8d.json)
- **Contenido:** Entradas de extranjeros a Colombia discriminadas por nacionalidad, género y periodo
- **Cobertura:** 2012 – 2024 (~173,000 registros)

## Instalación local

### 1. Clonar el repositorio

```bash
git clone <https://github.com/SamKarsa/PA_Clase.git>
cd PA_Clase
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Mongo configuration
MONGO_USER=your_mongo_user
MONGO_PASSWORD=your_mongo_password
MONGO_HOST=your_mongo_host
DATABASE_NAME=migracion_colombia
DATABASE_COLLECTION=entradas_extranjeros

# API configuration
API_URL=https://www.datos.gov.co/resource/96sh-4v8d.json
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

## Estructura del proyecto

```
PA_Clase/
├── app.py                  # Punto de entrada, navegación y scheduler
├── api_client.py           # Cliente HTTP para la API de Datos Abiertos
├── database.py             # Cliente MongoDB (conexión, consultas, inserción)
├── sincronizador_auto.py   # Scheduler de sincronización automática
├── pages/
│   ├── Inicio.py           # Dashboard de estado del sistema
│   ├── API.py              # Sincronización manual con la API
│   ├── MongoDB.py          # Consulta y filtrado de datos almacenados
│   └── Analisis.py         # Gráficas y análisis estadístico
├── .streamlit/
│   └── config.toml         # Configuración del servidor Streamlit
├── requirements.txt
└── .env                    # Variables de entorno (no subir al repo)
```

## Páginas

### 🏠 Inicio

Estado general del sistema: conexión a MongoDB, total de registros y estado del scheduler automático.

### 📡 Sincronización API

Permite obtener una vista previa de 10 registros o ejecutar una sincronización completa que reemplaza todos los datos en MongoDB.

### 💾 Base de Datos

Consulta paginada (100 registros por página) con filtros por año, nacionalidad y mes. Carga optimizada mediante `distinct()` sin traer todos los documentos.

### 📊 Análisis

Visualizaciones interactivas con filtros por año y nacionalidad:

- Tendencia mensual (línea)
- Top 10 nacionalidades (barras)
- Distribución por género (donut)
- Estacionalidad por mes/año (heatmap)
- Distribución geográfica mundial (mapa choropleth)
