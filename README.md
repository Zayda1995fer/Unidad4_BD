# Personalidad & Hábitos Musicales — Análisis No Supervisado (K-Means)

App en Python (Streamlit) que cumple con los requisitos de la Actividad 1
de la Unidad IV: carga de datos, filtros, estadística descriptiva propia,
entrenamiento de K-Means, nombrado automático de los perfiles resultantes,
y un cuestionario final que recomienda un género musical según tu perfil.

## 1. Instalación

```bash
pip install -r requirements.txt
```

## 2. Ejecutar la app

```bash
streamlit run app.py
```

Se abre en el navegador, normalmente en `http://localhost:8501`.

## 3. Estructura del proyecto

```
app.py              orquesta la navegación lateral (7 secciones)
config.py           constantes compartidas (paleta, mínimos, carpeta de modelos)
styles.py           CSS y utilidades visuales (sidebar, tarjetas, tema de Plotly)
etiquetas.py        etiquetas cortas de las preguntas + detección de columnas especiales
estadistica.py      media, mediana, moda, desviación y rango — implementación propia
modelo.py           método del codo, guardado de modelos y nombrado de clusters
vistas.py           una función por sección de la interfaz
.streamlit/
  config.toml       tema de colores de Streamlit (paleta pastel: lavanda + morado + rosa)
modelos_guardados/  se crea sola al entrenar; guarda cada modelo .pkl con fecha y metadata
```

La navegación es un **menú lateral** (no pestañas horizontales): al elegir una
sección en la barra morada de la izquierda, solo esa sección se dibuja. Los
datos cargados y los filtros aplicados se conservan en `st.session_state`
para que sigan disponibles al cambiar de sección.

La sección **📊 Estadística** muestra únicamente las variables numéricas
(tabla + gráfica de media/desviación); no incluye una vista separada para
columnas categóricas.

## 4. Cómo usar tus datos de encuesta

1. Exporta las respuestas de tu encuesta (Google Forms → Respuestas → Hoja de
   cálculo → Archivo → Descargar → CSV).
2. Sube ese CSV en la sección **📂 Datos**. La columna "Marca temporal" se
   elimina automáticamente.
3. En **🔍 Filtros**, acota la muestra por categoría o rango si lo necesitas.
4. En **📊 Estadística**, revisa media, mediana, moda, desviación y rango —
   calculados con funciones propias, sin `pandas.describe()`.
5. En **🤖 Entrenamiento**, elige las características, revisa el método del
   codo, define k y entrena. Cada entrenamiento:
   - Crea un archivo **nuevo** `modelo_AAAAMMDD_HHMMSS.pkl` dentro de
     `modelos_guardados/` (nunca sobrescribe uno anterior).
   - Guarda junto con el modelo: el scaler, las variables usadas, la fecha,
     los **filtros que estaban activos**, el número de registros y el
     Silhouette Score.
6. En **📈 Resultados**, cada cluster aparece con un **nombre automático**
   (ej. "Extrovertidos y Creativos") calculado por z-score de sus rasgos
   más distintivos, no solo los más altos en promedio.
7. En **🎯 Recomendador**, responde el cuestionario y descubre tu perfil y
   el género musical recomendado.
8. En **🗂️ Historial**, consulta todos los modelos entrenados hasta ahora
   — con fecha, filtros, k, Silhouette Score y la **ruta completa en disco**
   de cada archivo `.pkl`.

## 5. Dónde se guarda el modelo

Cada modelo se guarda como archivo **`.pkl`** (formato *pickle*, escrito con
`joblib.dump`) dentro de la carpeta **`modelos_guardados/`**, ubicada en el
mismo directorio donde corre `app.py` (la ruta exacta y absoluta se muestra
en pantalla justo después de entrenar, y también en la sección Historial).
El nombre incluye la fecha y hora exactas del entrenamiento, así que entrenar
varias veces no borra los modelos anteriores.

Puedes cargar cualquiera de esos archivos de vuelta (sección 📈 Resultados →
"Cargar un modelo ya entrenado") incluso sin tener el CSV original a la mano.

## 6. Notas para la entrega

- Para el repositorio, sube el `.pkl` que quieras entregar como final desde
  `modelos_guardados/` (la carpeta está en `.gitignore` por defecto para no
  llenar el repo de versiones de prueba — usa `git add -f` sobre el archivo
  específico que quieras conservar).
- Para la exposición: carga → filtros → estadística → método del codo →
  entrenar → resultados con nombres de cluster → recomendador → historial.
