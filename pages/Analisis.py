import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Análisis de Extranjeros en Colombia")

URL = "https://www.datos.gov.co/resource/96sh-4v8d.json"

@st.cache_data
def load_data():
    return pd.read_json(URL)

df = load_data()

# ---------------- LIMPIEZA ----------------
df.columns = df.columns.str.lower()

# Ajuste de columnas (por si cambian nombres)
if "año" in df.columns:
    df.rename(columns={"año": "anio"}, inplace=True)

if "país_de_procedencia" in df.columns:
    df.rename(columns={"país_de_procedencia": "nacionalidad"}, inplace=True)

# Convertir datos
for col in ["anio", "mes", "total"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Crear fecha
if "anio" in df.columns and "mes" in df.columns:
    df["fecha"] = pd.to_datetime(df["anio"].astype(str) + "-" + df["mes"].astype(str), errors="coerce")

# ---------------- FILTROS ----------------
st.sidebar.header("🔎 Filtros")

filtered_df = df.copy()

if "anio" in df.columns:
    years = sorted(df["anio"].dropna().unique())
    selected_year = st.sidebar.multiselect("Año", years, default=years)
    filtered_df = filtered_df[filtered_df["anio"].isin(selected_year)]

if "nacionalidad" in df.columns:
    countries = sorted(df["nacionalidad"].dropna().unique())
    selected_country = st.sidebar.multiselect("Nacionalidad", countries)
    if selected_country:
        filtered_df = filtered_df[filtered_df["nacionalidad"].isin(selected_country)]

if "genero" in df.columns:
    genders = df["genero"].dropna().unique()
    selected_gender = st.sidebar.multiselect("Género", genders)
    if selected_gender:
        filtered_df = filtered_df[filtered_df["genero"].isin(selected_gender)]

# ---------------- KPIs ----------------
st.subheader("📌 Indicadores")

col1, col2, col3 = st.columns(3)

total = int(filtered_df["total"].sum()) if "total" in filtered_df.columns else 0

top_country = (
    filtered_df.groupby("nacionalidad")["total"].sum().idxmax()
    if "nacionalidad" in filtered_df.columns and not filtered_df.empty else "N/A"
)

top_year = (
    filtered_df.groupby("anio")["total"].sum().idxmax()
    if "anio" in filtered_df.columns and not filtered_df.empty else "N/A"
)

col1.metric("Total", f"{total:,}")
col2.metric("País principal", top_country)
col3.metric("Año top", top_year)

# ---------------- GRÁFICOS ----------------

# 📈 Tendencia
st.subheader("📈 Tendencia en el tiempo")
if "fecha" in filtered_df.columns:
    trend = filtered_df.groupby("fecha")["total"].sum().reset_index()
    fig1 = px.line(trend, x="fecha", y="total")
    st.plotly_chart(fig1, use_container_width=True)

# 🌎 Top países
st.subheader("🌎 Top nacionalidades")
if "nacionalidad" in filtered_df.columns:
    top = (
        filtered_df.groupby("nacionalidad")["total"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig2 = px.bar(top, x="total", y="nacionalidad", orientation="h")
    st.plotly_chart(fig2, use_container_width=True)

# 🧍 Género
st.subheader("🧍 Distribución por género")
if "genero" in filtered_df.columns:
    gen = filtered_df.groupby("genero")["total"].sum().reset_index()
    fig3 = px.pie(gen, names="genero", values="total")
    st.plotly_chart(fig3, use_container_width=True)

# 🔥 Heatmap
st.subheader("🔥 Estacionalidad")
if "anio" in filtered_df.columns and "mes" in filtered_df.columns:
    heat = filtered_df.pivot_table(values="total", index="anio", columns="mes", aggfunc="sum")
    fig4 = px.imshow(heat, aspect="auto")
    st.plotly_chart(fig4, use_container_width=True)

# 🌍 Mapa
st.subheader("🌍 Mapa de entradas")
if "nacionalidad" in filtered_df.columns:
    map_df = filtered_df.groupby("nacionalidad")["total"].sum().reset_index()
    fig5 = px.choropleth(
        map_df,
        locations="nacionalidad",
        locationmode="country names",
        color="total"
    )
    st.plotly_chart(fig5, use_container_width=True)