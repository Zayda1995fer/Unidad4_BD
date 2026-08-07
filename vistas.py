"""Una función por sección de la aplicación (carga, filtros,
estadística, entrenamiento, resultados y cuestionario)."""

import pandas as pd
import streamlit as st
import joblib
import plotly.express as px
import plotly.graph_objects as go

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from config import PALETA, MIN_REGISTROS, MIN_VARIABLES_NUMERICAS
from styles import card_abierta, card_cerrada, estilizar_tabla, tema_plotly, mensaje_error, icono
from etiquetas import (
    detectar_columnas_musica, detectar_columnas_genero, detectar_columna_edad,
    eliminar_marca_temporal, derivar_filtros_categoricos,
)
from estadistica import media, resumen_estadistico
from modelo import formatear_fecha, guardar_modelo, metodo_codo, nombrar_clusters, listar_modelos_guardados


def exportar_resultados(df, etiqueta, nombre_archivo):
    st.download_button(etiqueta, df.to_csv(index=False).encode("utf-8"), file_name=nombre_archivo, mime="text/csv")


# ==================================================================
# 1. Carga y 2. visualización de datos
# ==================================================================
def cargar_datos():
    card_abierta("folder_open", "Carga de datos", "Sube el CSV exportado de tu encuesta de personalidad y hábitos musicales.")
    archivo = st.file_uploader("Selecciona el archivo CSV", type=["csv"])
    if archivo is not None:
        try:
            df = eliminar_marca_temporal(pd.read_csv(archivo))
            st.session_state.df_original = df
        except Exception as e:
            st.session_state.df_original = None
            mensaje_error(f"No se pudo leer el archivo: {e}")
    card_cerrada()
    return st.session_state.df_original


def validar_dataset(df):
    errores = []
    if df is None or df.empty:
        errores.append("El archivo está vacío o no contiene registros.")
    else:
        if df.shape[0] < MIN_REGISTROS:
            errores.append(f"Se requieren al menos {MIN_REGISTROS} registros ({df.shape[0]} encontrados).")
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if len(num_cols) < MIN_VARIABLES_NUMERICAS:
            errores.append(f"Se requieren al menos {MIN_VARIABLES_NUMERICAS} columnas numéricas ({len(num_cols)} encontradas).")
        if df.columns.duplicated().any():
            errores.append(f"Columnas duplicadas: {df.columns[df.columns.duplicated()].tolist()}.")
    if errores:
        lista = "".join(f"<li>{e}</li>" for e in errores)
        mensaje_error(f"<strong>Estructura inválida:</strong><ul>{lista}</ul>")
        return False
    return True


def mostrar_dataset(df):
    card_abierta("table_view", "Información general del dataset", "Resumen del archivo cargado antes de filtrar o entrenar.")
    st.dataframe(estilizar_tabla(df), use_container_width=True, height=280)
    card_cerrada()


# ==================================================================
# 3. Filtro de datos
# ==================================================================
def filtrar_datos(df):
    card_abierta(
        "filter_alt", "Filtrar datos",
        "Filtra por categorías naturales (tipo de personalidad, edad, hábitos musicales) en vez de pregunta por pregunta.",
    )
    df_f = df.copy()
    filtros_activos = []

    categorias = derivar_filtros_categoricos(df)
    if categorias:
        cols = st.columns(min(2, len(categorias)) or 1)
        for i, (nombre, serie) in enumerate(categorias.items()):
            with cols[i % len(cols)]:
                valores = sorted([v for v in serie.dropna().unique().tolist() if v != "nan"])
                sel = st.multiselect(nombre, valores, default=valores)
                df_f = df_f[serie.isin(sel).reindex(df_f.index, fill_value=False)]
                if len(sel) < len(valores):
                    filtros_activos.append(f"{nombre}: {', '.join(map(str, sel)) or 'ninguno'}")
        st.caption(
            "Estas categorías se calculan a partir de tus respuestas numéricas reales "
            "(por ejemplo, \"Tipo de personalidad\" combina tus respuestas de extraversión y sociabilidad). "
            "Categorías como estado de ánimo, plataforma o instrumento favorito necesitarían agregar esas "
            "preguntas al formulario — no se derivan de la encuesta actual."
        )
    else:
        st.caption("No se pudieron derivar categorías de filtro con las columnas de este dataset.")

    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if num_cols:
        with st.expander("Filtros adicionales por rango numérico (pregunta por pregunta)"):
            for col in num_cols:
                lo, hi = float(df[col].min()), float(df[col].max())
                if lo == hi:
                    continue
                r = st.slider(col, lo, hi, (lo, hi))
                df_f = df_f[(df_f[col] >= r[0]) & (df_f[col] <= r[1])]
                if r[0] > lo or r[1] < hi:
                    filtros_activos.append(f"{col}: {r[0]:.0f}–{r[1]:.0f}")

    filtros_resumen = " · ".join(filtros_activos) if filtros_activos else "Sin filtros aplicados (dataset completo)"
    st.session_state.filtros_resumen = filtros_resumen

    st.markdown(f'<p style="color:#B3907A;font-weight:700;">Registros tras el filtro: {df_f.shape[0]} de {df.shape[0]}</p>', unsafe_allow_html=True)
    st.dataframe(estilizar_tabla(df_f), use_container_width=True, height=260)
    exportar_resultados(df_f, "Descargar datos filtrados (CSV)", "datos_filtrados.csv")
    card_cerrada()
    return df_f


# ==================================================================
# 4. Estadística descriptiva básica (solo variables numéricas)
# ==================================================================
def mostrar_estadisticas(df, num_cols, etiquetas):
    card_abierta("bar_chart", "Estadística descriptiva básica", "Media, mediana, moda, desviación y rango — calculados con funciones propias.")
    if num_cols:
        tabla = resumen_estadistico(df, num_cols, etiquetas)
        st.dataframe(estilizar_tabla(tabla), use_container_width=True)
        st.caption(
            "**n**: respuestas válidas · **media**: promedio · **mediana**: valor central al ordenar los datos · "
            "**moda**: valor más repetido · **desv. estándar**: qué tan dispersas están las respuestas respecto "
            "a la media (más alto = más variedad de opiniones) · **rango**: diferencia entre el máximo y el mínimo."
        )
        fig = go.Figure([
            go.Bar(x=tabla["característica"], y=tabla["media"], name="Media", marker_color=PALETA[0]),
            go.Bar(x=tabla["característica"], y=tabla["desv_estandar"], name="Desv. estándar", marker_color=PALETA[1]),
        ])
        fig.update_layout(barmode="group", title="Media y dispersión por característica")
        fig.update_xaxes(tickangle=-35)
        st.plotly_chart(tema_plotly(fig, 380), use_container_width=True)
    else:
        st.caption("No hay columnas numéricas.")
    card_cerrada()


# ==================================================================
# 5. Entrenamiento K-Means (con método del codo) y guardado
# ==================================================================
def entrenar_kmeans(df, num_cols, etiquetas):
    card_abierta("model_training", "Entrenamiento del modelo (K-Means)", "Activa o desactiva cada pregunta, revisa el codo y entrena el modelo final.")

    st.markdown("**Preguntas a incluir en el entrenamiento**")
    col_a, col_b, col_c = st.columns([1, 1, 2])
    with col_a:
        if st.button("Activar todas", key="activar_todas"):
            for col in num_cols:
                st.session_state[f"var_{col}"] = True
    with col_b:
        if st.button("Desactivar todas", key="desactivar_todas"):
            for col in num_cols:
                st.session_state[f"var_{col}"] = False

    cols_grid = st.columns(2)
    for i, col in enumerate(num_cols):
        etiqueta_corta = etiquetas.get(col, col)
        texto_completo = col.split(".", 1)[-1].strip() if "." in col[:4] else col
        with cols_grid[i % 2]:
            st.checkbox(f"**{etiqueta_corta}** — {texto_completo}", value=True, key=f"var_{col}")
    variables = [col for col in num_cols if st.session_state.get(f"var_{col}", True)]

    normalizar_datos = st.checkbox("Normalizar variables (recomendado)", value=True)

    if len(variables) < 2:
        st.warning("Activa al menos 2 preguntas numéricas."); card_cerrada(); return
    if df.shape[0] < MIN_REGISTROS:
        st.warning(f"Se necesitan al menos {MIN_REGISTROS} registros filtrados."); card_cerrada(); return

    X = df[variables].dropna()
    idx = X.index
    scaler = StandardScaler() if normalizar_datos else None
    Xp = scaler.fit_transform(X) if scaler else X.values

    st.markdown("**Paso 1 · Método del Codo**")
    metodo_codo(Xp, k_max=min(10, X.shape[0] - 1))
    st.markdown("**Paso 2 · Número final de clusters**")
    k = st.slider("k final", 2, 10, 4)

    if st.button("Entrenar modelo K-Means"):
        modelo = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = modelo.fit_predict(Xp)
        df_res = df.loc[idx].copy()
        df_res["cluster"] = labels

        st.session_state.update(modelo=modelo, scaler=scaler, df_resultados=df_res, variables_modelo=variables)

        try:
            silhouette = silhouette_score(Xp, labels)
        except Exception:
            silhouette = None

        filtros_resumen = st.session_state.get("filtros_resumen", "Sin filtros aplicados (dataset completo)")
        guardar_modelo(modelo, scaler, variables, filtros_resumen=filtros_resumen,
                        n_registros=X.shape[0], k=k, silhouette=silhouette)

        m1, m2 = st.columns(2)
        m1.metric("Clusters entrenados", k)
        if silhouette is not None:
            m2.metric("Silhouette Score", f"{silhouette:.3f}")
        st.caption("El Silhouette Score va de -1 a 1; más cerca de 1 significa grupos mejor separados.")
    card_cerrada()


# ==================================================================
# Reutilización de un modelo ya entrenado (independiente del dataset)
# ==================================================================
def cargar_modelo_previo():
    """Permite subir un modelo .pkl ya entrenado en cualquier momento,
    aunque todavía no se haya cargado ningún dataset. Los resultados
    se generan aparte (ver generar_resultados_si_posible), en cuanto
    haya un dataset compatible disponible."""
    with st.expander("Cargar un modelo ya entrenado (.pkl)"):
        st.caption("Puedes cargar un modelo aquí aunque todavía no hayas subido un dataset en la sección Datos.")
        archivo = st.file_uploader("Sube el archivo .pkl", type=["pkl"], key="modelo_upload")
        if archivo is not None:
            try:
                contenido = joblib.load(archivo)
                modelo = contenido.get("modelo")
                scaler = contenido.get("scaler")
                variables = contenido.get("variables")
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**Algoritmo:**", contenido.get("algoritmo", "N/D"))
                    st.write("**Fecha y hora de creación:**", formatear_fecha(contenido.get("fecha_entrenamiento")))
                    st.write("**k (clusters):**", contenido.get("k", "N/D"))
                with c2:
                    st.write("**Registros usados al entrenar:**", contenido.get("n_registros", "N/D"))
                    sil = contenido.get("silhouette_score")
                    st.write("**Silhouette Score:**", f"{sil:.3f}" if isinstance(sil, (int, float)) else "N/D")
                    st.write("**Filtros activos al entrenar:**", contenido.get("filtros_aplicados", "N/D (modelo guardado con una versión anterior)"))
                st.write("**Características:**", variables)

                es_modelo_nuevo = st.session_state.get("variables_modelo") != variables
                st.session_state.update(modelo=modelo, scaler=scaler, variables_modelo=variables)
                if es_modelo_nuevo:
                    st.session_state.df_resultados = None  # evita mezclar resultados de un modelo distinto
                st.success("Modelo cargado en memoria. Sube o usa un dataset compatible para ver resultados.")
            except Exception as e:
                mensaje_error(f"No se pudo cargar el modelo: {e}")


def mostrar_historial_modelos():
    """Muestra todos los modelos .pkl guardados en disco hasta ahora,
    con su fecha, filtros usados, k, registros y Silhouette Score —
    y la ruta exacta (absoluta) de cada archivo dentro del proyecto."""
    card_abierta("history", "Historial de modelos guardados", "Cada vez que entrenas, se crea un archivo .pkl nuevo — nada se sobrescribe.")
    tabla, ruta_carpeta = listar_modelos_guardados()
    st.markdown(
        f'<p>{icono("folder", 18)} Carpeta donde se guardan los modelos:<br>'
        f'<span class="ruta" style="font-family:\'Courier New\',monospace;background:#EDE9FE;padding:.15rem .5rem;border-radius:6px;">{ruta_carpeta}</span></p>',
        unsafe_allow_html=True,
    )
    if tabla.empty:
        st.info("Todavía no has entrenado ningún modelo en esta sesión. Ve a la sección **Entrenamiento** para crear el primero.")
    else:
        st.dataframe(tabla.drop(columns=["Ruta completa"]), use_container_width=True, height=min(60 + 38 * len(tabla), 320))
        with st.expander("Ver rutas completas de cada archivo"):
            for _, fila in tabla.iterrows():
                st.markdown(f'<div class="ficha-modelo"><strong>{fila["Archivo"]}</strong><br><span class="ruta">{fila["Ruta completa"]}</span></div>', unsafe_allow_html=True)
    card_cerrada()


def generar_resultados_si_posible(df):
    """Si ya hay un modelo cargado/entrenado en memoria pero todavía no
    hay resultados calculados para el dataset actual (por ejemplo,
    porque el modelo se cargó antes de subir el CSV), intenta generarlos
    automáticamente prediciendo sobre el dataset actual."""
    modelo = st.session_state.modelo
    variables = st.session_state.variables_modelo
    if modelo is None or not variables or st.session_state.df_resultados is not None:
        return
    if not set(variables).issubset(df.columns):
        st.warning("El dataset actual no tiene todas las columnas que usa el modelo cargado; no se pueden generar resultados con él.")
        return
    scaler = st.session_state.scaler
    X = df[variables].dropna()
    Xp = scaler.transform(X) if scaler else X.values
    df_res = df.loc[X.index].copy()
    df_res["cluster"] = modelo.predict(Xp)
    st.session_state.df_resultados = df_res
    st.success("Resultados generados automáticamente con el modelo cargado.")


# ==================================================================
# 6. Resultados del modelo
# ==================================================================
def mostrar_resultados(etiquetas):
    card_abierta("insights", "Resultados del modelo", "Perfiles encontrados, distribución, proyección PCA y promedios.")
    df_res = st.session_state.df_resultados
    if df_res is None:
        st.info("Entrena un modelo en la sección de Entrenamiento, o carga uno ya entrenado arriba junto con un dataset compatible, para ver resultados aquí.")
        card_cerrada(); return

    variables = st.session_state.variables_modelo
    modelo, scaler = st.session_state.modelo, st.session_state.scaler
    musica = detectar_columnas_musica(variables)
    personalidad = [v for v in variables if v not in musica]
    nombres = nombrar_clusters(df_res, personalidad, etiquetas)
    st.session_state.nombres_cluster = nombres

    st.markdown("**Perfiles encontrados**")
    st.markdown("".join(f'<span class="cluster-chip">{icono("headphones", 15)}{n}</span>' for n in nombres.values()), unsafe_allow_html=True)

    df_mostrar = df_res.rename(columns=etiquetas).copy()
    df_mostrar["perfil"] = df_res["cluster"].map(nombres)
    st.markdown("**Tabla con el perfil asignado a cada persona**")
    st.dataframe(estilizar_tabla(df_mostrar), use_container_width=True, height=280)

    col1, col2 = st.columns([1, 1.4])
    with col1:
        conteo = df_res["cluster"].value_counts().sort_index().reset_index()
        conteo.columns = ["cluster", "conteo"]
        conteo["perfil"] = conteo["cluster"].map(nombres)
        fig = px.pie(conteo, names="perfil", values="conteo", color_discrete_sequence=PALETA, hole=.5, title="Personas por perfil")
        st.plotly_chart(tema_plotly(fig, 360), use_container_width=True)

    with col2:
        Xv = scaler.transform(df_res[variables]) if scaler else df_res[variables].values
        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(Xv)
        df_plot = pd.DataFrame({"PC1": coords[:, 0], "PC2": coords[:, 1], "perfil": df_res["cluster"].map(nombres).values})
        fig = px.scatter(df_plot, x="PC1", y="PC2", color="perfil", color_discrete_sequence=PALETA, opacity=.85,
                          title=f"Proyección PCA · varianza explicada {pca.explained_variance_ratio_.sum():.1%}")
        fig.update_traces(marker=dict(size=11, line=dict(width=1, color="white")))
        st.plotly_chart(tema_plotly(fig, 360), use_container_width=True)

    st.markdown("**Centroides de cada perfil**")
    centroides = scaler.inverse_transform(modelo.cluster_centers_) if scaler else modelo.cluster_centers_
    df_cent = pd.DataFrame(centroides, columns=[etiquetas.get(v, v) for v in variables])
    df_cent.insert(0, "perfil", [nombres[c] for c in range(df_cent.shape[0])])
    st.dataframe(estilizar_tabla(df_cent), use_container_width=True)

    st.markdown("**Personas y edad promedio por perfil**")
    col_edad = detectar_columna_edad(df_res.columns)
    filas = [{"Perfil": nombres[c], "Personas": (s := df_res[df_res["cluster"] == c]).shape[0],
              "Edad promedio": round(media(s[col_edad].dropna().tolist()), 2) if col_edad else "N/D"}
             for c in sorted(df_res["cluster"].unique())]
    st.dataframe(pd.DataFrame(filas), use_container_width=True)

    st.markdown("**Promedio de todas las características numéricas por perfil**")
    num_cols = [c for c in df_res.columns if pd.api.types.is_numeric_dtype(df_res[c]) and c != "cluster"]
    tabla_prom = df_res.groupby("cluster")[num_cols].mean().round(3)
    tabla_prom.index = [nombres[c] for c in tabla_prom.index]
    st.dataframe(estilizar_tabla(tabla_prom.rename(columns=etiquetas).reset_index().rename(columns={"index": "Perfil"})), use_container_width=True)

    generos = detectar_columnas_genero(df_res.columns)
    if generos:
        st.markdown("**Género musical dominante por perfil**")
        filas_g = []
        for c in sorted(df_res["cluster"].unique()):
            s = df_res[df_res["cluster"] == c]
            prom = {g: media(s[col].dropna().tolist()) for g, col in generos.items()}
            filas_g.append({"Perfil": nombres[c], "Género recomendado": max(prom, key=prom.get) if prom else "N/D"})
        st.dataframe(pd.DataFrame(filas_g), use_container_width=True)

    with st.expander("Resumen estadístico detallado por perfil"):
        for c in sorted(df_res["cluster"].unique()):
            st.markdown(f"**{nombres[c]}**")
            st.dataframe(estilizar_tabla(resumen_estadistico(df_res[df_res["cluster"] == c], num_cols, etiquetas)), use_container_width=True)

    exportar_resultados(df_mostrar, "Descargar resultados (CSV con perfil asignado)", "resultados_clusters.csv")
    card_cerrada()


# ==================================================================
# 7. Cuestionario: recomendación de música según personalidad
# ==================================================================
def cuestionario_recomendacion(df, etiquetas):
    """df puede ser None: el cuestionario debe poder probarse con un
    modelo cargado aunque todavía no se haya subido ningún dataset.
    En ese caso se usan rangos genéricos (escala 1-5, edad 1-100) y,
    al enviar, solo se muestra el número de cluster crudo (el nombre
    del perfil y la recomendación de género necesitan un dataset para
    calcularse)."""
    card_abierta("recommend", "Cuestionario: descubre tu tipo de música", "Responde y el modelo entrenado te ubicará en un perfil.")
    if st.session_state.modelo is None or not st.session_state.variables_modelo:
        st.info("Entrena o carga primero un modelo K-Means para habilitar este cuestionario.")
        card_cerrada(); return

    modelo, scaler = st.session_state.modelo, st.session_state.scaler
    variables = st.session_state.variables_modelo
    df_res = st.session_state.df_resultados
    nombres = st.session_state.get("nombres_cluster") or {}
    musica = detectar_columnas_musica(variables)
    preguntas = [v for v in variables if v not in musica]

    if not preguntas:
        st.warning("El modelo solo usa variables musicales; incluye alguna de personalidad al entrenar.")
        card_cerrada(); return

    if df is None:
        st.caption("No hay un dataset cargado todavía: se usará una escala genérica (1-5, edad 1-100).")
    st.caption("1 = Totalmente en desacuerdo · 5 = Totalmente de acuerdo")
    opciones = {1: "1 · Desacuerdo", 2: "2 · Poco de acuerdo", 3: "3 · Neutral", 4: "4 · De acuerdo", 5: "5 · Totalmente de acuerdo"}
    col_edad = detectar_columna_edad(df.columns if df is not None else variables)

    respuestas = {}
    with st.form("form_cuestionario"):
        for p in preguntas:
            if df is not None:
                vals = df[p].dropna()
                lo, hi = (int(vals.min()), int(vals.max())) if not vals.empty else (1, 5)
                media_col = float(vals.mean()) if not vals.empty else 3.0
            else:
                vals = pd.Series(dtype=float)
                lo, hi, media_col = 1, 5, 3.0

            if p == col_edad:
                valor_defecto = int(round(vals.mean())) if not vals.empty else 25
                respuestas[p] = st.number_input(
                    f"**{etiquetas.get(p, p)}** — ¿cuál es tu edad?",
                    min_value=max(lo, 1) if df is not None else 1,
                    max_value=max(hi, lo + 1) if df is not None else 100,
                    value=valor_defecto, step=1,
                )
            else:
                opts = [v for v in range(1, 6) if lo <= v <= hi] or list(range(lo, hi + 1))
                respuestas[p] = st.radio(
                    f"**{etiquetas.get(p, p)}** — {p}",
                    opts, format_func=lambda v: opciones.get(v, str(v)),
                    horizontal=True, key=f"quiz_{p}",
                )
        enviado = st.form_submit_button("Descubrir mi tipo de música")

    if enviado:
        vector = []
        for v in variables:
            if v in respuestas:
                vector.append(respuestas[v])
            elif df is not None:
                vector.append(float(df[v].dropna().mean()))
            else:
                vector.append(3.0)  # valor neutro genérico si no hay dataset

        Xn = pd.DataFrame([vector], columns=variables)
        Xn = scaler.transform(Xn) if scaler else Xn.values
        cluster = int(modelo.predict(Xn)[0])
        nombre_perfil = nombres.get(cluster)

        if nombre_perfil:
            st.markdown(f'<p style="color:#B3907A;font-weight:700;font-size:1.05rem;">Tu perfil: {nombre_perfil}</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="color:#B3907A;font-weight:700;font-size:1.05rem;">Tu cluster: {cluster}</p>', unsafe_allow_html=True)
            st.caption("Sube un dataset compatible en la pestaña Datos para ver el nombre del perfil y la recomendación de género musical.")

        generos = detectar_columnas_genero(df.columns) if df is not None else {}
        if generos and df_res is not None:
            subset = df_res[df_res["cluster"] == cluster]
            prom = {g: media(subset[col].dropna().tolist()) for g, col in generos.items() if col in subset and not subset[col].dropna().empty}
            if prom:
                top = max(prom, key=prom.get)
                st.success(f"Tu tipo de música recomendado es: **{top}**")
                df_g = pd.DataFrame({"género": list(prom.keys()), "afinidad_promedio": [round(v, 2) for v in prom.values()]}).sort_values("afinidad_promedio", ascending=False)
                fig = px.bar(df_g, x="género", y="afinidad_promedio", text="afinidad_promedio", color="género",
                             color_discrete_sequence=PALETA, title="Afinidad musical de tu perfil")
                fig.update_traces(textposition="outside"); fig.update_layout(showlegend=False)
                st.plotly_chart(tema_plotly(fig, 320), use_container_width=True)
            else:
                st.info("No hay suficientes datos musicales en tu perfil para recomendar un género.")
        elif df is not None:
            st.info("No se detectaron columnas de género musical en el dataset.")
    card_cerrada()