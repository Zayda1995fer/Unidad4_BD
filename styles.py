"""CSS/HTML de la aplicación y utilidades visuales reutilizables.

Paleta café-crema (dada por la persona usuaria):
  #F5F5EB  fondo general (el más claro)
  #EFE7DA  tarjetas
  #E1DACA  bordes suaves / fondos secundarios
  #C1B6A3  tono neutro secundario (texto atenuado, series de gráficas)
  #B3907A  acento principal (mocha) — antes terracota
La paleta no incluye un tono oscuro, así que se usa #3A2E22 (café
oscuro) para texto y bordes fuertes, buscando buen contraste.
"""

import streamlit as st

from config import FUENTE

# IMPORTANTE: ni una sola línea en blanco dentro de CSS. Una línea en
# blanco corta el bloque <style> a la mitad en el renderizador de
# Streamlit y el resto del CSS aparece como texto visible en pantalla.
CSS = """
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@600;700;800&family=Work+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] { font-family: 'Work Sans', sans-serif; color-scheme: light only; }
.icono-svg { vertical-align: middle; flex-shrink: 0; }
.stApp { background: #F5F5EB !important; }
header[data-testid="stHeader"] { background: transparent; }
/* ---------- Compatibilidad modo claro/oscuro del sistema ---------- */
[data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"], li[role="option"], [data-testid="stExpander"], [data-testid="stExpanderDetails"], section[data-testid="stFileUploaderDropzone"] { background-color: #FFFFFF !important; color: #3A2E22 !important; }
[data-baseweb="popover"] *, [data-baseweb="menu"] *, li[role="option"] * { color: #3A2E22 !important; }
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span, [data-testid="stWidgetLabel"] *, .stFileUploader small, div[data-testid="stFileUploaderDropzoneInstructions"] span, div[data-testid="stFileUploaderDropzoneInstructions"] small, .stCaptionContainer, [data-testid="stCaptionContainer"] { color: #3A2E22 !important; }
.stMain .stMarkdown p:not([style]):not(.subtitulo) { color: #3A2E22 !important; }
/* ---------- Radios y opciones dentro del contenido principal (cuestionario, etc.) ---------- */
.stMain div[data-testid="stRadio"], .stMain div[data-testid="stRadio"] * { color: #3A2E22 !important; }
.stMain div[data-testid="stRadio"] label:has(input:checked) p { color: #B3907A !important; font-weight: 700; }
/* ---------- Multiselect: tarjeta clara, tags color acento ---------- */
div[data-testid="stMultiSelect"] div[data-baseweb="select"] { background-color: transparent !important; border: none !important; }
div[data-testid="stMultiSelect"] div[data-baseweb="select"] *:not([data-baseweb="tag"]):not([data-baseweb="tag"] *) { background-color: transparent !important; }
div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div { border: 2px solid #E1DACA !important; border-radius: 12px !important; background-color: #FFFDF9 !important; padding: .4rem !important; }
[data-baseweb="tag"] { background-color: #B3907A !important; border: none !important; border-radius: 8px !important; margin: .2rem !important; }
[data-baseweb="tag"] span { color: #FFFFFF !important; font-weight: 600; }
[data-baseweb="tag"] svg { fill: #FFFFFF !important; opacity: .85; }
/* ---------- Encabezado tipo afiche ---------- */
.hero { padding: 2rem 2.3rem; border: 3px solid #3A2E22; color: #3A2E22 !important; margin-bottom: 1.4rem; background: #EFE7DA !important; position: relative; overflow: hidden; }
.hero::after { content: ""; position: absolute; left: 0; bottom: 0; width: 100%; height: 8px; background: repeating-linear-gradient(90deg, #B3907A 0 22px, #C1B6A3 22px 44px); }
.hero .eyebrow { text-transform: uppercase; letter-spacing: .16em; font-size: .72rem; font-weight: 700; color: #B3907A !important; }
.hero h1 { color: #3A2E22 !important; margin: .3rem 0; font-size: 2rem; font-weight: 800; font-family: 'Bitter', Georgia, serif; }
.hero p { color: #5C4E3F !important; opacity: 1; font-size: .98rem; max-width: 760px; line-height: 1.5; }
/* ---------- Navegación horizontal (pestañas) ---------- */
div[data-testid="stRadio"][aria-label="nav-principal"], .nav-principal div[data-testid="stRadio"] { margin-bottom: .3rem; }
.nav-principal div[role="radiogroup"] { display: flex; flex-wrap: wrap; gap: .5rem; border-bottom: 3px solid #E1DACA; padding-bottom: .1rem; }
.nav-principal div[role="radiogroup"] label, .nav-principal div[role="radiogroup"] label * { background: transparent !important; border: none !important; border-radius: 0 !important; font-weight: 700; color: #8C7B68 !important; }
.nav-principal div[role="radiogroup"] label { padding: .5rem .3rem !important; margin: 0 .55rem -3px 0 !important; border-bottom: 3px solid transparent !important; }
.nav-principal div[role="radiogroup"] label:has(input:checked), .nav-principal div[role="radiogroup"] label:has(input:checked) * { color: #B3907A !important; }
.nav-principal div[role="radiogroup"] label:has(input:checked) { border-bottom: 3px solid #B3907A !important; }
/* ---------- Tarjetas: bordes sólidos, sin sombra, esquinas rectas ---------- */
.card { background: #EFE7DA; border: 2px solid #3A2E22; padding: 1.5rem 1.7rem; margin-bottom: 1.3rem; }
.card h2 { font-size: 1.12rem; font-weight: 800; color: #3A2E22; margin: 0 0 .3rem 0; font-family: 'Bitter', Georgia, serif; display: flex; align-items: center; gap: .5rem; }
.card h2 .icono-svg { color: #B3907A; }
.card .subtitulo { color: #5C4E3F !important; font-size: .89rem; margin-bottom: 1rem; line-height: 1.5; }
/* ---------- Casillas de verificación como tarjetas (selección de preguntas) ---------- */
div[data-testid="stCheckbox"] { border: 2px solid #E1DACA; border-radius: 10px; padding: .55rem .8rem; margin-bottom: .5rem; background: #FFFDF9; }
div[data-testid="stCheckbox"]:has(input:checked) { border-color: #B3907A; background: #F3E9DF; }
div[data-testid="stCheckbox"] label p { font-size: .85rem !important; line-height: 1.35; color: #3A2E22 !important; }
/* ---------- Métricas ---------- */
div[data-testid="stMetric"] { background: #F5F0E4; border: 2px solid #3A2E22; border-left: 8px solid #B3907A; padding: .9rem 1rem .6rem; }
div[data-testid="stMetricValue"] { color: #B3907A; font-weight: 800; font-family: 'Bitter', Georgia, serif; }
div[data-testid="stMetricLabel"] { text-transform: uppercase; letter-spacing: .04em; font-size: .74rem !important; color: #5C4E3F !important; }
/* ---------- Botones ---------- */
.stButton>button, .stDownloadButton>button { border-radius: 0; font-weight: 700; border: 2px solid #3A2E22; padding: .55rem 1.3rem; text-transform: uppercase; letter-spacing: .03em; font-size: .8rem; }
.stButton>button { background: #B3907A !important; color: #FFFFFF !important; }
.stButton>button:hover { background: #3A2E22 !important; border-color: #3A2E22 !important; color: #EFE7DA !important; }
.stDownloadButton>button { background: #FFFFFF; color: #3A2E22; }
.stDownloadButton>button:hover { background: #C1B6A3; color: #3A2E22 !important; border-color: #3A2E22; }
.boton-siguiente { display: flex; justify-content: flex-end; margin-top: .8rem; }
/* ---------- Tablas ---------- */
div[data-testid="stDataFrame"] { border: 2px solid #3A2E22; overflow: hidden; }
/* ---------- Alertas / chips ---------- */
.error-box { background: #FBEAE4; border: 2px solid #A85A3A; padding: 1rem 1.2rem; color: #6B3620 !important; display: flex; align-items: flex-start; gap: .6rem; }
.cluster-chip { display: inline-flex; align-items: center; gap: .35rem; padding: .5rem 1rem; border: 2px solid #3A2E22; font-weight: 700; background: #EFE7DA; color: #3A2E22; margin: 0 .5rem .55rem 0; font-size: .85rem; }
.cluster-chip:nth-child(2n) { border-color: #C1B6A3; }
.cluster-chip:nth-child(3n) { border-color: #B3907A; }
/* ---------- Ficha de modelo guardado (historial) ---------- */
.ficha-modelo, .ficha-modelo * { color: #3A2E22 !important; }
.ficha-modelo { border: 2px solid #3A2E22; border-left: 8px solid #B3907A; background: #FFFFFF; padding: 1rem 1.2rem; margin-bottom: .9rem; }
.ficha-modelo .fila-meta { display: flex; align-items: center; gap: .45rem; margin-bottom: .25rem; }
.ficha-modelo .fila-meta .icono-svg { color: #B3907A !important; }
.ficha-modelo .ruta { font-family: 'Courier New', monospace; font-size: .82rem; background: #EFE7DA; padding: .15rem .5rem; display: inline-block; margin-top: .3rem; }
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
    "graphic_eq": '<circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/>',
    "folder_open": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    "folder": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    "table_view": '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>',
    "filter_alt": '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    "tune": '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
    "bar_chart": '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    "model_training": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "history": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "schedule": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "insights": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "recommend": '<path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>',
    "error": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "headphones": '<path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>',
    "arrow_forward": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
}


def icono(nombre, tamano=20):
    """Icono SVG en línea (sin emoji, sin depender de fuentes externas).
    Solo funciona dentro de HTML renderizado con unsafe_allow_html=True."""
    trazos = _ICONOS_SVG.get(nombre, "")
    return (
        f'<svg class="icono-svg" xmlns="http://www.w3.org/2000/svg" width="{tamano}" height="{tamano}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{trazos}</svg>'
    )


def card_abierta(icono_nombre, titulo, subtitulo=None):
    sub = f'<p class="subtitulo">{subtitulo}</p>' if subtitulo else ""
    st.markdown(f'<div class="card"><h2>{icono(icono_nombre, 20)}{titulo}</h2>{sub}', unsafe_allow_html=True)


def card_cerrada():
    st.markdown("</div>", unsafe_allow_html=True)


def mensaje_error(texto):
    st.markdown(f'<div class="error-box">{icono("error", 20)}<div>{texto}</div></div>', unsafe_allow_html=True)


def estilizar_tabla(df):
    """Degradado café claro y suave (no colores saturados)."""
    try:
        cols_num = df.select_dtypes("number").columns
        return df.style.background_gradient(subset=cols_num, cmap="copper_r", low=0.15, high=0.55).format(precision=2)
    except Exception:
        return df


def tema_plotly(fig, altura=340):
    fig.update_layout(
        font=dict(family=FUENTE, size=12, color="#3A2E22"), height=altura,
        margin=dict(t=45, b=15, l=15, r=15), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", y=1.12, font=dict(size=11, color="#3A2E22")),
        title_font=dict(size=14, color="#3A2E22", family="Bitter, Georgia, serif"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#3A2E22", tickfont=dict(color="#3A2E22", size=11))
    fig.update_yaxes(showgrid=True, gridcolor="#E1DACA", linecolor="#3A2E22", tickfont=dict(color="#3A2E22", size=11))
    return fig
