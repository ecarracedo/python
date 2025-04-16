
# Scraper de Agencias de Viaje en Argentina 🇦🇷

Este proyecto permite extraer información de agencias de viaje registradas en [https://www.agenciasdeviajes.ar/](https://www.agenciasdeviajes.ar/) utilizando `Playwright` en un entorno como Google Colab.

## 📌 Descripción

El script automatiza la navegación por la página oficial de agencias de viaje, buscando por provincia y extrayendo información útil como:

- Nombre de la agencia
- Teléfono
- Correo electrónico
- Localidad
- Provincia

Los datos se guardan automáticamente en:

- Un archivo `.CSV` (local)
- Un archivo `.XLSX` en Google Drive

Existen dos versiones de archivos con extensión `.py`:

- `web_scraping-rnav.py`: Versión para ejecutar en la PC, sin conexión a Google Drive
- `web_scraping-rnav_colab-jupiter.py`: Versión para ejecutar en Google Colab o Jupyter

## 🧰 Tecnologías utilizadas

- `Playwright` → Para automatizar la navegación por la web
- `asyncio` → Para gestionar tareas asíncronas
- `pandas` → Para exportar los datos a Excel
- `google.colab` → Para montar Google Drive
- `nest_asyncio` → Permite ejecutar bucles asíncronos dentro de notebooks de Colab
- `email-validator` → Para validar correos electrónicos

## ⚙️ Requisitos previos

Antes de ejecutar el script, asegurate de instalar y configurar:

```bash
pip install playwright nest_asyncio pandas email-validator
playwright install
```

Además, montá Google Drive en Colab con:

```python
from google.colab import drive
drive.mount('/content/drive')
```

## 🧠 Cómo funciona

1. El usuario ingresa la **provincia** a consultar.
2. El navegador se abre en segundo plano y navega al sitio.
3. Se escribe la provincia en el buscador.
4. Se recorren todas las páginas de resultados.
5. Por cada agencia, se extraen los datos desde su bloque HTML.
6. Si aparece un **modal emergente (pop-up)**, se cierra automáticamente para no interrumpir la navegación.
7. Antes de guardar los resultados, se realiza un proceso de normalización de correos.
8. Finalmente, se guardan los resultados en CSV y XLXS(opcional).

## ✉️ Normalización y corrección de correos electrónicos

Durante el proceso de scraping, los correos electrónicos extraídos son normalizados automáticamente para corregir errores comunes como:

- Faltante del símbolo `@`
- Dominios incompletos como `gmail` en lugar de `@gmail.com`
- Sustituciones como `(at)`, `[arroba]`, etc.
- Caracteres especiales no válidos

Esta normalización se realiza con la función:

```python
normalizar_correo(correo: str) -> str
```

Si un correo no puede ser validado automáticamente, se almacena junto con el nombre de la agencia para su revisión posterior.

---

### 🛠 Corrección manual de correos

Al finalizar el scraping, si hay correos inválidos, se listan y se ofrece la opción de corregirlos manualmente con:

```python
corregir_correos_invalidos()
```

Este proceso permite:

- Ver el nombre de la agencia asociada al correo inválido
- Ingresar una corrección válida
- Validar automáticamente el nuevo correo
- Actualizar el archivo CSV con la corrección correspondiente

---

### ⚠️ Aviso al usuario antes de guardar

En caso de que **uno o más correos no puedan ser normalizados automáticamente**, el sistema lo informará al usuario.  
Antes de guardar el archivo final, se ofrecerá la posibilidad de **modificarlos manualmente**, asegurando así que la información quede lo más completa y precisa posible.

## ⚙️ Manejo del Modal en el Scraping

Durante el scraping, la web puede mostrar un modal (ventana emergente) que interrumpe el proceso. Para evitar esto, el script incluye un bloque para cerrar automáticamente cualquier modal detectado:

```python
await page.evaluate("""
    () => {
        const modal = document.querySelector('[role=dialog]');
        if (modal) {
            window.dispatchEvent(new CustomEvent('close-modal', { detail: { id: 'video1year' }}));
        }
    }
""")
```

Esto permite que el scraping continúe sin interrupciones.

## 📦 Ejecución del script

```python
await scrapear_agencias_completo()
```

---

## 📜 Licencia

Este proyecto se publica con fines educativos y de práctica.

## 📌 Contacto

ecarracedo@gmail.com

## 📋 Changelog

### [1.4.0] - 2025-04-16  
#### Añadido  
- Asociación de correos inválidos con el nombre de la agencia durante el scraping  
- Opción para corregir manualmente correos inválidos, identificando claramente a qué agencia pertenecen  
- Validación mejorada de correos ingresados manualmente  
- Actualización automática del archivo CSV con correcciones  
- Mejora del formato de salida al mostrar correos inválidos (más legible y profesional)

#### Corregido  
- Problema donde el nombre de la agencia no se guardaba correctamente al detectar un correo inválido

### [1.3.0] - 2024-03-21  
#### Añadido  
- Mejoras en la normalización de correos electrónicos:
  - Detección y corrección de falta de @ en dominios comunes
  - Detección y corrección de falta de .com en dominios comunes
  - Reemplazo de símbolos comunes que se usan en lugar de @
  - Mejor manejo de caracteres especiales

### [1.2.0] - 2024-03-21  
#### Añadido  
- Normalización de correos electrónicos (eliminación de caracteres especiales y tildes)

### [1.1.0] - 2024-03-21  
#### Añadido  
- Menú interactivo con todas las provincias de Argentina  
- Opción para volver a ejecutar el script con otra provincia  
- Mejor manejo de errores en la selección de provincias

### [1.0.0] - 2024-03-20  
#### Añadido  
- Versión inicial del scraper  
- Extracción de datos de agencias de viaje  
- Guardado en formato CSV y Excel  
- Manejo automático de modales emergentes
