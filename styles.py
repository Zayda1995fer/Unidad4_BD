"""CSS/HTML de la aplicación y utilidades visuales reutilizables.

Sin emojis: los títulos e indicadores usan la tipografía de iconos
"Material Symbols Outlined" (Google Fonts) en vez de emoji, para un
aspecto más formal. Las tablas usan un degradado morado claro y
semitransparente en vez de tonos saturados.
"""

import streamlit as st

from config import FUENTE

# IMPORTANTE: ni una sola línea en blanco dentro de CSS. Una línea en
# blanco corta el bloque <style> a la mitad en el renderizador de
# Streamlit y el resto del CSS aparece como texto visible en pantalla.
CSS = """
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color-scheme: light only; }
.icono-svg { vertical-align: middle; flex-shrink: 0; }
.stApp { background: linear-gradient(160deg, #F6F3FD 0%, #EFEAFB 100%); }
header[data-testid="stHeader"] { background: transparent; }
/* ---------- Compatibilidad modo claro/oscuro del sistema ---------- */
[data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"], li[role="option"], [data-testid="stExpander"], [data-testid="stExpanderDetails"], section[data-testid="stFileUploaderDropzone"] { background-color: #FFFFFF !important; color: #3B2E5A !important; }
[data-baseweb="popover"] *, [data-baseweb="menu"] *, li[role="option"] * { color: #3B2E5A !important; }
/* ---------- Selector de características (multiselect): tarjeta clara con tags morados ---------- */
div[data-testid="stMultiSelect"] div[data-baseweb="select"] { background-color: transparent !important; border: none !important; }
div[data-testid="stMultiSelect"] div[data-baseweb="select"] * { background-color: transparent !important; }
div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div { border: 2px solid #DDD6FE !important; border-radius: 18px !important; background-color: #FBFAFF !important; padding: .5rem !important; box-shadow: inset 0 1px 3px rgba(109,40,217,.06); }
div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:focus-within { border-color: #A78BFA !important; }
[data-baseweb="tag"] { background: linear-gradient(120deg, #8B5CF6, #7C3AED) !important; border: none !important; border-radius: 10px !important; box-shadow: 0 2px 6px rgba(124,58,237,.25); margin: .2rem !important; }
[data-baseweb="tag"] span { color: #FFFFFF !important; font-weight: 600; }
[data-baseweb="tag"] svg { fill: #FFFFFF !important; opacity: .8; }
[data-baseweb="tag"]:hover svg { opacity: 1; }
div[data-baseweb="select"] > div { min-height: 3.4rem; }
/* ---------- Barra lateral: degradado morado ---------- */
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #A78BFA 0%, #7C5CE0 100%) !important; border-right: none; }
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
section[data-testid="stSidebar"] .sidebar-brand { padding: .4rem 0 1.4rem 0; display: flex; align-items: center; gap: .55rem; }
section[data-testid="stSidebar"] .sidebar-brand .icono-svg { flex-shrink: 0; }
section[data-testid="stSidebar"] .sidebar-brand .texto-marca { line-height: 1.25; }
section[data-testid="stSidebar"] .sidebar-brand .titulo-marca { font-size: 1.15rem; font-weight: 900; display: block; }
section[data-testid="stSidebar"] .sidebar-brand .subtitulo-marca { opacity: .85; font-weight: 600; font-size: .78rem; display: block; }
section[data-testid="stSidebar"] div[data-testid="stRadio"] label { background: rgba(255,255,255,.14); border-radius: 14px; padding: .65rem 1rem; margin-bottom: .5rem; width: 100%; transition: background .15s ease; }
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover { background: rgba(255,255,255,.24); }
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) { background: rgba(255,255,255,.34); font-weight: 800; box-shadow: 0 4px 14px rgba(0,0,0,.12); }
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div { gap: 0; }
/* ---------- Encabezado principal ---------- */
.hero { padding: 2rem 2.3rem; border-radius: 22px; color: #FFFFFF !important; margin-bottom: 1.6rem; background: linear-gradient(120deg, #8B5CF6 0%, #7C3AED 60%, #6D28D9 130%) !important; box-shadow: 0 14px 32px rgba(109,40,217,.25); }
.hero .eyebrow { text-transform: uppercase; letter-spacing: .1em; font-size: .72rem; font-weight: 800; color: #E9D5FF !important; }
.hero h1 { color: #FFFFFF !important; margin: .3rem 0; font-size: 1.85rem; font-weight: 900; }
.hero p { color: #F3E8FF !important; opacity: .95; font-size: .98rem; max-width: 720px; line-height: 1.55; }
/* ---------- Tarjetas: blancas, redondeadas, sombra suave ---------- */
.card { background: var(--secondary-background-color); border: none; border-radius: 20px; padding: 1.6rem 1.8rem; margin-bottom: 1.4rem; box-shadow: 0 10px 28px rgba(109,40,217,.09); }
.card h2 { font-size: 1.1rem; font-weight: 800; color: #4C1D95; margin: 0 0 .3rem 0; display: flex; align-items: center; gap: .5rem; }
.card h2 .icono-svg { color: #7C3AED; }
.card .subtitulo { color: #6B4FA0; font-size: .89rem; margin-bottom: 1.1rem; line-height: 1.5; }
/* ---------- Texto de widgets nativos: color explícito, sin depender de variables de tema ---------- */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span, [data-testid="stWidgetLabel"] *, .stFileUploader small, div[data-testid="stFileUploaderDropzoneInstructions"] span, div[data-testid="stFileUploaderDropzoneInstructions"] small, .stCaptionContainer, [data-testid="stCaptionContainer"] { color: #3B2E5A !important; }
/* Etiquetas de sección en texto plano (p. ej. "Paso 1 · Método del Codo") sin clase propia */
.stMain .stMarkdown p:not([style]):not(.subtitulo) { color: #3B2E5A !important; }
/* Preguntas y opciones del cuestionario (radio buttons fuera de la barra lateral) */
.stMain div[data-testid="stRadio"] { color: #3B2E5A !important; }
.stMain div[data-testid="stRadio"] * { color: #3B2E5A !important; }
/* ---------- Métricas: pastel rotativo ---------- */
div[data-testid="stMetric"] { border-radius: 18px; border: none; padding: 1rem 1.1rem .85rem; box-shadow: 0 6px 16px rgba(109,40,217,.09); }
div[data-testid="column"]:nth-of-type(4n+1) div[data-testid="stMetric"] { background: #EDE9FE; }
div[data-testid="column"]:nth-of-type(4n+2) div[data-testid="stMetric"] { background: #F3E8FD; }
div[data-testid="column"]:nth-of-type(4n+3) div[data-testid="stMetric"] { background: #EEF2FF; }
div[data-testid="column"]:nth-of-type(4n+4) div[data-testid="stMetric"] { background: #F5F3FF; }
div[data-testid="stMetricValue"] { color: #6D28D9; font-weight: 900; }
div[data-testid="stMetricLabel"] { font-weight: 700; opacity: .75; }
/* ---------- Botones ---------- */
.stButton>button, .stDownloadButton>button { border-radius: 999px; font-weight: 800; border: none; padding: .6rem 1.5rem; }
.stButton>button { background: linear-gradient(120deg, #7C3AED, #6D28D9) !important; color: white !important; box-shadow: 0 8px 18px rgba(109,40,217,.3); }
.stButton>button:hover { filter: brightness(1.06); }
.stDownloadButton>button { background: #EDE9FE; color: #6D28D9; }
.stDownloadButton>button:hover { background: #DDD6FE; }
/* ---------- Tablas: morado claro semitransparente ---------- */
div[data-testid="stDataFrame"] { border-radius: 16px; overflow: hidden; border: none; box-shadow: 0 6px 18px rgba(109,40,217,.09); }
/* ---------- Alertas / chips ---------- */
.error-box { background: #FEE2E2; border-radius: 16px; padding: 1rem 1.2rem; color: #B91C1C !important; display: flex; align-items: flex-start; gap: .6rem; }
.cluster-chip { display: inline-flex; align-items: center; gap: .35rem; padding: .5rem 1.1rem; border-radius: 999px; font-weight: 800; background: #EDE9FE; color: #6D28D9; margin: 0 .5rem .6rem 0; font-size: .85rem; }
.cluster-chip .icono-svg { flex-shrink: 0; }
.cluster-chip:nth-child(2n) { background: #F3E8FD; color: #7C2D9E; }
.cluster-chip:nth-child(3n) { background: #EEF2FF; color: #4338CA; }
/* ---------- Ficha de modelo guardado (historial) ---------- */
.ficha-modelo { border-radius: 16px; background: #F5F3FF; padding: 1rem 1.2rem; margin-bottom: .9rem; box-shadow: 0 4px 14px rgba(109,40,217,.07); }
.ficha-modelo .fila-meta { display: flex; align-items: center; gap: .45rem; margin-bottom: .25rem; }
.ficha-modelo .fila-meta .icono-svg { color: #7C3AED; }
.ficha-modelo .ruta { font-family: 'Courier New', monospace; font-size: .82rem; background: #EDE9FE; padding: .15rem .5rem; border-radius: 6px; display: inline-block; margin-top: .3rem; }
</style>
"""

HERO = """
<div class="hero">
<div class="eyebrow">Unidad IV · Análisis No Supervisado</div>
<h1>Personalidad &amp; Hábitos Musicales</h1>
<p>Agrupa perfiles de personalidad con gustos musicales afines usando K-Means, y descubre qué género
va mejor con tu forma de ser. Cada modelo entrenado queda registrado con fecha, filtros y resultados.</p>
</div>
"""


_ICONOS_SVG = {
    # Logo de la barra lateral: ondas de sonido
    "graphic_eq": '<circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/>',
    # Carpeta (carga de datos / carpeta de modelos)
    "folder_open": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    "folder": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    # Lista (información general del dataset)
    "table_view": '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>',
    # Embudo (filtrar datos)
    "filter_alt": '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    # Controles deslizantes (filtros por rango)
    "tune": '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
    # Barras (estadística)
    "bar_chart": '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    # Actividad (entrenamiento del modelo)
    "model_training": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    # Reloj (historial / fecha)
    "history": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "schedule": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    # Tendencia ascendente (resultados)
    "insights": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    # Pulgar arriba (recomendador)
    "recommend": '<path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>',
    # Alerta (errores)
    "error": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    # Audífonos (perfiles / recomendación musical)
    "headphones": '<path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>',
}


def icono(nombre, tamano=20):
    """Devuelve el HTML de un icono SVG en línea, estilo trazo simple
    (sin relleno, esquinas redondeadas) — sin depender de ninguna
    fuente externa ni de emoji. `nombre` debe ser una de las claves de
    _ICONOS_SVG. Solo funciona dentro de HTML renderizado con
    unsafe_allow_html=True — los widgets nativos de Streamlit (botones,
    expanders, mensajes st.success/info/error) no aceptan HTML en su
    etiqueta, así que esos usan solo texto sin icono."""
    trazos = _ICONOS_SVG.get(nombre, "")
    return (
        f'<svg class="icono-svg" xmlns="http://www.w3.org/2000/svg" width="{tamano}" height="{tamano}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{trazos}</svg>'
    )


def sidebar_brand():
    st.sidebar.markdown(
        f'<div class="sidebar-brand">{icono("graphic_eq", 26)}'
        f'<span class="texto-marca"><span class="titulo-marca">Persona&amp;Play</span>'
        f'<span class="subtitulo-marca">Panel de análisis</span></span></div>',
        unsafe_allow_html=True,
    )


def card_abierta(icono_nombre, titulo, subtitulo=None):
    sub = f'<p class="subtitulo">{subtitulo}</p>' if subtitulo else ""
    st.markdown(f'<div class="card"><h2>{icono(icono_nombre, 20)}{titulo}</h2>{sub}', unsafe_allow_html=True)


def card_cerrada():
    st.markdown("</div>", unsafe_allow_html=True)


def mensaje_error(texto):
    st.markdown(f'<div class="error-box">{icono("error", 20)}<div>{texto}</div></div>', unsafe_allow_html=True)


def estilizar_tabla(df):
    """Degradado morado claro y semitransparente (no colores saturados)."""
    try:
        cols_num = df.select_dtypes("number").columns
        return (
            df.style
            .background_gradient(subset=cols_num, cmap="Purples", low=0, high=0.55, vmin=None)
            .format(precision=2)
        )
    except Exception:
        return df


def tema_plotly(fig, altura=340):
    fig.update_layout(
        font=dict(family=FUENTE, size=12, color="#3B2E5A"), height=altura,
        margin=dict(t=45, b=15, l=15, r=15), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", y=1.12, font=dict(size=11)), title_font=dict(size=14, color="#4C1D95"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#F1EDFB")
    return fig
