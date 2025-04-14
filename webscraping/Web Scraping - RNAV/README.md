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

## 🧰 Tecnologías utilizadas

- `Playwright` → Para automatizar la navegación por la web
- `asyncio` → Para gestionar tareas asíncronas
- `pandas` → Para exportar los datos a Excel
- `google.colab` → Para montar Google Drive
- `nest_asyncio` → Permite ejecutar bucles asíncronos dentro de notebooks de Colab

## ⚙️ Requisitos previos

Antes de ejecutar el script, asegurate de instalar y configurar:

```bash
pip install playwright nest_asyncio pandas
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
7. Finalmente, se guardan los resultados en CSV y XLSX.

## 💡 Sobre el modal emergente

El sitio a veces muestra un modal (ventana emergente) con un video o información. Esto puede interferir con los clics y el scraping.

El script detecta si hay un modal abierto mediante:

```js
const modal = document.querySelector('[role=dialog]')
```

Y si existe, lo cierra usando un `CustomEvent`:

```js
window.dispatchEvent(new CustomEvent('close-modal', { detail: { id: 'video1year' }}))
```

Esto evita bloqueos y permite continuar con el scraping.

## 📦 Ejecución del script

```python
await scrapear_agencias_completo()
```
# 🧠 Explicación línea por línea del código

Este script automatiza el scraping de agencias de viajes desde [https://www.agenciasdeviajes.ar](https://www.agenciasdeviajes.ar) usando `Playwright` y se ejecuta perfectamente en Google Colab.

---

```python
import asyncio                              # Para manejar tareas asíncronas
import csv                                  # Para guardar los datos como archivo CSV
import pandas as pd                         # Para manipulación de datos y exportación a Excel
from google.colab import drive              # Para montar Google Drive en Colab
from playwright.async_api import async_playwright, TimeoutError  # Librería principal de automatización web
```

```python
drive.mount('/content/drive')              # Monta Google Drive para poder guardar archivos directamente allí
```

---

### Función principal

```python
async def scrapear_agencias_completo():
    provincia = input("📍 Ingresá la provincia que querés buscar: ").strip()  # Solicita al usuario la provincia a buscar
```

```python
    async with async_playwright() as p:                      # Inicializa Playwright
        browser = await p.chromium.launch(headless=True)     # Lanza navegador Chromium en modo sin cabeza
        context = await browser.new_context()                # Crea nuevo contexto (como una pestaña aislada)
        page = await context.new_page()                      # Abre nueva página
```

---

### Ir a la web y buscar

```python
        await page.goto("https://www.agenciasdeviajes.ar/#buscador", timeout=30000)  # Carga la página
        await page.wait_for_selector("input[placeholder*='Ciudad o Provincia']", timeout=20000)
        await page.fill("input[placeholder*='Ciudad o Provincia']", provincia)        # Escribe la provincia
        await page.wait_for_timeout(2000)                                             # Espera a que cargue
        await page.wait_for_selector("h3.text-lg", timeout=20000)                    # Espera que aparezcan los resultados
```

---

### Extraer resultados

```python
        agencias = []             # Lista donde se guardarán los datos
        pagina = 1                # Contador de páginas

        while True:
            h3_agencias = await page.query_selector_all("h3.text-lg")  # Encuentra los títulos (nombres de agencias)
```

```python
            for h3 in h3_agencias:
                nombre = await h3.inner_text()      # Extrae el nombre de la agencia
                telefono = ""
                correo = ""
                localidad = ""

                contenedor = await h3.evaluate_handle("node => node.parentElement.parentElement")  # Va al contenedor de info
                contenedor_element = contenedor.as_element()

                if contenedor_element:
                    parrafos = await contenedor_element.query_selector_all("p.leading-relaxed.text-sm")  # Busca los párrafos de datos

                    for p in parrafos:
                        texto = await p.inner_text()
                        if "Teléfono:" in texto:
                            telefono = texto.replace("Teléfono:", "").strip()
                        if "Correo electrónico:" in texto:
                            correo = texto.replace("Correo electrónico:", "").strip()
                        if "Localidad:" in texto:
                            localidad = texto.replace("Localidad:", "").strip()
```

```python
                agencias.append({                               # Agrega los datos a la lista
                    "nombre": nombre,
                    "telefono": telefono,
                    "correo": correo,
                    "localidad": localidad,
                    "provincia": provincia
                })
```

---

### Cierre de modal (si aparece)

```python
            await page.evaluate("""                            # Ejecuta código JavaScript para cerrar un modal emergente
                () => {
                    const modal = document.querySelector('[role=dialog]');
                    if (modal) {
                        window.dispatchEvent(new CustomEvent('close-modal', { detail: { id: 'video1year' }}));
                    }
                }
            """)
```

---

### Navegación entre páginas

```python
            siguiente = page.locator("button[dusk='nextPage.after']")    # Busca el botón "Siguiente"
            if await siguiente.count() == 0 or not await siguiente.is_enabled():  # Si no hay más páginas
                break

            await siguiente.scroll_into_view_if_needed()    # Asegura que el botón esté visible
            await siguiente.click()                         # Hace clic en "Siguiente"
            await page.wait_for_timeout(2500)               # Espera a que cargue
            pagina += 1
```

---

### Guardado de datos

```python
        await browser.close()   # Cierra el navegador
```

```python
        # Guardar CSV local
        csv_filename = f"{provincia.lower().replace(' ', '_')}_agencias_viaje.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["nombre", "telefono", "correo", "localidad", "provincia"])
            writer.writeheader()
            writer.writerows(agencias)
```

```python
        # Guardar Excel en Drive
        df = pd.DataFrame(agencias)
        xlsx_path = f"/content/drive/MyDrive/EC/WebScraping/RNAV/{provincia.lower().replace(' ', '_')}_agencias_viaje.xlsx"
        df.to_excel(xlsx_path, index=False)
```

---

### Manejador de errores

```python
    except KeyboardInterrupt:
        print("❌ Ejecución interrumpida por el usuario.")
    except TimeoutError as e:
        print(f"❌ Timeout alcanzado: {e}")
    except Exception as e:
        print(f"⚠️ Ocurrió un error inesperado: {e}")
```

---

### Ejecución

```python
await scrapear_agencias_completo()   # Ejecuta todo el proceso
```

---


## 📜 Licencia

Este proyecto se publica con fines educativos y de práctica.
