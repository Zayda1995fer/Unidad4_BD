"""
Personalidad y Hábitos Musicales — Análisis No Supervisado (K-Means)
Carga un CSV de encuesta, filtra, calcula estadística básica (propia),
entrena K-Means, nombra los perfiles resultantes según sus rasgos
dominantes y recomienda un género musical con un cuestionario final.

El proyecto está dividido en módulos para no amontonar todo en un
solo archivo:
  - config.py       constantes compartidas
  - styles.py       CSS/HTML y utilidades visuales (tarjetas, tema Plotly)
  - etiquetas.py     etiquetas cortas, filtros derivados y detección de columnas
  - estadistica.py  estadística descriptiva básica (implementación propia)
  - modelo.py       método del codo, guardado/formato de metadata, nombrado de clusters
  - vistas.py       una función por sección de la interfaz
  - app.py          este archivo: solo orquesta la navegación

La navegación es una fila de pestañas horizontales (no una barra
lateral) controlada por `st.session_state`, para poder avanzar con un
botón "Siguiente" al final de cada sección sin depender de que la
persona haga clic manualmente arriba.

Ejecutar con: streamlit run app.py
"""

import pandas as pd
import streamlit as st

from config import SECCIONES
from styles import CSS, HERO, icono
from etiquetas import obtener_etiquetas_cortas
from vistas import (
    cargar_datos, validar_dataset, mostrar_dataset, filtrar_datos, mostrar_estadisticas,
    entrenar_kmeans, mostrar_resultados, generar_resultados_si_posible,
    cargar_modelo_previo, cuestionario_recomendacion, mostrar_historial_modelos,
)

st.set_page_config(page_title="Personalidad & Música", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


def boton_siguiente(seccion_actual):
    """Botón al final de cada sección para avanzar a la siguiente sin
    tener que subir hasta la navegación de arriba. No se puede asignar
    directamente a session_state['seccion_actual'] porque ese widget ya
    se instanció en esta misma corrida — en vez de eso, se guarda la
    sección pendiente y se aplica al inicio de la SIGUIENTE corrida,
    antes de crear el radio."""
    idx = SECCIONES.index(seccion_actual)
    if idx < len(SECCIONES) - 1:
        st.markdown('<div class="boton-siguiente">', unsafe_allow_html=True)
        siguiente = SECCIONES[idx + 1]
        if st.button(f"Siguiente: {siguiente} →", key=f"siguiente_{seccion_actual}"):
            st.session_state.seccion_pendiente = siguiente
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def main():
    for clave in ["df_original", "df_filtrado", "modelo", "df_resultados", "scaler", "variables_modelo", "nombres_cluster"]:
        st.session_state.setdefault(clave, None)
    st.session_state.setdefault("seccion_actual", SECCIONES[0])
    if "seccion_pendiente" in st.session_state:
        st.session_state.seccion_actual = st.session_state.pop("seccion_pendiente")

    st.markdown(HERO, unsafe_allow_html=True)

    st.markdown('<div class="nav-principal">', unsafe_allow_html=True)
    seccion = st.radio("nav-principal", SECCIONES, key="seccion_actual", horizontal=True, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

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
            boton_siguiente(seccion)
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
            boton_siguiente(seccion)
    # Fuera de la sección Filtros, se reutiliza el último filtro guardado;
    # si nunca se filtró, se usa el dataset completo por defecto.
    df_f = st.session_state.df_filtrado if st.session_state.df_filtrado is not None else df
    num_cols = [c for c in df_f.columns if pd.api.types.is_numeric_dtype(df_f[c])] if df_f is not None else []

    if seccion == "Estadística":
        if df_f is None:
            st.info("Carga primero un archivo CSV válido en la sección **Datos**.")
        else:
            mostrar_estadisticas(df_f, num_cols, etiquetas)
            boton_siguiente(seccion)

    if seccion == "Entrenamiento":
        if df_f is None:
            st.info("Carga primero un archivo CSV válido en la sección **Datos**.")
        else:
            entrenar_kmeans(df_f, num_cols, etiquetas)
            boton_siguiente(seccion)

    if seccion == "Resultados":
        cargar_modelo_previo()
        if df_f is not None:
            generar_resultados_si_posible(df_f)
        mostrar_resultados(etiquetas)
        boton_siguiente(seccion)

    # El recomendador también funciona sin dataset: usa rangos
    # genéricos (1-5) mientras no haya datos reales cargados.
    if seccion == "Recomendador":
        cuestionario_recomendacion(df_f, etiquetas)
        boton_siguiente(seccion)

    if seccion == "Historial":
        mostrar_historial_modelos()


if __name__ == "__main__":
    main()
