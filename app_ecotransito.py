import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Configuración de página
st.set_page_config(
    page_title="Sistema EcoTránsito CDMX",
    layout="wide"
)

st.title("Sistema EcoTránsito CDMX")

# 2. Cargar datos
from pathlib import Path

ruta = Path(__file__).resolve().parent / "cdmx_air_traffic_clean..csv"

st.write("Ruta buscada:", str(ruta))
st.write("¿Existe el archivo?", ruta.exists())
st.write("Archivos disponibles:", [p.name for p in ruta.parent.iterdir()])


df = pd.read_csv(ruta, sep=",", encoding="utf-8-sig")

if len(df.columns) == 1:
    df = df.iloc[:, 0].str.split(",", expand=True)
    df.columns = [
        "ID_Registro", "Timestamp", "Zona_Estacion",
        "Concentracion_PM25", "Nivel_NO2",
        "Indice_Trafico_Vehicular", "Estado_Sensor", "Hora_Dia"
    ]

st.write("Columnas del archivo:", df.columns.tolist())
st.write("Primeros registros:", df.head())
# 3. Barra lateral
st.sidebar.header("Filtros")

zonas = st.sidebar.multiselect(
    "Selecciona las zonas:",
    options=sorted(df["Zona_Estacion"].dropna().unique()),
    default=sorted(df["Zona_Estacion"].dropna().unique())
)

df_filtrado = df[df["Zona_Estacion"].isin(zonas)]

# 4. Panel de KPIs
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total de lecturas activas",
    len(df_filtrado)
)

col2.metric(
    "Promedio de PM2.5",
    f"{df_filtrado['Concentracion_PM25'].mean():.2f} µg/m³"
    if not df_filtrado.empty else "Sin datos"
)

col3.metric(
    "Índice máximo de tráfico",
    f"{df_filtrado['Indice_Trafico_Vehicular'].max():.2f}"
    if not df_filtrado.empty else "Sin datos"
)

# 5. Pestañas
tab1, tab2 = st.tabs([
    "Dispersión",
    "Correlación Spearman"
])

with tab1:
    st.subheader("Tráfico vehicular vs PM2.5")

    fig = px.scatter(
        df_filtrado,
        x="Indice_Trafico_Vehicular",
        y="Concentracion_PM25",
        color="Zona_Estacion",
        hover_data=["ID_Registro"],
        title="Relación entre tráfico y contaminación"
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Mapa de calor de correlación Spearman")

    numericas = df_filtrado.select_dtypes(include="number")

    if len(numericas) >= 2:
        correlacion = numericas.corr(method="spearman")

        fig2, ax = plt.subplots(figsize=(8, 5))

        sns.heatmap(
            correlacion,
            annot=True,
            cmap="coolwarm",
            fmt=".2f",
            ax=ax
        )

        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.warning("No hay suficientes datos para calcular correlaciones.")
