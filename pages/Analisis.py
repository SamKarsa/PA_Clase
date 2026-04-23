import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_white"

st.title("📊 Análisis de Extranjeros en Colombia")

URL = "https://www.datos.gov.co/resource/96sh-4v8d.json?$limit=100000"

@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_json(URL)
        return df, None
    except Exception as e:
        return None, str(e)

with st.spinner("Cargando datos..."):
    df, error = load_data()

if error or df is None:
    st.error(f"❌ No se pudieron cargar los datos: {error}")
    st.stop()

# ---------------- LIMPIEZA ----------------
df.columns = df.columns.str.lower()

if "a_o" in df.columns:
    df.rename(columns={"a_o": "anio"}, inplace=True)

if "país_de_procedencia" in df.columns:
    df.rename(columns={"país_de_procedencia": "nacionalidad"}, inplace=True)

for col in ["anio", "total", "femenino", "masculino"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

meses_map = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

df["mes_num"] = df["mes"].map(meses_map)
df["fecha"] = pd.to_datetime(
    df["anio"].astype(str) + "-" + df["mes_num"].astype(str) + "-01",
    errors="coerce"
)
df = df.dropna(subset=["fecha", "total"])

# ---------------- MAPA: nombres en español → ISO alpha-3 ----------------
PAIS_ISO = {
    "Venezuela": "VEN", "Estados Unidos": "USA", "Ecuador": "ECU",
    "Perú": "PER", "Argentina": "ARG", "Brasil": "BRA", "Chile": "CHI",
    "México": "MEX", "Bolivia": "BOL", "Cuba": "CUB", "Haití": "HTI",
    "España": "ESP", "Francia": "FRA", "Alemania": "DEU", "Italia": "ITA",
    "Reino Unido": "GBR", "China": "CHN", "Corea del Sur": "KOR",
    "Japón": "JPN", "India": "IND", "Canadá": "CAN", "Australia": "AUS",
    "Panamá": "PAN", "Costa Rica": "CRI", "Guatemala": "GTM",
    "Honduras": "HND", "El Salvador": "SLV", "Nicaragua": "NIC",
    "Uruguay": "URY", "Paraguay": "PRY", "Turquía": "TUR",
    "Rusia": "RUS", "Ucrania": "UKR", "Polonia": "POL",
    "Portugal": "PRT", "Países Bajos": "NLD", "Bélgica": "BEL",
    "Suiza": "CHE", "Suecia": "SWE", "Noruega": "NOR", "Dinamarca": "DNK",
    "Israel": "ISR", "Líbano": "LBN", "Siria": "SYR", "Irán": "IRN",
    "Sudáfrica": "ZAF", "Nigeria": "NGA", "Egipto": "EGY",
    "Marruecos": "MAR", "Senegal": "SEN", "República Dominicana": "DOM",
    "Jamaica": "JAM", "Trinidad y Tobago": "TTO", "Bahamas": "BHS",
}

# ---------------- FILTROS ----------------
st.sidebar.header("🔎 Filtros")

filtered_df = df.copy()

years = sorted(df["anio"].dropna().unique())
selected_year = st.sidebar.multiselect("Año", years, default=years)
filtered_df = filtered_df[filtered_df["anio"].isin(selected_year)]

countries = sorted(df["nacionalidad"].dropna().unique())
selected_country = st.sidebar.multiselect("Nacionalidad", countries)
if selected_country:
    filtered_df = filtered_df[filtered_df["nacionalidad"].isin(selected_country)]

if filtered_df.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados.")
    st.stop()

# ---------------- KPIs ----------------
st.subheader("📌 Indicadores")

col1, col2, col3 = st.columns(3)

total = int(filtered_df["total"].sum())

por_pais = filtered_df.groupby("nacionalidad")["total"].sum()
top_country = por_pais.idxmax() if not por_pais.empty else "N/A"

por_anio = filtered_df.groupby("anio")["total"].sum()
top_year = int(por_anio.idxmax()) if not por_anio.empty else "N/A"

col1.metric("Total", f"{total:,}")
col2.metric("País principal", top_country)
col3.metric("Año top", top_year)

# ---------------- GRÁFICOS ----------------
color = "#1f77b4"

# Fila 1: Tendencia + Género
col_izq, col_der = st.columns([3, 2])

with col_izq:
    st.subheader("📈 Tendencia en el tiempo")
    trend = filtered_df.groupby("fecha")["total"].sum().reset_index()
    fig1 = px.line(trend, x="fecha", y="total", markers=True, title="Evolución mensual")
    fig1.update_traces(line=dict(width=3, color=color))
    st.plotly_chart(fig1, width='stretch')
    max_row = trend.loc[trend["total"].idxmax()]
    st.markdown(f"📌 El mayor flujo fue en **{max_row['fecha'].strftime('%Y-%m')}** con **{int(max_row['total']):,} entradas**.")

with col_der:
    st.subheader("🧍 Distribución por género")
    genero_df = pd.DataFrame({
        "genero": ["Femenino", "Masculino"],
        "total": [filtered_df["femenino"].sum(), filtered_df["masculino"].sum()]
    })
    fig3 = px.pie(genero_df, names="genero", values="total", hole=0.4, title="Distribución por género")
    st.plotly_chart(fig3, width='stretch')
    mayor = genero_df.loc[genero_df["total"].idxmax()]
    st.markdown(f"📌 Predomina el género **{mayor['genero']}**.")

# Fila 2: Top nacionalidades + Estacionalidad
col_izq2, col_der2 = st.columns([2, 3])

# 🔽 Top nacionalidades
st.subheader("🌎 Top nacionalidades")
top = (
    filtered_df.groupby("nacionalidad")["total"]
    .sum().sort_values().tail(10).reset_index()
)

fig2 = px.bar(
    top,
    x="total",
    y="nacionalidad",
    orientation="h",
    text="total",
    title="Top 10 países"
)
fig2.update_traces(marker_color=color)
st.plotly_chart(fig2, width='stretch')

top1 = top.iloc[-1]
st.markdown(f"📌 **{top1['nacionalidad']}** lidera con **{int(top1['total']):,} entradas**.")


# 🔽 Estacionalidad
st.subheader("🔥 Estacionalidad")
heat = filtered_df.pivot_table(
    values="total",
    index="anio",
    columns="mes_num",
    aggfunc="sum"
)

heat.columns = [list(meses_map.keys())[m - 1] for m in heat.columns]

fig4 = px.imshow(
    heat,
    aspect="auto",
    color_continuous_scale="Blues",
    title="Patrón estacional"
)

st.plotly_chart(fig4, width='stretch')
st.markdown("📌 Se observan patrones repetitivos en ciertos meses, indicando estacionalidad.")
# Fila 3: Mapa
st.subheader("🌍 Mapa de entradas")

map_df = filtered_df.groupby("nacionalidad")["total"].sum().reset_index()
map_df["iso"] = map_df["nacionalidad"].map(PAIS_ISO)
map_df_valido = map_df.dropna(subset=["iso"])

if map_df_valido.empty:
    st.info("ℹ️ No hay países reconocidos en el mapa para los filtros actuales.")
else:
    fig5 = px.choropleth(
        map_df_valido,
        locations="iso",
        locationmode="ISO-3",
        color="total",
        hover_name="nacionalidad",
        color_continuous_scale="Blues",
        title="Distribución global"
    )
    st.plotly_chart(fig5, width='stretch')
    st.markdown(f"📌 Flujo total: **{int(map_df['total'].sum()):,} registros** ({len(map_df_valido)} países en mapa).")
