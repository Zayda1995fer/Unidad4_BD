"""CSS/HTML de la aplicación y utilidades visuales reutilizables."""

import streamlit as st

from config import FUENTE

# Las constantes de HTML/CSS se escriben SIN sangría (empiezan en la
# columna 0) para que Streamlit las trate como HTML y no como un
# bloque de código (Markdown convierte 4+ espacios iniciales en un
# bloque <code> literal). Los colores usan las variables de tema de
# Streamlit (--background-color, --secondary-background-color,
# --text-color) para que la app respete el modo claro/oscuro elegido
# por la persona, en vez de forzar siempre un tema fijo.
CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: var(--background-color); }
header[data-testid="stHeader"] { background: var(--background-color); }
.hero {
padding: 2.2rem 2.4rem; border-radius: 20px; color: white; margin-bottom: 1.6rem;
background: linear-gradient(120deg, #0F172A 0%, #1E293B 45%, #4338CA 100%);
box-shadow: 0 12px 30px rgba(15,23,42,0.35); position: relative; overflow: hidden;
}
.hero::before {
content: ""; position: absolute; top: -60px; right: -60px; width: 220px; height: 220px;
background: radial-gradient(circle, rgba(79,70,229,0.35) 0%, rgba(79,70,229,0) 70%);
}
.hero .eyebrow, .hero h1, .hero p { position: relative; z-index: 1; }
.hero .eyebrow { text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; font-weight: 700; color: #A5B4FC !important; }
.hero h1 { color: #FFFFFF !important; margin: .3rem 0; font-size: 1.9rem; font-weight: 800; }
.hero p { color: #F1F0FB !important; opacity: .92; font-size: .98rem; max-width: 720px; line-height: 1.5; }
.card { background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,.25); border-radius: 16px; padding: 1.5rem 1.6rem; margin-bottom: 1.3rem; box-shadow: 0 1px 3px rgba(0,0,0,.06); }
.card h2 { font-size: 1.08rem; font-weight: 700; color: var(--text-color); margin: 0 0 .3rem 0; }
.card .subtitulo { color: var(--text-color); opacity: .65; font-size: .88rem; margin-bottom: 1rem; line-height: 1.5; }
div[data-testid="stMetric"] { background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,.25); border-radius: 14px; padding: .9rem 1rem .7rem; }
div[data-testid="stMetricValue"] { color: #6D5EF0; font-weight: 800; }
.stButton>button, .stDownloadButton>button { border-radius: 10px; font-weight: 600; border: none; padding: .55rem 1.3rem; }
.stButton>button { background: linear-gradient(120deg, #4338CA, #4F46E5); color: white !important; }
.stDownloadButton>button { background: var(--secondary-background-color); color: #6D5EF0; border: 1px solid rgba(109,94,240,.4); }
button[data-baseweb="tab"][aria-selected="true"] { color: #6D5EF0; }
div[data-baseweb="tab-highlight"] { background-color: #6D5EF0; }
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid rgba(128,128,128,.25); }
.error-box { background: rgba(239,68,68,.12); border: 1px solid #EF4444; border-radius: 12px; padding: 1rem 1.2rem; color: #EF4444 !important; }
.cluster-chip { display: inline-block; padding: .55rem 1rem; border-radius: 12px; font-weight: 700; background: rgba(109,94,240,.15); color: #6D5EF0; margin: 0 .4rem .6rem 0; }
</style>
"""

HERO = """
<div class="hero">
<div class="eyebrow">Unidad IV · Análisis No Supervisado</div>
<h1>🎼 Personalidad y Hábitos Musicales</h1>
<p>Agrupa perfiles de personalidad con gustos musicales afines usando K-Means, y descubre qué género
va mejor con tu forma de ser.</p>
</div>
"""


def card_abierta(titulo, subtitulo=None):
    sub = f'<p class="subtitulo">{subtitulo}</p>' if subtitulo else ""
    st.markdown(f'<div class="card"><h2>{titulo}</h2>{sub}', unsafe_allow_html=True)


def card_cerrada():
    st.markdown("</div>", unsafe_allow_html=True)


def estilizar_tabla(df):
    try:
        return df.style.background_gradient(subset=df.select_dtypes("number").columns, cmap="Purples").format(precision=2)
    except Exception:
        return df


def tema_plotly(fig, altura=340):
    fig.update_layout(
        font=dict(family=FUENTE, size=12, color="#1F2937"), height=altura,
        margin=dict(t=45, b=15, l=15, r=15), plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", y=1.12, font=dict(size=11)), title_font=dict(size=14, color="#1E1B4B"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#F1F0FB")
    return fig