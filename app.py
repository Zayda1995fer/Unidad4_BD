"""
Personalidad y Hábitos Musicales — Análisis No Supervisado (K-Means)
Carga un CSV de encuesta, filtra, calcula estadística básica (propia),
entrena K-Means, nombra los perfiles resultantes según sus rasgos
dominantes y recomienda un género musical con un cuestionario final.

El proyecto está dividido en módulos para no amontonar todo en un
solo archivo:
  - config.py       constantes compartidas
  - styles.py       CSS/HTML y utilidades visuales (tarjetas, tema Plotly, sidebar)
  - etiquetas.py     etiquetas cortas y detección de columnas especiales
  - estadistica.py  estadística descriptiva básica (implementación propia)
  - modelo.py       método del codo, guardado/formato de metadata, nombrado de clusters
  - vistas.py       una función por sección de la interfaz
  - app.py          este archivo: solo orquesta la navegación lateral

Ejecutar con: streamlit run app.py
"""

import pandas as pd
import streamlit as st

from styles import CSS, HERO, sidebar_brand
from etiquetas import obtener_etiquetas_cortas
from vistas import (
    cargar_datos, validar_dataset, mostrar_dataset, filtrar_datos, mostrar_estadisticas,
    entrenar_kmeans, mostrar_resultados, generar_resultados_si_posible,
    cargar_modelo_previo, cuestionario_recomendacion, mostrar_historial_modelos,
)

st.set_page_config(page_title="Personalidad & Música", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

SECCIONES = ["Datos", "Filtros", "Estadística", "Entrenamiento", "Resultados", "Recomendador", "Historial"]


def main():
    for clave in ["df_original", "df_filtrado", "modelo", "df_resultados", "scaler", "variables_modelo", "nombres_cluster"]:
        st.session_state.setdefault(clave, None)

    sidebar_brand()
    seccion = st.sidebar.radio("Navegación", SECCIONES, label_visibility="collapsed")

    st.markdown(HERO, unsafe_allow_html=True)

    # A diferencia de st.tabs (que renderiza todas las pestañas en cada
    # ejecución), aquí solo se dibuja la sección elegida. Por eso el
    # dataset y el filtro se guardan/leen de session_state para que
    # sigan disponibles en las demás secciones aunque no se vuelvan a
    # calcular en esta misma corrida.
    if seccion == "Datos":
        df = cargar_datos()
        if df is None:
            st.info("Sube un archivo CSV para comenzar.")
        elif not validar_dataset(df):
            st.session_state.df_original = None
        else:
            mostrar_dataset(df)
    df = st.session_state.df_original

    if df is not None:
        etiquetas = obtener_etiquetas_cortas(df.columns.tolist())
    elif st.session_state.get("variables_modelo"):
        etiquetas = obtener_etiquetas_cortas(st.session_state.variables_modelo)
    else:
        etiquetas = {}

    if seccion == "Filtros":
        if df is None:
            st.info("Carga primero un archivo CSV válido en la sección **Datos**.")
        else:
            st.session_state.df_filtrado = filtrar_datos(df)
    # Fuera de la sección Filtros, se reutiliza el último filtro guardado;
    # si nunca se filtró, se usa el dataset completo por defecto.
    df_f = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else df
    num_cols = [c for c in df_f.columns if pd.api.types.is_numeric_dtype(df_f[c])] if df_f is not None else []

    if seccion == "Estadística":
        if df_f is None:
            st.info("Carga primero un archivo CSV válido en la sección **Datos**.")
        else:
            mostrar_estadisticas(df_f, num_cols, etiquetas)

    if seccion == "Entrenamiento":
        if df_f is None:
            st.info("Carga primero un archivo CSV válido en la sección **Datos**.")
        else:
            entrenar_kmeans(df_f, num_cols)

    if seccion == "Resultados":
        cargar_modelo_previo()
        if df_f is not None:
            generar_resultados_si_posible(df_f)
        mostrar_resultados(etiquetas)

    # El recomendador también funciona sin dataset: usa rangos
    # genéricos (1-5) mientras no haya datos reales cargados.
    if seccion == "Recomendador":
        cuestionario_recomendacion(df_f, etiquetas)

    if seccion == "Historial":
        mostrar_historial_modelos()


if __name__ == "__main__":
    main()
