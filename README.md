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

# Análisis de Extranjeros en Colombia

Este proyecto presenta un análisis exploratorio de los flujos de entrada de extranjeros a Colombia a lo largo del tiempo, destacando tendencias, nacionalidades predominantes, distribución demográfica y patrones estacionales.

## Indicadores principales

- **Total de registros:** 22,178,592 entradas de extranjeros  
- **País de origen principal:** Venezuela (República Bolivariana de)  
- **Año con mayor flujo:** 2018  

Estos indicadores muestran una alta concentración de entradas en un periodo reciente, con un claro protagonismo de un país en particular.

## Tendencia en el tiempo

El análisis de la evolución mensual evidencia:

- Un crecimiento sostenido desde 2012 hasta aproximadamente 2018  
- A partir de 2016, el crecimiento se vuelve más acelerado  
- Picos importantes entre 2017 y 2019, con valores cercanos a 400 mil entradas mensuales  
- Una caída abrupta hacia 2020, posiblemente asociada a factores externos como restricciones globales de movilidad  

En general, la tendencia refleja un aumento significativo en la llegada de extranjeros durante la segunda mitad de la década analizada.

## Distribución por género

- **Masculino:** 58.4%  
- **Femenino:** 41.6%  

Existe una mayor proporción de hombres en los registros, aunque la participación femenina es considerable, lo que sugiere flujos relativamente equilibrados.

## Top nacionalidades

Las 10 principales nacionalidades concentran una parte significativa del total de entradas:

1. Venezuela (4,764,555)  
2. Estados Unidos (3,880,997)  
3. Argentina (1,246,447)  
4. Brasil (1,218,000)  
5. Ecuador (1,197,080)  
6. México (1,179,849)  
7. Perú (1,084,793)  
8. España (964,782)  
9. Chile (936,029)  
10. Panamá (581,231)  

**Hallazgos clave:**

- Venezuela lidera ampliamente, superando por gran margen al resto de países  
- Predominan países de América Latina, lo que evidencia una fuerte dinámica regional  
- Estados Unidos destaca como principal origen extrarregional  

## Estacionalidad

El análisis por meses y años muestra patrones repetitivos que indican la presencia de estacionalidad:

- Incrementos frecuentes a mitad de año (junio a agosto)  
- Aumentos adicionales en algunos casos hacia finales de año  
- Mayores volúmenes entre 2017 y 2019  
- Disminución atípica en 2020 que rompe el patrón  

Estos comportamientos sugieren que los flujos migratorios están influenciados por factores cíclicos como temporadas vacacionales o dinámicas económicas.

## Distribución global

De manera general:

- La mayoría de los visitantes provienen del continente americano  
- Existe una menor, pero relevante, participación de países europeos  

## Conclusiones

- Colombia experimentó un incremento notable en la llegada de extranjeros, especialmente entre 2016 y 2019  
- La migración está altamente concentrada en países cercanos, con Venezuela como principal origen  
- Existen patrones estacionales claros que pueden ser útiles para planificación en distintos sectores  
- Eventos globales recientes impactaron directamente la movilidad internacional, reflejado en la caída de 2020  
