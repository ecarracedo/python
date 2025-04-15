import os  # Importa el módulo os para interactuar con el sistema operativo
import pandas as pd  # Importa pandas para la manipulación de datos
import matplotlib.pyplot as plt  # Importa matplotlib para la creación de gráficos
import numpy as np  # Importa numpy para operaciones con arreglos y números

# Parámetros
precio_strike = 3910  # Precio de strike de la opción (precio de ejercicio)
prima = 158  # Prima de la opción (el costo de la opción)
cant_contratos = 1  # Cantidad de contratos vendidos
rango = 40  # Rango de precios alrededor del precio de equilibrio para analizar

# Código alternativo para entrada de datos por teclado (descomentar si se prefiere y comentar el código de arriba en Parámetros)
"""
precio_strike = int(input("Introduce el strike: "))
prima = float(input("Introduce la prima: "))
cant_contratos = int(input("Introduce la cantidad de contratos: "))
rango = int(input("Introduce el rango: "))
"""

# Punto de equilibrio
punto_equilibrio = precio_strike + prima  # El punto donde la ganancia es igual a la prima recibida

# Rango de precios centrado en el punto de equilibrio
precios = np.arange(punto_equilibrio - rango*8, punto_equilibrio + rango*10, rango)  # Rango de precios en pasos de 'rango' alrededor del punto de equilibrio
if punto_equilibrio not in precios:  # Verifica si el punto de equilibrio ya está en el rango de precios
    precios = np.append(precios, punto_equilibrio)  # Si no está, lo agrega
    precios = np.sort(precios)  # Ordena el arreglo de precios de menor a mayor

# Cálculo del payoff (ganancia/pérdida)
datos = []  # Lista vacía para almacenar los resultados
for precio_sub in precios:  # Itera sobre cada precio en el rango de precios
    # Fórmula para venta de CALL: prima - max(0, precio_sub - precio_strike)
    # Es el opuesto del payoff de compra de CALL
    resultado = prima - max(0, precio_sub - precio_strike)
    datos.append([precio_sub, resultado * cant_contratos])  # Agrega el precio y el resultado al listado de datos

# Crear DataFrame de pandas con los datos
df = pd.DataFrame(datos, columns=['Precio Sub', 'Resultado'])  # Convierte los datos a un DataFrame para mejor manejo

# Obtener la ruta del directorio donde se encuentra este script
directorio_actual = os.path.dirname(os.path.abspath(__file__))

# Crear la carpeta de resultados al mismo nivel que el script
carpeta_resultados = os.path.join(directorio_actual, 'resultados')  # Define la ruta completa de la carpeta

# Verificar si la carpeta no existe y crearla si es necesario
if not os.path.exists(carpeta_resultados):  # Verifica si la carpeta no existe
    os.makedirs(carpeta_resultados)  # Si no existe, la crea

# Gráfico de resultados
plt.figure(figsize=(10, 6))  # Define el tamaño del gráfico (más compacto)

# Líneas guía en el gráfico
plt.axhline(y=0, color='blue', linestyle='--')  # Línea horizontal para el punto de equilibrio
plt.axhline(y=prima, color='green', linestyle='--', label='Ganancia máxima')  # Línea horizontal para la ganancia máxima
plt.axvline(x=punto_equilibrio, color='blue', linestyle='--', label='Punto de equilibrio')  # Línea vertical para el punto de equilibrio

# Línea principal del gráfico
plt.plot(df['Precio Sub'], df['Resultado'], marker='o', color='black', label='Payoff Opción')  # Plotea el payoff de la opción

# Personalización del gráfico
plt.xticks(df['Precio Sub'], rotation=60, fontsize=12)  # Rotación de las etiquetas del eje X para mejor visualización

# Eje Y: Utilizamos los resultados calculados en la tabla como ticks en el eje Y
yticks = np.unique(df['Resultado'])  # Obtiene los valores únicos de los resultados para los ticks del eje Y
plt.yticks(yticks, fontsize=12)  # Establece los valores del eje Y según los resultados

plt.ylim(min(yticks) - 10, max(yticks) + 10)  # Establece los límites del eje Y con un pequeño margen

# Etiquetas y leyenda
plt.xlabel('Precio Subyacente', fontsize=14)  # Etiqueta para el eje X
plt.ylabel('Ganancia / Pérdida', fontsize=14)  # Etiqueta para el eje Y
plt.title('Resultado de una Venta de CALL', fontsize=16)  # Título del gráfico
plt.grid(color='gray', linestyle='--', linewidth=0.5)  # Añade una cuadrícula ligera en el gráfico
plt.legend(fontsize=12)  # Muestra la leyenda con una fuente de tamaño 12
plt.tight_layout(pad=2)  # Ajusta el espacio en el gráfico para evitar que las etiquetas se corten

# Guardar el gráfico como imagen
nombre_imagen = f"{precio_strike}_venta_call_grafico.png"
ruta_imagen = os.path.join(carpeta_resultados, nombre_imagen)
plt.savefig(ruta_imagen, dpi=300, bbox_inches='tight')
plt.show()  # Muestra el gráfico

# Mostrar DataFrame en la consola
print("\nTabla de ganancias y pérdidas:")
print(df)  # Imprime el DataFrame con los resultados

# Exportar directamente a Excel dentro de la carpeta de resultados
nombre_archivo = f"{precio_strike}_venta_call_tabla_PL.xlsx"  # Define el nombre del archivo Excel
ruta_archivo = os.path.join(carpeta_resultados, nombre_archivo)  # Crea la ruta completa del archivo
df.to_excel(ruta_archivo, index=False)  # Guarda el DataFrame en un archivo Excel en la ruta especificada

# Mensaje de confirmación
print(f"\n✅ El resultado se exportó a Excel como: {ruta_archivo}")  # Imprime el mensaje de éxito
print(f"✅ El gráfico se guardó como: {ruta_imagen}")  # Imprime el mensaje de éxito para la imagen 