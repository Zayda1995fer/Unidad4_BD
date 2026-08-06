import pandas as pd
import numpy as np

np.random.seed(42)

archivo = "resultados_clusters.csv"

cantidad = int(input("Cantidad de registros a generar: "))

df = pd.read_csv(archivo)

# Eliminar marca temporal
df = df.drop(columns=["Marca temporal"], errors="ignore")

numericas = df.select_dtypes(include=np.number)

nuevo_df = pd.DataFrame()

for columna in numericas.columns:

    media = numericas[columna].mean()
    desviacion = numericas[columna].std()

    minimo = numericas[columna].min()
    maximo = numericas[columna].max()

    datos = np.random.normal(
        media,
        desviacion * 2.5,
        cantidad
    )

    # 5% de valores extremos
    n_outliers = max(1, round(cantidad * 0.05))

    indices = np.random.choice(cantidad, n_outliers, replace=False)

    datos[indices] += np.random.normal(
        0,
        desviacion * 5,
        n_outliers
    )

    # Redondear a enteros
    datos = np.rint(datos)

    # Mantener dentro del rango observado
    datos = np.clip(datos, minimo, maximo)

    nuevo_df[columna] = datos.astype(int)

nuevo_df.to_csv("datos_dispersos.csv", index=False)

print("Datos generados correctamente.")