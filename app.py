"""
Aplicación: Análisis No Supervisado de Perfiles de Personalidad
Materia: Extracción de Conocimientos en Base de Datos - Unidad IV
------------------------------------------------------------------
Cumple con los requisitos de la Actividad 1:
  1. Cargar un archivo CSV.
  2. Mostrar la información cargada.
  3. Filtrar los datos.
  4. Generar estadística descriptiva básica (implementación manual).
  5. Entrenar un algoritmo de aprendizaje no supervisado (K-Means).
  6. Guardar el modelo entrenado para uso posterior (joblib).
  7. Mostrar los resultados del algoritmo.
  8. Descargar los datos filtrados.
  9. Descargar los resultados generados.

Ejecutar con:  streamlit run app.py
"""

from datetime import datetime
import unicodedata

import pandas as pd
import streamlit as st
import joblib
import plotly.express as px
import plotly.graph_objects as go

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
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

# Número mínimo de registros y de variables numéricas que debe tener
# el CSV para considerarse válido para este análisis.
MIN_REGISTROS = 5
MIN_VARIABLES_NUMERICAS = 2

# ------------------------------------------------------------------
# CSS personalizado (sin cambios respecto al diseño original)
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Fuerza SIEMPRE modo claro para toda la app, sin importar si el
       sistema operativo o el navegador de quien la usa está en modo
       oscuro. Esto evita que controles nativos (selects, sliders,
       menús desplegables, formularios) hereden fondo oscuro mientras
       nuestro CSS fuerza texto oscuro, lo que los volvía invisibles. */
    html, body, .stApp {
        color-scheme: light only;
    }

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

    .error-box {
        background: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        color: #991B1B !important;
    }
    .error-box strong { color: #991B1B !important; }

    /* Fondo claro forzado en menús desplegables, formularios, sliders,
       zona de arrastrar-y-soltar y expanders: estos elementos suelen
       renderizarse "flotando" fuera de nuestras tarjetas blancas, así
       que necesitan su propio fondo explícito. */
    [data-baseweb="popover"], [data-baseweb="menu"],
    ul[role="listbox"], li[role="option"],
    [data-baseweb="select"], [data-baseweb="tag"],
    div[data-testid="stForm"],
    section[data-testid="stFileUploaderDropzone"],
    div[data-testid="stExpander"], div[data-testid="stExpander"] summary,
    div[data-testid="stExpanderDetails"],
    .stSlider, .stRadio, .stMultiSelect, .stSelectbox {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
    }

    [data-baseweb="popover"] *, [data-baseweb="menu"] *,
    li[role="option"] *, div[data-testid="stExpanderDetails"] * {
        color: #1F2937 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================================
# UTILIDADES DE ESTADÍSTICA BÁSICA (implementadas "a mano", sin
# depender de funciones ya empaquetadas tipo describe())
# ==================================================================
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
    """Calcula estadística descriptiva básica columna por columna,
    usando únicamente las funciones manuales definidas arriba."""
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


def eliminar_marca_temporal(df):
    """Elimina la columna de 'Marca temporal' (timestamp) que agregan
    automáticamente formularios como Google Forms, ya que no aporta
    valor para el análisis de personalidad/gustos musicales."""
    columnas_a_eliminar = [
        c for c in df.columns
        if "marca temporal" in _normalizar_texto(c) or _normalizar_texto(c).strip() == "timestamp"
    ]
    if columnas_a_eliminar:
        df = df.drop(columns=columnas_a_eliminar)
    return df


# ==================================================================
# 1. CARGA DE DATOS
# ==================================================================
def cargar_datos():
    """Muestra el uploader y devuelve el DataFrame cargado (o None)."""
    card_abierta("① Carga de datos")
    archivo = st.file_uploader(
        "Sube el CSV exportado de tu encuesta (Google Forms, Typeform, etc.)",
        type=["csv"],
        label_visibility="visible",
    )

    if archivo is not None:
        try:
            df_cargado = pd.read_csv(archivo)
            df_cargado = eliminar_marca_temporal(df_cargado)
            st.session_state.df_original = df_cargado
            st.session_state.nombre_archivo = archivo.name
        except Exception as e:
            st.session_state.df_original = None
            st.markdown(
                f'<div class="error-box">❌ <strong>No se pudo leer el archivo.</strong><br>'
                f'Detalle: {e}</div>',
                unsafe_allow_html=True,
            )

    card_cerrada()
    return st.session_state.df_original


# ==================================================================
# VALIDACIÓN DEL CSV
# ==================================================================
def validar_dataset(df):
    """Verifica que el DataFrame tenga una estructura mínima usable
    (al menos MIN_REGISTROS filas y MIN_VARIABLES_NUMERICAS columnas
    numéricas). Muestra errores claros si no cumple y devuelve
    True/False."""
    errores = []

    if df is None or df.empty:
        errores.append("El archivo está vacío o no contiene registros.")
    else:
        if df.shape[0] < MIN_REGISTROS:
            errores.append(
                f"Se requieren al menos {MIN_REGISTROS} registros y el archivo solo tiene {df.shape[0]}."
            )

        columnas_numericas = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if len(columnas_numericas) < MIN_VARIABLES_NUMERICAS:
            errores.append(
                f"Se requieren al menos {MIN_VARIABLES_NUMERICAS} columnas numéricas "
                f"(rasgos/puntuaciones) y se detectaron {len(columnas_numericas)}."
            )

        if df.columns.duplicated().any():
            dup = df.columns[df.columns.duplicated()].tolist()
            errores.append(f"Existen columnas con nombres duplicados: {dup}.")

    if errores:
        lista_html = "".join(f"<li>{e}</li>" for e in errores)
        st.markdown(
            f'<div class="error-box">❌ <strong>El archivo no tiene la estructura esperada:</strong>'
            f'<ul>{lista_html}</ul></div>',
            unsafe_allow_html=True,
        )
        return False

    return True


# ==================================================================
# 2. MOSTRAR INFORMACIÓN GENERAL DEL DATASET
# ==================================================================
def mostrar_dataset(df):
    """Muestra métricas generales del dataset y una vista previa."""
    card_abierta("② Información general del dataset")

    columnas_numericas = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    valores_faltantes = int(df.isna().sum().sum())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Registros", df.shape[0])
    m2.metric("Columnas", df.shape[1])
    m3.metric("Variables numéricas", len(columnas_numericas))
    m4.metric("Valores faltantes", valores_faltantes)

    st.dataframe(estilizar_tabla(df), use_container_width=True, height=280)
    card_cerrada()


# ==================================================================
# 3. FILTRAR DATOS
# ==================================================================
def filtrar_datos(df):
    """Aplica filtros por categoría y por rango numérico. Devuelve el
    DataFrame filtrado y permite descargarlo."""
    card_abierta("③ Filtrar datos")

    columnas_categoricas = [c for c in df.columns if df[c].dtype == object]
    columnas_numericas = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    df_filtrado = df.copy()

    if columnas_categoricas:
        cols_filtro = st.columns(min(3, len(columnas_categoricas)))
        for i, col in enumerate(columnas_categoricas):
            with cols_filtro[i % len(cols_filtro)]:
                valores_unicos = sorted(df[col].dropna().unique().tolist(), key=str)
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

    st.markdown(
        f'<p style="color:#6D28D9; font-weight:600;">Registros después del filtro: {df_filtrado.shape[0]} '
        f'de {df.shape[0]}</p>',
        unsafe_allow_html=True,
    )
    st.dataframe(estilizar_tabla(df_filtrado), use_container_width=True, height=260)

    exportar_resultados(
        df_filtrado,
        etiqueta="⬇️ Descargar datos filtrados (CSV)",
        nombre_archivo="datos_filtrados.csv",
    )

    card_cerrada()
    return df_filtrado


# ==================================================================
# 4. ESTADÍSTICA DESCRIPTIVA BÁSICA
# ==================================================================
def mostrar_estadisticas(df_filtrado, columnas_numericas):
    """Muestra la estadística descriptiva (manual) y gráficas de
    apoyo, tanto para variables numéricas como categóricas."""
    card_abierta("④ Estadística descriptiva básica")

    columnas_categoricas = [c for c in df_filtrado.columns if df_filtrado[c].dtype == object]
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
            for col in columnas_categoricas:
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


# ==================================================================
# MÉTODO DEL CODO (ELBOW METHOD)
# ==================================================================
def metodo_codo(X_proc, k_max=10):
    """Calcula y grafica la inercia de K-Means para k = 1..k_max,
    para ayudar a elegir el número óptimo de clusters antes de
    entrenar el modelo final."""
    k_max = min(k_max, X_proc.shape[0] - 1) if X_proc.shape[0] > 2 else 2
    k_max = max(k_max, 2)

    inercias = []
    rango_k = list(range(1, k_max + 1))
    for k in rango_k:
        modelo_tmp = KMeans(n_clusters=k, random_state=42, n_init=10)
        modelo_tmp.fit(X_proc)
        inercias.append(modelo_tmp.inertia_)

    fig_codo = go.Figure()
    fig_codo.add_trace(go.Scatter(
        x=rango_k, y=inercias, mode="lines+markers",
        line=dict(color=PALETA[0], width=3),
        marker=dict(size=9, color=PALETA[1]),
    ))
    fig_codo.update_layout(
        title="Método del Codo — Inercia vs. Número de clusters (k)",
        xaxis_title="k (número de clusters)",
        yaxis_title="Inercia (WCSS)",
        height=340, margin=dict(t=50, b=10, l=10, r=10),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_codo, use_container_width=True)
    st.caption(
        "Busca el punto donde la curva deja de disminuir bruscamente (el 'codo'): "
        "ese valor de k suele ser una buena elección para el número de clusters."
    )


# ==================================================================
# 5. ENTRENAMIENTO DEL MODELO (ÚNICAMENTE K-MEANS)
# ==================================================================
def entrenar_kmeans(df_filtrado, columnas_numericas):
    """Sección completa de entrenamiento: selección de variables,
    método del codo, elección de k y ejecución de K-Means."""
    card_abierta("⑤ Entrenamiento del modelo (K-Means)")

    variables_modelo = st.multiselect(
        "Selecciona las variables numéricas a usar en el algoritmo",
        columnas_numericas,
        default=columnas_numericas,
    )

    normalizar = st.checkbox("Normalizar variables (recomendado)", value=True)

    if len(variables_modelo) < 2:
        st.warning("Selecciona al menos 2 variables numéricas para continuar.")
        card_cerrada()
        return

    if df_filtrado.shape[0] < MIN_REGISTROS:
        st.warning(f"Se necesitan al menos {MIN_REGISTROS} registros (después del filtro) para entrenar.")
        card_cerrada()
        return

    X = df_filtrado[variables_modelo].dropna()
    indices_validos = X.index

    if normalizar:
        scaler = StandardScaler()
        X_proc = scaler.fit_transform(X)
    else:
        scaler = None
        X_proc = X.values

    st.markdown("**Método del Codo — elige k antes de entrenar**")
    metodo_codo(X_proc, k_max=min(10, X.shape[0] - 1))

    k = st.slider("Número de clusters (k) a utilizar en el entrenamiento final", 2, 10, 4)

    entrenar = st.button("🚀 Entrenar modelo K-Means")

    if entrenar:
        modelo = KMeans(n_clusters=k, random_state=42, n_init=10)
        etiquetas = modelo.fit_predict(X_proc)

        df_resultados = df_filtrado.loc[indices_validos].copy()
        df_resultados["cluster"] = etiquetas

        st.session_state.modelo = modelo
        st.session_state.scaler = scaler
        st.session_state.df_resultados = df_resultados
        st.session_state.variables_modelo = variables_modelo

        guardar_modelo(modelo, scaler, variables_modelo)

        met1, met2 = st.columns(2)
        met1.metric("Clusters entrenados", k)
        try:
            sil = silhouette_score(X_proc, etiquetas)
            met2.metric("Silhouette Score", f"{sil:.3f}")
        except Exception:
            pass

    card_cerrada()


# ==================================================================
# GUARDAR MODELO ENTRENADO
# ==================================================================
def guardar_modelo(modelo, scaler, variables_modelo):
    """Guarda el modelo entrenado (y su scaler) en disco con joblib,
    para poder reutilizarlo posteriormente."""
    joblib.dump(
        {
            "modelo": modelo,
            "scaler": scaler,
            "variables": variables_modelo,
            "algoritmo": "K-Means",
            "fecha_entrenamiento": datetime.now().isoformat(),
        },
        "modelo_kmeans.pkl",
    )
    st.success("✅ Modelo entrenado y guardado como 'modelo_kmeans.pkl'.")

    try:
        with open("modelo_kmeans.pkl", "rb") as f:
            st.download_button(
                "⬇️ Descargar modelo entrenado (.pkl)",
                f.read(),
                file_name="modelo_kmeans.pkl",
                mime="application/octet-stream",
            )
    except Exception:
        pass


# ==================================================================
# 6. MOSTRAR RESULTADOS
# ==================================================================
def mostrar_resultados():
    """Muestra la tabla con el cluster asignado, la distribución de
    clusters, la proyección PCA en 2D, los centroides y los resúmenes
    estadísticos por cluster."""
    card_abierta("⑥ Resultados del algoritmo")

    if st.session_state.df_resultados is None:
        st.info("Entrena un modelo en la sección anterior para ver resultados aquí.")
        card_cerrada()
        return

    df_res = st.session_state.df_resultados
    variables_modelo = st.session_state.variables_modelo
    modelo = st.session_state.modelo
    scaler = st.session_state.scaler

    st.markdown("**Tabla con cluster asignado**")
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
        st.markdown("**Clusters proyectados en 2D (PCA)**")
        X_vis = df_res[variables_modelo].values
        if scaler is not None:
            X_vis = scaler.transform(X_vis)

        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(X_vis)

        df_plot = pd.DataFrame({
            "PC1": coords[:, 0],
            "PC2": coords[:, 1],
            "cluster": df_res["cluster"].astype(str).values,
        })

        var_explicada = pca.explained_variance_ratio_.sum()
        st.caption(f"Varianza explicada por los 2 componentes: {var_explicada:.1%}")
        fig_pca = px.scatter(
            df_plot, x="PC1", y="PC2", color="cluster",
            color_discrete_sequence=PALETA, opacity=0.85,
        )
        fig_pca.update_traces(marker=dict(size=11, line=dict(width=1, color="white")))
        fig_pca.update_layout(height=340, margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor="white")
        st.plotly_chart(fig_pca, use_container_width=True)

    # --- Centroides ---
    st.markdown("**Centroides de los clusters**")
    if scaler is not None:
        centroides = scaler.inverse_transform(modelo.cluster_centers_)
    else:
        centroides = modelo.cluster_centers_
    df_centroides = pd.DataFrame(centroides, columns=variables_modelo)
    df_centroides.insert(0, "cluster", range(df_centroides.shape[0]))
    st.dataframe(estilizar_tabla(df_centroides), use_container_width=True)

    # --- Tabla resumen: Cluster | Personas | Edad promedio ---
    st.markdown("**Resumen por cluster: personas y edad promedio**")
    columna_edad = _detectar_columna_edad(df_res)
    filas_resumen = []
    for c in sorted(df_res["cluster"].unique()):
        subset = df_res[df_res["cluster"] == c]
        edad_prom = None
        if columna_edad is not None:
            edad_prom = round(media_manual(subset[columna_edad].dropna().tolist()), 2)
        filas_resumen.append({
            "Cluster": c,
            "Personas": subset.shape[0],
            "Edad promedio": edad_prom if edad_prom is not None else "N/D",
        })
    st.dataframe(pd.DataFrame(filas_resumen), use_container_width=True)
    if columna_edad is None:
        st.caption("No se detectó una columna de edad en el dataset; se muestra 'N/D'.")

    # --- Promedio de todas las variables por cluster ---
    st.markdown("**Promedio de todas las variables numéricas por cluster**")
    columnas_numericas = [c for c in df_res.columns if pd.api.types.is_numeric_dtype(df_res[c]) and c != "cluster"]
    tabla_prom = df_res.groupby("cluster")[columnas_numericas].mean().round(3).reset_index()
    st.dataframe(estilizar_tabla(tabla_prom), use_container_width=True)

    # --- Resumen estadístico completo por cluster ---
    with st.expander("📊 Resumen estadístico detallado por cluster"):
        for c in sorted(df_res["cluster"].unique()):
            st.markdown(f"**Cluster {c}**")
            subset = df_res[df_res["cluster"] == c]
            tabla_stats_c = resumen_estadistico(subset, columnas_numericas)
            st.dataframe(estilizar_tabla(tabla_stats_c), use_container_width=True)

    exportar_resultados(
        df_res,
        etiqueta="⬇️ Descargar resultados (CSV con cluster asignado)",
        nombre_archivo="resultados_clusters.csv",
    )

    card_cerrada()


def _detectar_columna_edad(df):
    """Intenta ubicar automáticamente una columna de edad dentro del
    dataset (para la tabla Cluster | Personas | Edad promedio)."""
    for col in df.columns:
        if "edad" in col.lower() or "age" in col.lower():
            if pd.api.types.is_numeric_dtype(df[col]):
                return col
    return None


def _normalizar_texto(texto):
    """Pasa a minúsculas y elimina acentos, para poder comparar
    palabras clave sin importar tildes (música/musica, clásica/clasica,
    electrónica/electronica, etc.)."""
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(ch for ch in texto if not unicodedata.combining(ch))


def _detectar_columnas_musica(columnas):
    """Detecta qué columnas están relacionadas con gustos/hábitos
    musicales (para poder rellenarlas con un valor neutro cuando el
    cuestionario de personalidad no las pregunta directamente)."""
    palabras_clave = ["musica", "cancion"]
    return [c for c in columnas if any(p in _normalizar_texto(c) for p in palabras_clave)]


def _detectar_columnas_genero(columnas):
    """Detecta columnas asociadas a un género musical específico, para
    poder recomendar un género concreto según el cluster predicho.
    Devuelve un diccionario {nombre_genero: nombre_columna}.

    Primero intenta reconocer géneros comunes por nombre (para dar una
    etiqueta más "bonita"); cualquier otra columna musical detectada
    (por ejemplo con nombres propios de tu encuesta, como "Reggaetón"
    o "Corridos") se agrega igualmente usando el nombre original de la
    columna, para que la recomendación no dependa de una lista fija.
    """
    mapa_generos_conocidos = {
        "Rock": ["rock"],
        "Pop": ["pop"],
        "Electrónica": ["electronica"],
        "Clásica / Instrumental": ["clasica", "instrumental"],
        "Jazz": ["jazz"],
        "Hip Hop / Rap": ["hip hop", "hiphop", "rap"],
        "Reggaetón": ["reggaeton", "reggaton"],
        "Regional / Corridos": ["corrido", "regional", "banda", "ranchera"],
        "Metal": ["metal"],
        "R&B / Soul": ["r&b", "rnb", "soul"],
    }

    encontrados = {}
    columnas_musicales = _detectar_columnas_musica(columnas)

    # 1) Géneros conocidos, con etiqueta legible
    for genero, claves in mapa_generos_conocidos.items():
        for col in columnas:
            col_norm = _normalizar_texto(col)
            if any(clave in col_norm for clave in claves):
                encontrados[genero] = col
                break

    # 2) Cualquier otra columna musical no cubierta arriba: se agrega
    #    usando el nombre original de la columna como etiqueta.
    columnas_ya_usadas = set(encontrados.values())
    for col in columnas_musicales:
        if col not in columnas_ya_usadas:
            encontrados[col] = col

    return encontrados


# ==================================================================
# 9. EXPORTAR RESULTADOS / DATOS (botón de descarga reutilizable)
# ==================================================================
def exportar_resultados(df, etiqueta, nombre_archivo):
    st.download_button(
        etiqueta,
        df.to_csv(index=False).encode("utf-8"),
        file_name=nombre_archivo,
        mime="text/csv",
    )


# ==================================================================
# 7. CUESTIONARIO DE PRUEBA: RECOMENDACIÓN DE MÚSICA SEGÚN PERSONALIDAD
# ==================================================================
def cuestionario_recomendacion(df_base):
    """Pequeño cuestionario de opción múltiple que usa el modelo
    K-Means ya entrenado para predecir a qué cluster pertenece la
    persona según sus respuestas de personalidad, y recomienda un
    género musical con base en las preferencias dominantes de ese
    cluster."""
    card_abierta("⑦ Cuestionario: descubre qué música va con tu personalidad")

    if st.session_state.modelo is None or not st.session_state.variables_modelo:
        st.info("Entrena primero un modelo K-Means (sección ⑤) para habilitar este cuestionario.")
        card_cerrada()
        return

    modelo = st.session_state.modelo
    scaler = st.session_state.scaler
    variables_modelo = st.session_state.variables_modelo
    df_res = st.session_state.df_resultados

    columnas_musica = _detectar_columnas_musica(variables_modelo)
    preguntas_personalidad = [v for v in variables_modelo if v not in columnas_musica]

    if not preguntas_personalidad:
        st.warning(
            "El modelo actual fue entrenado únicamente con variables musicales; "
            "incluye al menos una variable de personalidad en el entrenamiento "
            "para poder generar este cuestionario."
        )
        card_cerrada()
        return

    st.caption(
        "Responde según qué tan de acuerdo estás con cada afirmación. "
        "1 = Totalmente en desacuerdo · 5 = Totalmente de acuerdo."
    )

    opciones_likert = {
        1: "1 · Totalmente en desacuerdo",
        2: "2 · En desacuerdo",
        3: "3 · Neutral",
        4: "4 · De acuerdo",
        5: "5 · Totalmente de acuerdo",
    }

    respuestas = {}
    with st.form("form_cuestionario_personalidad"):
        for pregunta in preguntas_personalidad:
            valores_col = df_base[pregunta].dropna()
            val_min = int(valores_col.min()) if not valores_col.empty else 1
            val_max = int(valores_col.max()) if not valores_col.empty else 5

            opciones_disponibles = [v for v in range(1, 6) if val_min <= v <= val_max] or list(range(val_min, val_max + 1))
            respuesta = st.radio(
                pregunta,
                options=opciones_disponibles,
                format_func=lambda v: opciones_likert.get(v, str(v)),
                horizontal=True,
                key=f"quiz_{pregunta}",
            )
            respuestas[pregunta] = respuesta

        enviado = st.form_submit_button("🔮 Descubrir mi tipo de música")

    if enviado:
        # Construir el vector de entrada en el mismo orden que variables_modelo.
        # Las variables musicales que no se preguntan se rellenan con el
        # promedio general del dataset (valor neutro que no sesga el cluster).
        vector = []
        for var in variables_modelo:
            if var in respuestas:
                vector.append(respuestas[var])
            else:
                vector.append(float(df_base[var].dropna().mean()))

        X_nuevo = pd.DataFrame([vector], columns=variables_modelo)
        if scaler is not None:
            X_nuevo_proc = scaler.transform(X_nuevo)
        else:
            X_nuevo_proc = X_nuevo.values

        cluster_predicho = int(modelo.predict(X_nuevo_proc)[0])

        st.markdown(
            f'<p style="color:#6D28D9; font-weight:700; font-size:1.05rem;">'
            f'Perteneces al Cluster {cluster_predicho}</p>',
            unsafe_allow_html=True,
        )

        generos_cols = _detectar_columnas_genero(df_base.columns.tolist())
        if generos_cols and df_res is not None and "cluster" in df_res.columns:
            subset_cluster = df_res[df_res["cluster"] == cluster_predicho]
            promedios_genero = {
                genero: media_manual(subset_cluster[col].dropna().tolist())
                for genero, col in generos_cols.items()
                if col in subset_cluster.columns and not subset_cluster[col].dropna().empty
            }
            if promedios_genero:
                genero_recomendado = max(promedios_genero, key=promedios_genero.get)
                st.success(f"🎧 Según tu perfil de personalidad, tu tipo de música recomendado es: **{genero_recomendado}**")

                df_generos = pd.DataFrame({
                    "género": list(promedios_genero.keys()),
                    "afinidad_promedio": [round(v, 2) for v in promedios_genero.values()],
                }).sort_values("afinidad_promedio", ascending=False)

                fig_genero = px.bar(
                    df_generos, x="género", y="afinidad_promedio", text="afinidad_promedio",
                    color="género", color_discrete_sequence=PALETA,
                )
                fig_genero.update_traces(textposition="outside")
                fig_genero.update_layout(
                    showlegend=False, height=320, margin=dict(t=20, b=10, l=10, r=10),
                    plot_bgcolor="white",
                )
                st.plotly_chart(fig_genero, use_container_width=True)
            else:
                st.info("No hay suficientes datos musicales en tu cluster para recomendar un género específico.")
        else:
            st.info(
                "No se detectaron columnas de géneros musicales (rock, pop, electrónica, clásica) "
                "en el dataset, así que no es posible recomendar un género concreto."
            )

    card_cerrada()


# ==================================================================
# CARGA DE UN MODELO YA ENTRENADO (uso posterior)
# ==================================================================
def cargar_modelo_previo():
    with st.expander("📦 Cargar un modelo ya entrenado (modelo_kmeans.pkl)"):
        archivo_modelo = st.file_uploader("Sube el archivo .pkl", type=["pkl"], key="modelo_upload")
        if archivo_modelo is not None:
            try:
                contenido = joblib.load(archivo_modelo)
                st.write("Algoritmo:", contenido.get("algoritmo"))
                st.write("Variables usadas:", contenido.get("variables"))
                st.write("Fecha de entrenamiento:", contenido.get("fecha_entrenamiento"))
                st.session_state.modelo = contenido.get("modelo")
                st.session_state.scaler = contenido.get("scaler")
                st.success("Modelo cargado en memoria correctamente.")
            except Exception as e:
                st.markdown(
                    f'<div class="error-box">❌ <strong>No se pudo cargar el modelo.</strong><br>'
                    f'Detalle: {e}</div>',
                    unsafe_allow_html=True,
                )


# ==================================================================
# ESTADO DE LA APP
# ==================================================================
def inicializar_estado():
    for clave in ["df_original", "df_filtrado", "modelo", "df_resultados", "scaler", "variables_modelo"]:
        if clave not in st.session_state:
            st.session_state[clave] = None


# ==================================================================
# PROGRAMA PRINCIPAL
# ==================================================================
def main():
    inicializar_estado()

    st.markdown(
        """
        <div class="hero">
            <h1>🧠 Análisis No Supervisado de Perfiles de Personalidad</h1>
            <p>Carga los resultados de tu encuesta en línea, explora los datos, entrena un modelo
            K-Means y descarga los resultados — todo en un solo lugar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = cargar_datos()

    if df is None:
        st.info("👆 Sube un archivo CSV para comenzar.")
        return

    if not validar_dataset(df):
        return

    mostrar_dataset(df)

    df_filtrado = filtrar_datos(df)
    st.session_state.df_filtrado = df_filtrado

    columnas_numericas = [c for c in df_filtrado.columns if pd.api.types.is_numeric_dtype(df_filtrado[c])]

    mostrar_estadisticas(df_filtrado, columnas_numericas)

    entrenar_kmeans(df_filtrado, columnas_numericas)

    mostrar_resultados()

    cuestionario_recomendacion(df_filtrado)

    cargar_modelo_previo()


if __name__ == "__main__":
    main()
