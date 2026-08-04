"""Entrenamiento (método del codo), guardado/formato de metadata y
nombrado automático de los clusters de K-Means."""

from datetime import datetime

import joblib
import streamlit as st
import plotly.graph_objects as go
from sklearn.cluster import KMeans

from config import PALETA
from styles import tema_plotly
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
                                fill="tozeroy", fillcolor="rgba(79,70,229,0.08)"))
    fig.update_layout(title="Método del Codo — Inercia vs. k", xaxis_title="k", yaxis_title="Inercia (WCSS)")
    st.plotly_chart(tema_plotly(fig, 360), use_container_width=True)
    st.caption("Elige k en el punto donde la curva deja de bajar bruscamente (el 'codo').")


def guardar_modelo(modelo, scaler, variables):
    """Guarda el modelo entrenado (con metadata: algoritmo, características
    y fecha/hora de creación) con joblib, para poder reutilizarlo después."""
    fecha = datetime.now()
    joblib.dump({"modelo": modelo, "scaler": scaler, "variables": variables,
                 "algoritmo": "K-Means", "fecha_entrenamiento": fecha.isoformat()}, "modelo_kmeans.pkl")
    st.success("✅ Modelo entrenado y guardado como 'modelo_kmeans.pkl'.")
    st.caption(f"🕒 Creado el {fecha.strftime('%d/%m/%Y %H:%M:%S')}")
    with open("modelo_kmeans.pkl", "rb") as f:
        st.download_button("⬇️ Descargar modelo (.pkl)", f.read(), file_name="modelo_kmeans.pkl", mime="application/octet-stream")


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