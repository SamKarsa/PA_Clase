import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_white"

st.title("📊 Análisis de Extranjeros en Colombia")

URL = "https://www.datos.gov.co/resource/96sh-4v8d.json?$limit=100000"

@st.cache_data
def load_data():
    return pd.read_json(URL)

df = load_data()

# ---------------- LIMPIEZA ----------------
df.columns = df.columns.str.lower()

# Renombrar columnas
if "a_o" in df.columns:
    df.rename(columns={"a_o": "anio"}, inplace=True)

if "país_de_procedencia" in df.columns:
    df.rename(columns={"país_de_procedencia": "nacionalidad"}, inplace=True)

# ---------------- TIPOS DE DATOS ----------------
for col in ["anio", "total", "femenino", "masculino"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------------- MESES ----------------
meses_map = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

df["mes_num"] = df["mes"].map(meses_map)

# Crear fecha correcta
df["fecha"] = pd.to_datetime(
    df["anio"].astype(str) + "-" + df["mes_num"].astype(str) + "-01",
    errors="coerce"
)

df = df.dropna(subset=["fecha", "total"])

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

# ---------------- KPIs ----------------
st.subheader("📌 Indicadores")

col1, col2, col3 = st.columns(3)

total = int(filtered_df["total"].sum())

top_country = filtered_df.groupby("nacionalidad")["total"].sum().idxmax()
top_year = filtered_df.groupby("anio")["total"].sum().idxmax()

col1.metric("Total", f"{total:,}")
col2.metric("País principal", top_country)
col3.metric("Año top", top_year)

# ---------------- GRÁFICOS ----------------
color = "#1f77b4"

# 📈 Tendencia
st.subheader("📈 Tendencia en el tiempo")

trend = filtered_df.groupby("fecha")["total"].sum().reset_index()

fig1 = px.line(
    trend, x="fecha", y="total",
    markers=True, title="Evolución mensual",
)

fig1.update_traces(line=dict(width=3, color=color))
st.plotly_chart(fig1, use_container_width=True)

max_row = trend.loc[trend["total"].idxmax()]
st.markdown(f"📌 **Conclusión:** El mayor flujo se presentó en **{max_row['fecha'].strftime('%Y-%m')}** con **{int(max_row['total']):,} entradas**, evidenciando un pico migratorio claro.")

# 🌎 Top nacionalidades
st.subheader("🌎 Top nacionalidades")

top = (
    filtered_df.groupby("nacionalidad")["total"]
    .sum().sort_values().tail(10).reset_index()
)

fig2 = px.bar(
    top, x="total", y="nacionalidad",
    orientation="h", text="total",
    title="Top 10 países"
)

fig2.update_traces(marker_color=color)
st.plotly_chart(fig2, use_container_width=True)

top1 = top.iloc[-1]
st.markdown(f"📌 **Conclusión:** **{top1['nacionalidad']}** lidera el ranking con **{int(top1['total']):,} entradas**, concentrando gran parte del flujo migratorio.")

# 🧍 Género (CORREGIDO)
st.subheader("🧍 Distribución por género")

genero_df = pd.DataFrame({
    "genero": ["Femenino", "Masculino"],
    "total": [
        filtered_df["femenino"].sum(),
        filtered_df["masculino"].sum()
    ]
})

fig3 = px.pie(
    genero_df,
    names="genero",
    values="total",
    hole=0.4,
    title="Distribución por género"
)

st.plotly_chart(fig3, use_container_width=True)

mayor = genero_df.loc[genero_df["total"].idxmax()]
st.markdown(f"📌 **Conclusión:** Predomina el género **{mayor['genero']}**, lo que sugiere una ligera concentración demográfica en este grupo.")

# 🔥 Estacionalidad
st.subheader("🔥 Estacionalidad")

heat = filtered_df.pivot_table(
    values="total",
    index="anio",
    columns="mes_num",
    aggfunc="sum"
)

fig4 = px.imshow(
    heat,
    aspect="auto",
    color_continuous_scale="Blues",
    title="Patrón estacional"
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("📌 **Conclusión:** Se observan patrones repetitivos en ciertos meses, lo que indica estacionalidad en las entradas al país.")

# 🌍 Mapa
st.subheader("🌍 Mapa de entradas")

map_df = filtered_df.groupby("nacionalidad")["total"].sum().reset_index()

fig5 = px.choropleth(
    map_df,
    locations="nacionalidad",
    locationmode="country names",
    color="total",
    color_continuous_scale="Blues",
    title="Distribución global"
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown(f"📌 **Conclusión:** El flujo migratorio alcanza un total de **{int(map_df['total'].sum()):,} registros**, con alta concentración en regiones específicas.")