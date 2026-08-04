"""
Personalidad y Hábitos Musicales — Análisis No Supervisado (K-Means)
Carga un CSV de encuesta, filtra, calcula estadística básica (propia),
entrena K-Means, nombra los perfiles resultantes según sus rasgos
dominantes y recomienda un género musical con un cuestionario final.

El proyecto está dividido en módulos para no amontonar todo en un
solo archivo:
  - config.py       constantes compartidas
  - styles.py       CSS/HTML y utilidades visuales (tarjetas, tema Plotly)
  - etiquetas.py     etiquetas cortas y detección de columnas especiales
  - estadistica.py  estadística descriptiva básica (implementación propia)
  - modelo.py       método del codo, guardado/formato de metadata, nombrado de clusters
  - vistas.py       una función por sección/pestaña de la interfaz
  - app.py          este archivo: solo orquesta las pestañas

Ejecutar con: streamlit run app.py
"""

import pandas as pd
import streamlit as st

from styles import CSS, HERO
from etiquetas import obtener_etiquetas_cortas
from vistas import (
    cargar_datos, validar_dataset, mostrar_dataset, filtrar_datos, mostrar_estadisticas,
    entrenar_kmeans, mostrar_resultados, generar_resultados_si_posible,
    cargar_modelo_previo, cuestionario_recomendacion,
)

st.set_page_config(page_title="Personalidad & Música", page_icon="🎼", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


def main():
    for clave in ["df_original", "df_filtrado", "modelo", "df_resultados", "scaler", "variables_modelo", "nombres_cluster"]:
        st.session_state.setdefault(clave, None)

    st.markdown(HERO, unsafe_allow_html=True)

    tab_datos, tab_filtros, tab_stats, tab_train, tab_res, tab_quiz = st.tabs(
        ["📂 Datos", "🔍 Filtros", "📊 Estadística", "🤖 Entrenamiento", "📈 Resultados", "🎯 Recomendador"]
    )

    with tab_datos:
        df = cargar_datos()
        if df is None:
            st.info("👆 Sube un archivo CSV para comenzar.")
        elif not validar_dataset(df):
            df = None
        else:
            mostrar_dataset(df)

    # El modelo se carga aquí (antes de calcular las etiquetas) para que,
    # si actualiza las características en el estado de sesión, el resto
    # de la app (incluido el cuestionario) ya las vea actualizadas en
    # esta misma ejecución. El expander sigue apareciendo visualmente
    # dentro de la pestaña Resultados.
    with tab_res:
        cargar_modelo_previo()

    if df is not None:
        etiquetas = obtener_etiquetas_cortas(df.columns.tolist())
    elif st.session_state.get("variables_modelo"):
        etiquetas = obtener_etiquetas_cortas(st.session_state.variables_modelo)
    else:
        etiquetas = {}

    df_f = None
    with tab_filtros:
        if df is None:
            st.info("Carga primero un archivo CSV válido en la pestaña **Datos**.")
        else:
            df_f = filtrar_datos(df)
            st.session_state.df_filtrado = df_f

    num_cols = [c for c in df_f.columns if pd.api.types.is_numeric_dtype(df_f[c])] if df_f is not None else []

    with tab_stats:
        if df_f is None:
            st.info("Carga primero un archivo CSV válido en la pestaña **Datos**.")
        else:
            mostrar_estadisticas(df_f, num_cols, etiquetas)

    with tab_train:
        if df_f is None:
            st.info("Carga primero un archivo CSV válido en la pestaña **Datos**.")
        else:
            entrenar_kmeans(df_f, num_cols)

    # Se vuelve a entrar a la pestaña de Resultados para añadir la
    # sección de resultados debajo del expander de carga de modelo.
    with tab_res:
        if df_f is not None:
            generar_resultados_si_posible(df_f)
        mostrar_resultados(etiquetas)

    # La pestaña de Recomendador también funciona sin dataset: usa
    # rangos genéricos (1-5) mientras no haya datos reales cargados.
    with tab_quiz:
        cuestionario_recomendacion(df_f, etiquetas)


if __name__ == "__main__":
    main()