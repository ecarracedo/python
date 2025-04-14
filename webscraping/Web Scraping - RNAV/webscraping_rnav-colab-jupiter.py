# -*- coding: utf-8 -*-
"""WebScraping_RNAV.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/github/ecarracedo/form-contact/blob/master/WebScraping_RNAV.ipynb
"""

!pip install playwright
!pip install playwright nest_asyncio
!playwright install
!apt install -y libnss3

import asyncio  # Para ejecutar funciones asíncronas
import csv  # Para guardar los datos como archivo CSV
import pandas as pd  # Para trabajar con DataFrames y exportar a Excel
import os  # Para manejar rutas de carpetas
from google.colab import drive  # Para montar Google Drive en Colab
from playwright.async_api import async_playwright, TimeoutError  # Playwright para scraping web

# Montar Google Drive en Colab
drive.mount('/content/drive')

async def scrapear_agencias_completo():
    provincia = input("📍 Ingresá la provincia que querés buscar: ").strip()  # Solicita la provincia al usuario

    async with async_playwright() as p:  # Inicia Playwright en contexto asíncrono
        browser = await p.chromium.launch(headless=True)  # Lanza navegador Chromium sin interfaz gráfica
        context = await browser.new_context()  # Crea un contexto nuevo (como una pestaña)
        page = await context.new_page()  # Abre una página nueva

        try:
            print("🌐 Cargando página...")
            await page.goto("https://www.agenciasdeviajes.ar/#buscador", timeout=30000)  # Abre la web con timeout de 30s

            print(f"⌨️ Buscando '{provincia}'...")
            await page.wait_for_selector("input[placeholder*='Ciudad o Provincia']", timeout=20000)  # Espera el input
            await page.fill("input[placeholder*='Ciudad o Provincia']", provincia)  # Escribe la provincia
            await page.wait_for_timeout(2000)  # Espera 2 segundos por los resultados

            print("⌛ Esperando resultados...")
            await page.wait_for_selector("h3.text-lg", timeout=20000)  # Espera a que aparezcan las agencias

            agencias = []  # Lista para guardar los datos
            pagina = 1  # Contador de páginas

            while True:  # Loop para recorrer todas las páginas
                print(f"📃 Página {pagina}: extrayendo agencias...")

                h3_agencias = await page.query_selector_all("h3.text-lg")  # Encuentra los títulos de agencias
                for h3 in h3_agencias:
                    nombre = await h3.inner_text()  # Obtiene el nombre de la agencia
                    telefono = ""
                    correo = ""
                    localidad = ""

                    # Encuentra el contenedor padre con los detalles de contacto
                    contenedor = await h3.evaluate_handle("node => node.parentElement.parentElement")
                    contenedor_element = contenedor.as_element()

                    if contenedor_element:
                        # Busca los párrafos donde están teléfono, correo, localidad
                        parrafos = await contenedor_element.query_selector_all("p.leading-relaxed.text-sm")
                        for p in parrafos:
                            texto = await p.inner_text()
                            if "Teléfono:" in texto:
                                telefono = texto.replace("Teléfono:", "").strip()
                            if "Correo electrónico:" in texto:
                                correo = texto.replace("Correo electrónico:", "").strip()
                            if "Localidad:" in texto:
                                localidad = texto.replace("Localidad:", "").strip()

                    # Guarda los datos de la agencia
                    agencias.append({
                        "nombre": nombre,
                        "telefono": telefono,
                        "correo": correo,
                        "localidad": localidad,
                        "provincia": provincia
                    })

                # Cierra un modal si está abierto (como el de suscripción de video)
                print("🧹 Cerrando modal si está abierto...")
                await page.evaluate("""
                    () => {
                        const modal = document.querySelector('[role=dialog]');
                        if (modal) {
                            window.dispatchEvent(new CustomEvent('close-modal', { detail: { id: 'video1year' }}));
                        }
                    }
                """)
                await page.wait_for_timeout(1000)  # Espera un segundo luego de cerrar modal

                # Verifica si existe el botón de "Siguiente página"
                siguiente = page.locator("button[dusk='nextPage.after']")
                if await siguiente.count() == 0 or not await siguiente.is_enabled():
                    print("⛔ No hay más páginas.")
                    break  # Sale del loop si no hay más páginas

                try:
                    print("➡️ Haciendo clic en 'Siguiente'...")
                    await siguiente.scroll_into_view_if_needed()  # Asegura que el botón sea visible
                    await siguiente.click()  # Clic en botón de siguiente
                    await page.wait_for_timeout(2500)  # Espera a que cargue la nueva página
                    pagina += 1  # Incrementa el contador de página
                except Exception as e:
                    print(f"⚠️ Error al hacer clic en 'Siguiente': {e}")
                    break  # Sale del loop si ocurre un error

            await browser.close()  # Cierra el navegador

            # Crea carpeta destino en Drive si no existe
            drive_folder = "/content/drive/MyDrive/EC/WebScraping/RNAV/"
            os.makedirs(drive_folder, exist_ok=True)

            # Guarda los datos como CSV localmente en Colab
            csv_filename = f"{provincia.lower().replace(' ', '_')}_agencias_viaje.csv"
            print(f"💾 Guardando en CSV: {csv_filename}")
            with open(csv_filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["nombre", "telefono", "correo", "localidad", "provincia"])
                writer.writeheader()
                writer.writerows(agencias)

            # Exporta los datos a Excel y los guarda en Google Drive
            df = pd.DataFrame(agencias)
            xlsx_path = os.path.join(drive_folder, f"{provincia.lower().replace(' ', '_')}_agencias_viaje.xlsx")
            df.to_excel(xlsx_path, index=False)
            print(f"✅ Archivo Excel guardado en Google Drive: {xlsx_path}")
            print(f"📁 Total agencias: {len(agencias)}")

        # Manejo de errores
        except KeyboardInterrupt:
            print("❌ Ejecución interrumpida por el usuario.")
        except TimeoutError as e:
            print(f"❌ Timeout alcanzado: {e}")
        except Exception as e:
            print(f"⚠️ Ocurrió un error inesperado: {e}")

# Ejecutar la función
await scrapear_agencias_completo()