# App de Análisis No Supervisado — Perfiles de Personalidad

Aplicación en Python (Streamlit) que cumple con los requisitos de la **Actividad 1**
de la Unidad IV (Análisis No Supervisado): carga de datos, exploración, filtros,
estadística básica, entrenamiento de un algoritmo no supervisado, generación de
resultados y descarga de datos/resultados.

## 1. Instalación

```bash
pip install -r requirements.txt
```

## 2. Ejecutar la app

```bash
streamlit run app.py
```

Se abrirá en tu navegador (normalmente en `http://localhost:8501`).

## 3. Cómo usar tus datos de encuesta

1. Exporta las respuestas de tu encuesta en línea (Google Forms → Respuestas →
   Hoja de cálculo → Archivo → Descargar → CSV; o directo desde Typeform/otro).
2. En la app, sube ese CSV en la sección **"1. Carga de datos"**.
   - También puedes marcar "Usar dataset de ejemplo" para probar la app primero
     con `encuesta_personalidad_ejemplo.csv` (datos simulados tipo Big Five).
3. Explora tus datos, aplica filtros por categoría (género, rango de edad, etc.).
4. Revisa la estadística básica (media, mediana, moda, desviación estándar, etc.
   calculada manualmente, sin usar funciones ya empaquetadas).
5. Elige las variables numéricas (rasgos de personalidad) y el algoritmo:
   - K-Means
   - Clusterización Jerárquica
   - DBSCAN
   - Modelo de Agrupamiento Gaussiano (GMM)
6. Da clic en **"Entrenar modelo"**. Esto:
   - Entrena el algoritmo
   - Guarda el modelo en `modelo_personalidad.pkl` (para uso posterior)
   - Asigna un cluster a cada persona (posible "tipo de personalidad")
   - Muestra una gráfica 2D (PCA, reducción de dimensionalidad) de los grupos
7. Descarga los datos filtrados y los resultados con los botones de descarga.

## 4. Notas para la entrega

- El modelo entrenado (`modelo_personalidad.pkl`) es el archivo que debes subir
  al repositorio que pide el documento ("Entrega el modelo de agrupación... en
  un repositorio según la herramienta de software utilizada").
- Recuerda ajustar las columnas de tu encuesta real (nombres de preguntas) —
  la app detecta automáticamente cuáles son numéricas y cuáles categóricas.
- Para la exposición en clase, puedes mostrar en vivo: carga → filtro →
  estadística → entrenamiento → resultados → descarga.
