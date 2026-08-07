"""Etiquetas cortas para las preguntas de la encuesta y detección de
columnas especiales (marca temporal, música, género, edad)."""

import unicodedata

import pandas as pd

# Las preguntas de la encuesta son largas ("2. Disfruto iniciar
# conversaciones con personas que acabo de conocer."). Este mapa
# genera una etiqueta corta y descriptiva por cada columna.
MAPA_ETIQUETAS = [
    (["conversaciones", "personas que acabo de conocer"], "Extraversión"),
    (["espacio de trabajo", "limpio y ordenado"], "Organización"),
    (["adapto rapidamente", "cambian mis planes"], "Adaptabilidad"),
    (["soluciones originales", "diferentes"], "Creatividad"),
    (["persisto en mis tareas", "dificiles"], "Perseverancia"),
    (["ofrezco mi ayuda", "equipo"], "Empatía"),
    (["calma", "presion"], "Calma bajo presión"),
    (["decisiones", "rapidez y seguridad"], "Decisión"),
    (["centro de atencion", "eventos colectivos"], "Sociabilidad"),
    (["planifico detalladamente", "actividades diarias"], "Planificación"),
    (["formas nuevas", "inusuales"], "Apertura a lo nuevo"),
    (["compromiso", "meta a largo plazo"], "Constancia"),
    (["bienestar general del grupo"], "Colectivismo"),
    (["control emocional", "contratiempo"], "Resiliencia"),
    (["responsabilidad directiva", "situacion ambigua"], "Liderazgo"),
    (["edad"], "Edad"),
    (["rock"], "Gusto por el Rock"),
    (["pop"], "Gusto por el Pop"),
    (["electronica"], "Gusto por la Electrónica"),
    (["clasica", "instrumental"], "Gusto por la Clásica/Instrumental"),
    (["trabajo o estudio"], "Música al estudiar/trabajar"),
    (["relajarme"], "Música para relajarse"),
    (["descubro musica nueva"], "Exploración musical"),
    (["letra de una cancion"], "Importancia de la letra"),
    (["todos los dias"], "Frecuencia de escucha"),
]

ADJETIVO_POR_RASGO = {
    "Extraversión": "Extrovertidos", "Organización": "Organizados", "Adaptabilidad": "Adaptables",
    "Creatividad": "Creativos", "Perseverancia": "Perseverantes", "Empatía": "Empáticos",
    "Calma bajo presión": "Calmados", "Decisión": "Decididos", "Sociabilidad": "Sociables",
    "Planificación": "Planificadores", "Apertura a lo nuevo": "Curiosos", "Constancia": "Constantes",
    "Colectivismo": "Solidarios", "Resiliencia": "Resilientes", "Liderazgo": "Líderes",
}


def normalizar(texto):
    """Minúsculas y sin acentos, para comparar sin importar tildes."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(ch for ch in texto if not unicodedata.combining(ch))


def obtener_etiquetas_cortas(columnas):
    etiquetas, usadas = {}, {}
    for col in columnas:
        col_norm = normalizar(col)
        etiqueta = next((n for claves, n in MAPA_ETIQUETAS if any(k in col_norm for k in claves)), None)
        if etiqueta is None:
            texto = col.split(".", 1)[-1].strip() if "." in col[:4] else col
            etiqueta = " ".join(texto.split()[:4]).capitalize() or col
        usadas[etiqueta] = usadas.get(etiqueta, 0) + 1
        etiquetas[col] = etiqueta if usadas[etiqueta] == 1 else f"{etiqueta} ({usadas[etiqueta]})"
    return etiquetas


def detectar_columnas_musica(columnas):
    return [c for c in columnas if any(p in normalizar(c) for p in ("musica", "cancion"))]


def detectar_columnas_genero(columnas):
    mapa = {"Rock": ["rock"], "Pop": ["pop"], "Electrónica": ["electronica"], "Clásica / Instrumental": ["clasica", "instrumental"]}
    encontrados = {}
    for genero, claves in mapa.items():
        col = next((c for c in columnas if any(k in normalizar(c) for k in claves)), None)
        if col:
            encontrados[genero] = col
    return encontrados


def detectar_columna_edad(columnas):
    return next((c for c in columnas if "edad" in normalizar(c) or "age" in normalizar(c)), None)


def derivar_filtros_categoricos(df):
    """A partir de las respuestas numéricas ya existentes, arma categorías
    de filtro más naturales para la persona que usa la app (en vez de
    filtrar columna por columna). Devuelve un diccionario
    {nombre_filtro: pd.Series} — cada Serie tiene el mismo índice que df.
    Solo se derivan categorías que SÍ se pueden calcular con las preguntas
    actuales de la encuesta; otras categorías típicas (estado de ánimo,
    plataforma, instrumento favorito) requerirían agregar esas preguntas
    al formulario, así que no se inventan aquí."""
    columnas = df.columns.tolist()
    filtros = {}

    # --- Tipo de personalidad: a partir de Extraversión + Sociabilidad ---
    col_extra = next((c for c in columnas if "conversaciones" in normalizar(c)), None)
    col_socia = next((c for c in columnas if "centro de atencion" in normalizar(c)), None)
    cols_extraversion = [c for c in (col_extra, col_socia) if c]
    if cols_extraversion:
        promedio = df[cols_extraversion].mean(axis=1)
        filtros["Tipo de personalidad"] = pd.cut(
            promedio, bins=[0, 2.5, 3.5, 5.01],
            labels=["Introvertido", "Ambivertido", "Extrovertido"], include_lowest=True,
        ).astype(str)

    # --- Rango de edad ---
    col_edad = detectar_columna_edad(columnas)
    if col_edad:
        filtros["Rango de edad"] = pd.cut(
            df[col_edad], bins=[0, 20, 25, 30, 200],
            labels=["15-20", "21-25", "26-30", "31+"], include_lowest=True,
        ).astype(str)

    # --- Frecuencia de escucha: a partir de "Escucho música todos los días" ---
    col_frecuencia = next((c for c in columnas if "todos los dias" in normalizar(c)), None)
    if col_frecuencia:
        filtros["Frecuencia de escucha"] = pd.cut(
            df[col_frecuencia], bins=[0, 2, 3.5, 5.01],
            labels=["Ocasional", "Semanal", "Diario"], include_lowest=True,
        ).astype(str)

    # --- Género musical favorito: el de mayor puntuación por persona ---
    generos = detectar_columnas_genero(columnas)
    if generos:
        sub = df[list(generos.values())].rename(columns={v: k for k, v in generos.items()})
        filtros["Género musical favorito"] = sub.idxmax(axis=1)

    return filtros


def eliminar_marca_temporal(df):
    cols = [c for c in df.columns if "marca temporal" in normalizar(c) or normalizar(c).strip() == "timestamp"]
    return df.drop(columns=cols) if cols else df