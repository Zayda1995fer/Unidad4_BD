"""
Aplicación: Análisis No Supervisado de Perfiles de Personalidad
Materia: Extracción de Conocimientos en Base de Datos - Unidad IV
------------------------------------------------------------------
Cumple con los requisitos de la Actividad 1:
  - Carga de datos (CSV de encuesta en línea)
  - Mostrar la información cargada
  - Filtro por categorías
  - Estadística básica (implementada manualmente, sin usar df.describe())
  - Entrenamiento del algoritmo no supervisado (K-Means / DBSCAN / Jerárquico / GMM)
  - Guardado del modelo entrenado
  - Generación y visualización de resultados (clusters asignados)
  - Descarga de datos filtrados y de resultados

Ejecutar con:  streamlit run app.py
"""

from datetime import datetime

import pandas as pd
import streamlit as st
import joblib
import plotly.express as px
import plotly.graph_objects as go

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score

st.set_page_config(
    page_title="Análisis No Supervisado - Personalidad",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# Paleta de colores propia para gráficas
# ------------------------------------------------------------------
PALETA = ["#7C3AED", "#EC4899", "#06B6D4", "#F59E0B", "#10B981", "#EF4444", "#6366F1", "#84CC16"]

# ------------------------------------------------------------------
# CSS personalizado
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #FAFAFF 0%, #FFFFFF 250px);
    }

    .hero {
        padding: 2rem 2.2rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #7C3AED 0%, #C026D3 55%, #EC4899 100%);
        color: white;
        margin-bottom: 1.6rem;
        box-shadow: 0 10px 30px rgba(124, 58, 237, 0.25);
    }
    .hero h1 {
        color: white;
        margin: 0 0 0.35rem 0;
        font-size: 2rem;
        font-weight: 800;
    }
    .hero p {
        margin: 0;
        opacity: 0.92;
        font-size: 1.02rem;
    }

    .card {
        background: #FFFFFF;
        border: 1px solid #EEE9FB;
        border-radius: 16px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1.3rem;
        box-shadow: 0 2px 14px rgba(76, 29, 149, 0.06);
    }

    .card h2 {
        font-size: 1.15rem;
        font-weight: 700;
        color: #4C1D95;
        margin-top: 0;
        margin-bottom: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    div[data-testid="stMetric"] {
        background: #F5F3FF;
        border: 1px solid #E9E1FC;
        border-radius: 14px;
        padding: 0.9rem 1rem 0.6rem 1rem;
    }
    div[data-testid="stMetricValue"] {
        color: #6D28D9;
        font-weight: 800;
    }
    div[data-testid="stMetricLabel"] {
        color: #6B7280;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
        padding: 0.55rem 1.2rem;
    }
    .stButton > button {
        background: linear-gradient(120deg, #7C3AED, #C026D3);
        color: white;
    }
    .stButton > button:hover {
        opacity: 0.92;
        color: white;
    }
    .stDownloadButton > button {
        background: #F5F3FF;
        color: #6D28D9;
        border: 1px solid #DDD3FA;
    }

    button[data-baseweb="tab"] {
        font-weight: 600;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #EEE9FB;
    }

    .streamlit-expanderHeader {
        font-weight: 600;
        color: #4C1D95;
    }

    /* Forzar texto oscuro en toda la app (evita blanco-sobre-blanco
       cuando el navegador/SO está en modo oscuro) */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li,
    .stMarkdown, .stCaption, h1, h2, h3, h4, h5, h6,
    div[data-testid="stMarkdownContainer"],
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stMetricLabel"],
    section[data-testid="stFileUploaderDropzone"] span,
    section[data-testid="stFileUploaderDropzone"] small {
        color: #1F2937 !important;
    }

    /* El encabezado "hero" se mantiene en blanco por contraste */
    .hero, .hero h1, .hero p {
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Utilidades de estadística básica (implementadas "a mano", sin
# depender de funciones ya empaquetadas tipo describe())
# ------------------------------------------------------------------
def media_manual(valores):
    valores = list(valores)
    return sum(valores) / len(valores) if valores else float("nan")


def varianza_manual(valores):
    valores = list(valores)
    n = len(valores)
    if n < 2:
        return float("nan")
    m = media_manual(valores)
    return sum((x - m) ** 2 for x in valores) / (n - 1)


def desviacion_manual(valores):
    var = varianza_manual(valores)
    return var ** 0.5 if var == var else float("nan")  # var==var descarta NaN


def moda_manual(valores):
    conteo = {}
    for v in valores:
        conteo[v] = conteo.get(v, 0) + 1
    if not conteo:
        return None
    return max(conteo, key=conteo.get)


def mediana_manual(valores):
    ordenados = sorted(valores)
    n = len(ordenados)
    if n == 0:
        return float("nan")
    mitad = n // 2
    if n % 2 == 0:
        return (ordenados[mitad - 1] + ordenados[mitad]) / 2
    return ordenados[mitad]


def rango_manual(valores):
    if not valores:
        return float("nan")
    return max(valores) - min(valores)


def resumen_estadistico(df, columnas_numericas):
    filas = []
    for col in columnas_numericas:
        vals = df[col].dropna().tolist()
        filas.append({
            "columna": col,
            "n": len(vals),
            "media": round(media_manual(vals), 3) if vals else None,
            "mediana": round(mediana_manual(vals), 3) if vals else None,
            "moda": moda_manual(vals),
            "desv_estandar": round(desviacion_manual(vals), 3) if len(vals) > 1 else None,
            "varianza": round(varianza_manual(vals), 3) if len(vals) > 1 else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "rango": rango_manual(vals) if vals else None,
        })
    return pd.DataFrame(filas)


def card_abierta(titulo_html):
    st.markdown(f'<div class="card"><h2>{titulo_html}</h2>', unsafe_allow_html=True)


def card_cerrada():
    st.markdown("</div>", unsafe_allow_html=True)


def estilizar_tabla(df):
    """Devuelve un Styler con gradiente sutil para columnas numéricas."""
    cols_num = df.select_dtypes(include="number").columns
    try:
        return df.style.background_gradient(subset=cols_num, cmap="Purples").format(precision=2)
    except Exception:
        return df


# ------------------------------------------------------------------
# Estado de la app
# ------------------------------------------------------------------
for clave in ["df_original", "df_filtrado", "modelo", "df_resultados", "scaler"]:
    if clave not in st.session_state:
        st.session_state[clave] = None

# ------------------------------------------------------------------
# HERO / encabezado
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🧠 Análisis No Supervisado de Perfiles de Personalidad</h1>
        <p>Carga los resultados de tu encuesta en línea, explora los datos, entrena un algoritmo
        de agrupamiento y descarga los resultados — todo en un solo lugar.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# 1. CARGA DE DATOS
# ------------------------------------------------------------------
card_abierta("① Carga de datos")

col_up, col_demo = st.columns([2, 1])
with col_up:
    archivo = st.file_uploader(
        "Sube el CSV exportado de tu encuesta (Google Forms, Typeform, etc.)",
        type=["csv"],
        label_visibility="visible",
    )
with col_demo:
    st.write("")
    st.write("")
    usar_ejemplo = st.checkbox("✨ Usar dataset de ejemplo", value=False)

if archivo is not None:
    st.session_state.df_original = pd.read_csv(archivo)
elif usar_ejemplo and st.session_state.df_original is None:
    st.session_state.df_original = pd.read_csv("encuesta_personalidad_ejemplo.csv")

df = st.session_state.df_original
card_cerrada()

if df is None:
    st.info("👆 Sube un archivo CSV o activa el dataset de ejemplo para comenzar.")
    st.stop()

columnas = df.columns.tolist()
columnas_categoricas = [c for c in columnas if df[c].dtype == object]
columnas_numericas = [c for c in columnas if pd.api.types.is_numeric_dtype(df[c])]

# ------------------------------------------------------------------
# 2. MOSTRAR INFORMACIÓN CARGADA
# ------------------------------------------------------------------
card_abierta("② Datos cargados")

m1, m2, m3 = st.columns(3)
m1.metric("Registros", df.shape[0])
m2.metric("Columnas", df.shape[1])
m3.metric("Variables numéricas", len(columnas_numericas))

st.dataframe(estilizar_tabla(df), use_container_width=True, height=280)
card_cerrada()

# ------------------------------------------------------------------
# 3. FILTRO POR CATEGORÍAS
# ------------------------------------------------------------------
card_abierta("③ Filtrar por categorías")

df_filtrado = df.copy()

if columnas_categoricas:
    cols_filtro = st.columns(min(3, len(columnas_categoricas)))
    for i, col in enumerate(columnas_categoricas):
        with cols_filtro[i % len(cols_filtro)]:
            valores_unicos = sorted(df[col].dropna().unique().tolist())
            seleccion = st.multiselect(f"Filtrar por {col}", valores_unicos, default=valores_unicos)
            df_filtrado = df_filtrado[df_filtrado[col].isin(seleccion)]
else:
    st.caption("No se detectaron columnas categóricas para filtrar.")

if columnas_numericas:
    with st.expander("🔧 Filtros adicionales por rango numérico"):
        for col in columnas_numericas:
            min_v, max_v = float(df[col].min()), float(df[col].max())
            if min_v == max_v:
                continue
            rango = st.slider(f"{col}", min_v, max_v, (min_v, max_v))
            df_filtrado = df_filtrado[(df_filtrado[col] >= rango[0]) & (df_filtrado[col] <= rango[1])]

st.session_state.df_filtrado = df_filtrado

st.markdown(
    f'<p style="color:#6D28D9; font-weight:600;">Registros después del filtro: {df_filtrado.shape[0]} '
    f'de {df.shape[0]}</p>',
    unsafe_allow_html=True,
)
st.dataframe(estilizar_tabla(df_filtrado), use_container_width=True, height=260)

st.download_button(
    "⬇️ Descargar datos filtrados (CSV)",
    df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="datos_filtrados.csv",
    mime="text/csv",
)
card_cerrada()

# ------------------------------------------------------------------
# 4. ESTADÍSTICA BÁSICA (implementación propia)
# ------------------------------------------------------------------
card_abierta("④ Estadística descriptiva básica")

tab_num, tab_cat = st.tabs(["📈 Variables numéricas", "🗂️ Variables categóricas"])

with tab_num:
    if columnas_numericas:
        tabla_stats = resumen_estadistico(df_filtrado, columnas_numericas)
        st.dataframe(estilizar_tabla(tabla_stats), use_container_width=True)

        fig_stats = go.Figure()
        fig_stats.add_trace(go.Bar(
            x=tabla_stats["columna"], y=tabla_stats["media"],
            name="Media", marker_color=PALETA[0],
        ))
        fig_stats.add_trace(go.Bar(
            x=tabla_stats["columna"], y=tabla_stats["desv_estandar"],
            name="Desv. estándar", marker_color=PALETA[1],
        ))
        fig_stats.update_layout(
            barmode="group", height=350, margin=dict(t=20, b=10, l=10, r=10),
            plot_bgcolor="white", legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_stats, use_container_width=True)
    else:
        st.caption("No hay columnas numéricas para calcular estadística.")

with tab_cat:
    if columnas_categoricas:
        for i, col in enumerate(columnas_categoricas):
            conteo = df_filtrado[col].value_counts().reset_index()
            conteo.columns = [col, "conteo"]
            fig_cat = px.bar(
                conteo, x=col, y="conteo", text="conteo",
                color=col, color_discrete_sequence=PALETA,
                title=f"Frecuencia — {col}",
            )
            fig_cat.update_traces(textposition="outside")
            fig_cat.update_layout(
                showlegend=False, height=320, margin=dict(t=40, b=10, l=10, r=10),
                plot_bgcolor="white",
            )
            st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.caption("No hay columnas categóricas para graficar frecuencias.")

card_cerrada()

# ------------------------------------------------------------------
# 5. ENTRENAMIENTO DEL ALGORITMO NO SUPERVISADO
# ------------------------------------------------------------------
card_abierta("⑤ Entrenamiento del modelo (Aprendizaje No Supervisado)")

variables_modelo = st.multiselect(
    "Selecciona las variables numéricas a usar en el algoritmo (rasgos de personalidad)",
    columnas_numericas,
    default=columnas_numericas,
)

algoritmo = st.selectbox(
    "Algoritmo no supervisado",
    ["K-Means", "Clusterización Jerárquica", "DBSCAN", "Modelo de Agrupamiento Gaussiano (GMM)"],
)

col_a, col_b = st.columns(2)
with col_a:
    if algoritmo in ["K-Means", "Clusterización Jerárquica", "Modelo de Agrupamiento Gaussiano (GMM)"]:
        k = st.slider("Número de clusters (k)", 2, 10, 4)
    else:
        eps = st.slider("DBSCAN - eps (radio de vecindad)", 0.1, 3.0, 0.8)
        min_samples = st.slider("DBSCAN - min_samples", 2, 20, 5)

with col_b:
    normalizar = st.checkbox("Normalizar variables (recomendado)", value=True)

entrenar = st.button("🚀 Entrenar modelo")

if entrenar:
    if len(variables_modelo) < 2:
        st.error("Selecciona al menos 2 variables numéricas para entrenar el modelo.")
    elif df_filtrado.shape[0] < 5:
        st.error("Se necesitan al menos 5 registros (después del filtro) para entrenar.")
    else:
        X = df_filtrado[variables_modelo].dropna()
        indices_validos = X.index

        if normalizar:
            scaler = StandardScaler()
            X_proc = scaler.fit_transform(X)
            st.session_state.scaler = scaler
        else:
            X_proc = X.values
            st.session_state.scaler = None

        if algoritmo == "K-Means":
            modelo = KMeans(n_clusters=k, random_state=42, n_init=10)
            etiquetas = modelo.fit_predict(X_proc)
        elif algoritmo == "Clusterización Jerárquica":
            modelo = AgglomerativeClustering(n_clusters=k)
            etiquetas = modelo.fit_predict(X_proc)
        elif algoritmo == "DBSCAN":
            modelo = DBSCAN(eps=eps, min_samples=min_samples)
            etiquetas = modelo.fit_predict(X_proc)
        else:  # GMM
            modelo = GaussianMixture(n_components=k, random_state=42)
            modelo.fit(X_proc)
            etiquetas = modelo.predict(X_proc)

        st.session_state.modelo = modelo

        df_resultados = df_filtrado.loc[indices_validos].copy()
        df_resultados["cluster"] = etiquetas
        st.session_state.df_resultados = df_resultados
        st.session_state.variables_modelo = variables_modelo

        joblib.dump(
            {
                "modelo": modelo,
                "scaler": st.session_state.scaler,
                "variables": variables_modelo,
                "algoritmo": algoritmo,
                "fecha_entrenamiento": datetime.now().isoformat(),
            },
            "modelo_personalidad.pkl",
        )

        st.success(f"✅ Modelo entrenado y guardado como 'modelo_personalidad.pkl' ({algoritmo}).")

        n_clusters_encontrados = len(set(etiquetas)) - (1 if -1 in etiquetas else 0)

        met1, met2 = st.columns(2)
        met1.metric("Clusters encontrados", n_clusters_encontrados)
        try:
            if n_clusters_encontrados >= 2:
                sil = silhouette_score(X_proc, etiquetas)
                met2.metric("Silhouette Score", f"{sil:.3f}")
        except Exception:
            pass

card_cerrada()

# ------------------------------------------------------------------
# 6. RESULTADOS
# ------------------------------------------------------------------
card_abierta("⑥ Resultados del algoritmo")

if st.session_state.df_resultados is not None:
    df_res = st.session_state.df_resultados
    variables_modelo = st.session_state.get("variables_modelo", variables_modelo)

    st.dataframe(estilizar_tabla(df_res), use_container_width=True, height=280)

    col_dist, col_pca = st.columns([1, 1.4])

    with col_dist:
        st.markdown("**Distribución por cluster**")
        conteo_cluster = df_res["cluster"].value_counts().sort_index().reset_index()
        conteo_cluster.columns = ["cluster", "conteo"]
        conteo_cluster["cluster"] = conteo_cluster["cluster"].astype(str)
        fig_dist = px.pie(
            conteo_cluster, names="cluster", values="conteo",
            color_discrete_sequence=PALETA, hole=0.45,
        )
        fig_dist.update_layout(height=340, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_pca:
        if len(variables_modelo) >= 2:
            X_vis = df_res[variables_modelo].values
            if st.session_state.scaler is not None:
                X_vis = st.session_state.scaler.transform(X_vis)

            pca = PCA(n_components=2, random_state=42)
            coords = pca.fit_transform(X_vis)

            df_plot = pd.DataFrame({
                "PC1": coords[:, 0],
                "PC2": coords[:, 1],
                "cluster": df_res["cluster"].astype(str).values,
            })

            var_explicada = pca.explained_variance_ratio_.sum()
            st.markdown(f"**Clusters proyectados en 2D (PCA)** · varianza explicada: {var_explicada:.1%}")
            fig_pca = px.scatter(
                df_plot, x="PC1", y="PC2", color="cluster",
                color_discrete_sequence=PALETA,
                opacity=0.85,
            )
            fig_pca.update_traces(marker=dict(size=11, line=dict(width=1, color="white")))
            fig_pca.update_layout(height=340, margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor="white")
            st.plotly_chart(fig_pca, use_container_width=True)

    st.download_button(
        "⬇️ Descargar resultados (CSV con cluster asignado)",
        df_res.to_csv(index=False).encode("utf-8"),
        file_name="resultados_clusters.csv",
        mime="text/csv",
    )
else:
    st.info("Entrena un modelo en la sección anterior para ver resultados aquí.")

card_cerrada()

# ------------------------------------------------------------------
# 7. Carga de modelo previamente entrenado (uso posterior)
# ------------------------------------------------------------------
with st.expander("📦 Cargar un modelo ya entrenado (modelo_personalidad.pkl)"):
    archivo_modelo = st.file_uploader("Sube el archivo .pkl", type=["pkl"], key="modelo_upload")
    if archivo_modelo is not None:
        contenido = joblib.load(archivo_modelo)
        st.write("Algoritmo:", contenido.get("algoritmo"))
        st.write("Variables usadas:", contenido.get("variables"))
        st.write("Fecha de entrenamiento:", contenido.get("fecha_entrenamiento"))
        st.session_state.modelo = contenido.get("modelo")
        st.session_state.scaler = contenido.get("scaler")
        st.success("Modelo cargado en memoria correctamente.")
