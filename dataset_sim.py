import pandas as pd
import numpy as np

np.random.seed(42)

archivo = "resultados_clusters.csv"

cantidad = int(input("Cantidad de registros a generar: "))

df = pd.read_csv(archivo)

# Eliminar marca temporal
df = df.drop(columns=["Marca temporal"], errors="ignore")

# Solo columnas numéricas
numericas = df.select_dtypes(include=np.number)

nuevo_df = pd.DataFrame()

for columna in numericas.columns:

    media = numericas[columna].mean()
    desviacion = numericas[columna].std()

    minimo = numericas[columna].min()
    maximo = numericas[columna].max()

    datos = np.random.normal(
        media,
        desviacion,
        cantidad
    )

    # Convertir a enteros
    datos = np.rint(datos)

    # Respetar rango original
    datos = np.clip(datos, minimo, maximo)

    nuevo_df[columna] = datos.astype(int)

nuevo_df.to_csv("datos_simetricos.csv", index=False)

print("Datos generados correctamente.")