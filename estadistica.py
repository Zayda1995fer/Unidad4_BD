"""Estadística descriptiva básica, implementada a mano (sin usar
pandas.describe()), tal como pide la rúbrica de la actividad."""

import pandas as pd


def media(v): return sum(v) / len(v) if v else float("nan")
def varianza(v): return sum((x - media(v)) ** 2 for x in v) / (len(v) - 1) if len(v) > 1 else float("nan")
def desviacion(v): return varianza(v) ** 0.5 if varianza(v) == varianza(v) else float("nan")


def mediana(v):
    s = sorted(v); n = len(s)
    if n == 0:
        return float("nan")
    m = n // 2
    return (s[m - 1] + s[m]) / 2 if n % 2 == 0 else s[m]


def moda(v):
    conteo = {}
    for x in v:
        conteo[x] = conteo.get(x, 0) + 1
    return max(conteo, key=conteo.get) if conteo else None


def rango(v): return max(v) - min(v) if v else float("nan")


def resumen_estadistico(df, columnas, etiquetas=None):
    filas = []
    for col in columnas:
        vals = df[col].dropna().tolist()
        filas.append({
            "característica": (etiquetas or {}).get(col, col),
            "n": len(vals),
            "media": round(media(vals), 3) if vals else None,
            "mediana": round(mediana(vals), 3) if vals else None,
            "moda": moda(vals),
            "desv_estandar": round(desviacion(vals), 3) if len(vals) > 1 else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "rango": rango(vals) if vals else None,
        })
    return pd.DataFrame(filas)