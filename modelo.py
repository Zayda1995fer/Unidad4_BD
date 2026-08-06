"""Entrenamiento (método del codo), guardado/formato de metadata y
nombrado automático de los clusters de K-Means."""

import os
from datetime import datetime

import joblib
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sklearn.cluster import KMeans

from config import PALETA, CARPETA_MODELOS
from styles import tema_plotly, icono
from etiquetas import ADJETIVO_POR_RASGO


def formatear_fecha(fecha_iso):
    if not fecha_iso:
        return "N/D"
    try:
        return datetime.fromisoformat(fecha_iso).strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return fecha_iso


def metodo_codo(X, k_max=10):
    k_max = max(min(k_max, X.shape[0] - 1), 2)
    inercias = [KMeans(n_clusters=k, random_state=42, n_init=10).fit(X).inertia_ for k in range(1, k_max + 1)]
    fig = go.Figure(go.Scatter(x=list(range(1, k_max + 1)), y=inercias, mode="lines+markers",
                                line=dict(color=PALETA[0], width=3), marker=dict(size=9, color=PALETA[1]),
                                fill="tozeroy", fillcolor="rgba(124,58,237,0.10)"))
    fig.update_layout(title="Método del Codo — Inercia vs. k", xaxis_title="k", yaxis_title="Inercia (WCSS)")
    st.plotly_chart(tema_plotly(fig, 360), use_container_width=True)
    st.caption("Elige k en el punto donde la curva deja de bajar bruscamente (el 'codo').")


def guardar_modelo(modelo, scaler, variables, filtros_resumen="Sin filtros aplicados",
                    n_registros=None, k=None, silhouette=None):
    """Guarda el modelo entrenado con TODA su metadata (algoritmo,
    características, fecha/hora, filtros que estaban activos al
    entrenar, número de registros usados y Silhouette Score) usando
    joblib. Cada entrenamiento genera un archivo NUEVO con marca de
    tiempo en su nombre, dentro de la carpeta `modelos_guardados/`,
    para no perder el historial de versiones anteriores."""
    os.makedirs(CARPETA_MODELOS, exist_ok=True)
    fecha = datetime.now()
    nombre_archivo = f"modelo_{fecha:%Y%m%d_%H%M%S}.pkl"
    ruta = os.path.join(CARPETA_MODELOS, nombre_archivo)

    metadata = {
        "modelo": modelo,
        "scaler": scaler,
        "variables": variables,
        "algoritmo": "K-Means",
        "fecha_entrenamiento": fecha.isoformat(),
        "filtros_aplicados": filtros_resumen,
        "n_registros": n_registros,
        "k": k if k is not None else getattr(modelo, "n_clusters", None),
        "silhouette_score": silhouette,
    }
    joblib.dump(metadata, ruta)

    st.success(f"Modelo entrenado y guardado como `{nombre_archivo}`")
    ruta_absoluta = os.path.abspath(ruta)
    st.markdown(
        f'<div class="ficha-modelo">'
        f'<div class="fila-meta">{icono("schedule", 17)}<strong>Creado:</strong>&nbsp;{fecha.strftime("%d/%m/%Y %H:%M:%S")}</div>'
        f'<div class="fila-meta">{icono("tune", 17)}<strong>Filtros activos:</strong>&nbsp;{filtros_resumen}</div>'
        f'<div class="fila-meta">{icono("folder", 17)}<strong>Guardado en:</strong></div>'
        f'<span class="ruta">{ruta_absoluta}</span>'
        f'</div>', unsafe_allow_html=True,
    )
    with open(ruta, "rb") as f:
        st.download_button("Descargar este modelo (.pkl)", f.read(), file_name=nombre_archivo, mime="application/octet-stream")
    return ruta


def listar_modelos_guardados():
    """Escanea la carpeta `modelos_guardados/` y arma una tabla con la
    metadata de cada modelo `.pkl` encontrado (fecha, filtros, k,
    registros usados, Silhouette Score y ruta completa en disco)."""
    if not os.path.isdir(CARPETA_MODELOS):
        return pd.DataFrame(), CARPETA_MODELOS
    filas = []
    for nombre in sorted(os.listdir(CARPETA_MODELOS), reverse=True):
        if not nombre.endswith(".pkl"):
            continue
        ruta = os.path.join(CARPETA_MODELOS, nombre)
        try:
            d = joblib.load(ruta)
        except Exception:
            continue
        filas.append({
            "Archivo": nombre,
            "Fecha de creación": formatear_fecha(d.get("fecha_entrenamiento")),
            "Algoritmo": d.get("algoritmo", "N/D"),
            "k (clusters)": d.get("k", "N/D"),
            "Características": len(d.get("variables") or []),
            "Registros usados": d.get("n_registros", "N/D"),
            "Filtros aplicados": d.get("filtros_aplicados", "N/D"),
            "Silhouette Score": round(d["silhouette_score"], 3) if isinstance(d.get("silhouette_score"), (int, float)) else "N/D",
            "Ruta completa": os.path.abspath(ruta),
        })
    return pd.DataFrame(filas), os.path.abspath(CARPETA_MODELOS)


def nombrar_clusters(df_res, variables, etiquetas):
    """Analiza el promedio de cada rasgo de personalidad por cluster,
    lo compara contra el promedio general (z-score) y arma un nombre
    descriptivo con los 2 rasgos más distintivos de cada grupo. Solo
    usa columnas que correspondan a rasgos reconocidos (excluye datos
    demográficos como la edad)."""
    rasgo_vars = [v for v in variables if etiquetas.get(v, v) in ADJETIVO_POR_RASGO]
    if not rasgo_vars:
        return {c: f"Cluster {c}" for c in sorted(df_res["cluster"].unique())}

    medias = {v: df_res[v].mean() for v in rasgo_vars}
    desv = {v: df_res[v].std(ddof=0) or 1.0 for v in rasgo_vars}

    nombres = {}
    for c in sorted(df_res["cluster"].unique()):
        subset = df_res[df_res["cluster"] == c]
        z = {v: (subset[v].mean() - medias[v]) / desv[v] for v in rasgo_vars}
        top = sorted(z, key=z.get, reverse=True)[:2]
        adjetivos = [ADJETIVO_POR_RASGO[etiquetas.get(v, v)] for v in top]
        nombres[c] = f"{' y '.join(dict.fromkeys(adjetivos))} (Cluster {c})"
    return nombres

    """Analiza el promedio de cada rasgo de personalidad por cluster,
    lo compara contra el promedio general (z-score) y arma un nombre
    descriptivo con los 2 rasgos más distintivos de cada grupo. Solo
    usa columnas que correspondan a rasgos reconocidos (excluye datos
    demográficos como la edad)."""
    rasgo_vars = [v for v in variables if etiquetas.get(v, v) in ADJETIVO_POR_RASGO]
    if not rasgo_vars:
        return {c: f"Cluster {c}" for c in sorted(df_res["cluster"].unique())}

    medias = {v: df_res[v].mean() for v in rasgo_vars}
    desv = {v: df_res[v].std(ddof=0) or 1.0 for v in rasgo_vars}

    nombres = {}
    for c in sorted(df_res["cluster"].unique()):
        subset = df_res[df_res["cluster"] == c]
        z = {v: (subset[v].mean() - medias[v]) / desv[v] for v in rasgo_vars}
        top = sorted(z, key=z.get, reverse=True)[:2]
        adjetivos = [ADJETIVO_POR_RASGO[etiquetas.get(v, v)] for v in top]
        nombres[c] = f"{' y '.join(dict.fromkeys(adjetivos))} (Cluster {c})"
    return nombres