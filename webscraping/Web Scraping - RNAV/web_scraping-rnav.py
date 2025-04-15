import asyncio  # Importa la biblioteca para programación asíncrona
import csv  # Importa la biblioteca para manejar archivos CSV
import pandas as pd  # Importa pandas para análisis de datos
import os  # Importa el módulo de sistema operativo para operaciones de archivos
import re  # Importa el módulo re para operaciones de expresiones regulares
#from google.colab import drive  # Importación de Google Drive (comentada)
from playwright.async_api import async_playwright, TimeoutError  # Importa playwright para web scraping

# Montar Google Drive
#drive.mount('/content/drive')  # Monta Google Drive en el entorno (comentado)

# Lista de provincias de Argentina
PROVINCIAS = [
    "Buenos Aires",
    "Catamarca",
    "Chaco",
    "Chubut",
    "Córdoba",
    "Corrientes",
    "Entre Ríos",
    "Formosa",
    "Jujuy",
    "La Pampa",
    "La Rioja",
    "Mendoza",
    "Misiones",
    "Neuquén",
    "Río Negro",
    "Salta",
    "San Juan",
    "San Luis",
    "Santa Cruz",
    "Santa Fe",
    "Santiago del Estero",
    "Tierra del Fuego",
    "Tucumán"
]

def mostrar_menu():
    print("\n=== MENÚ DE PROVINCIAS ===")
    for i, provincia in enumerate(PROVINCIAS, 1):
        print(f"{i}. {provincia}")
    print("0. Salir")
    return input("\nSeleccione una provincia (número): ")

def normalizar_correo(correo):
    """Normaliza un correo electrónico eliminando caracteres especiales."""
    if not correo:
        return ""
    # Elimina espacios en blanco
    correo = correo.strip()
    # Elimina caracteres especiales excepto @ y .
    correo = re.sub(r'[^a-zA-Z0-9@.]', '', correo)
    return correo.lower()

async def scrapear_agencias_completo(provincia):
    async with async_playwright() as p:  # Inicializa playwright
        browser = await p.chromium.launch(headless=True)  # Inicia el navegador en modo headless (sin interfaz gráfica)
        context = await browser.new_context()  # Crea un nuevo contexto de navegación
        page = await context.new_page()  # Crea una nueva página

        try:
            print("🌐 Cargando página...")
            await page.goto("https://www.agenciasdeviajes.ar/#buscador", timeout=30000)  # Navega a la página de agencias de viaje

            print(f"⌨️ Buscando '{provincia}'...")
            await page.wait_for_selector("input[placeholder*='Ciudad o Provincia']", timeout=20000)  # Espera a que aparezca el campo de búsqueda
            await page.fill("input[placeholder*='Ciudad o Provincia']", provincia)  # Completa el campo de búsqueda con la provincia
            await page.wait_for_timeout(2000)  # Espera 2 segundos

            print("⌛ Esperando resultados...")
            await page.wait_for_selector("h3.text-lg", timeout=20000)  # Espera a que aparezcan los resultados

            agencias = []  # Lista para almacenar los datos de las agencias
            pagina = 1  # Contador de páginas

            while True:  # Bucle para recorrer todas las páginas de resultados
                print(f"📃 Página {pagina}: extrayendo agencias...")

                h3_agencias = await page.query_selector_all("h3.text-lg")  # Obtiene todos los nombres de agencias
                for h3 in h3_agencias:  # Recorre cada agencia encontrada
                    nombre = await h3.inner_text()  # Obtiene el nombre de la agencia
                    telefono = ""
                    correo = ""
                    localidad = ""

                    contenedor = await h3.evaluate_handle("node => node.parentElement.parentElement")  # Obtiene el contenedor padre que tiene toda la info
                    contenedor_element = contenedor.as_element()  # Convierte a elemento para poder interactuar

                    if contenedor_element:  # Si se encontró el contenedor
                        parrafos = await contenedor_element.query_selector_all("p.leading-relaxed.text-sm")  # Obtiene todos los párrafos con información
                        for p in parrafos:  # Recorre cada párrafo
                            texto = await p.inner_text()  # Obtiene el texto del párrafo
                            if "Teléfono:" in texto:  # Si contiene información de teléfono
                                telefono = texto.replace("Teléfono:", "").strip()  # Extrae el número de teléfono
                            if "Correo electrónico:" in texto:  # Si contiene información de correo
                                correo = texto.replace("Correo electrónico:", "").strip()
                                correo = normalizar_correo(correo)  # Normaliza el correo
                            if "Localidad:" in texto:  # Si contiene información de localidad
                                localidad = texto.replace("Localidad:", "").strip()  # Extrae la localidad

                    # Agrega la información de la agencia a la lista
                    agencias.append({
                        "nombre": nombre,
                        "telefono": telefono,
                        "correo": correo,
                        "localidad": localidad,
                        "provincia": provincia
                    })

                # Cerrar modal si está abierto
                print("🧹 Cerrando modal si está abierto...")
                await page.evaluate("""
                    () => {
                        const modal = document.querySelector('[role=dialog]');
                        if (modal) {
                            window.dispatchEvent(new CustomEvent('close-modal', { detail: { id: 'video1year' }}));
                        }
                    }
                """)  # Ejecuta JavaScript para cerrar cualquier modal que pueda aparecer
                await page.wait_for_timeout(1000)  # Espera 1 segundo

                # Verificar si hay botón de siguiente
                siguiente = page.locator("button[dusk='nextPage.after']")  # Localiza el botón "Siguiente"
                if await siguiente.count() == 0 or not await siguiente.is_enabled():  # Si no existe o está deshabilitado
                    print("⛔ No hay más páginas.")
                    break  # Sale del bucle

                try:
                    print("➡️ Haciendo clic en 'Siguiente'...")
                    await siguiente.scroll_into_view_if_needed()  # Desplaza hasta el botón si es necesario
                    await siguiente.click()  # Hace clic en el botón "Siguiente"
                    await page.wait_for_timeout(2500)  # Espera 2.5 segundos para que cargue la siguiente página
                    pagina += 1  # Incrementa el contador de páginas
                except Exception as e:
                    print(f"⚠️ Error al hacer clic en 'Siguiente': {e}")
                    break  # Sale del bucle si hay un error

            await browser.close()  # Cierra el navegador

            # Guardar CSV local
            script_dir = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ruta absoluta del directorio donde está el script
            results_dir = os.path.join(script_dir, "resultados")  # Crea la ruta a la carpeta "resultados" dentro del directorio del script
            # Crear la carpeta resultados si no existe
            if not os.path.exists(results_dir):  # Verifica si la carpeta "resultados" no existe
                os.makedirs(results_dir)  # Crea la carpeta "resultados" si no existe
            csv_filename = os.path.join(results_dir, f"{provincia.lower().replace(' ', '_')}_agencias_viaje.csv")  # Construye la ruta completa del archivo CSV
            print(f"💾 Guardando en CSV: {csv_filename}")
            with open(csv_filename, "w", newline="", encoding="utf-8") as f:  # Abre el archivo CSV en modo escritura con codificación UTF-8
                writer = csv.DictWriter(f, fieldnames=["nombre", "telefono", "correo", "localidad", "provincia"])  # Crea un escritor CSV con las columnas especificadas
                writer.writeheader()  # Escribe la fila de encabezados
                writer.writerows(agencias)  # Escribe todas las filas de datos de las agencias

            # Guardar Excel en Drive
            #df = pd.DataFrame(agencias)  # Crea un DataFrame de pandas con los datos de las agencias (comentado)
            #xlsx_path = f"/content/drive/MyDrive/{provincia.lower().replace(' ', '_')}_agencias_viaje.xlsx"  # Ruta del archivo Excel en Google Drive (comentado)
            #df.to_excel(xlsx_path, index=False)  # Guarda el DataFrame como Excel en Google Drive (comentado)
            #print(f"✅ Archivo Excel guardado en Google Drive: {xlsx_path}")  # Muestra mensaje de confirmación (comentado)
            
            print(f"📁 Total agencias: {len(agencias)}")  # Muestra el total de agencias encontradas

        except KeyboardInterrupt:
            print("❌ Ejecución interrumpida por el usuario.")  # Maneja la interrupción por teclado
        except TimeoutError as e:
            print(f"❌ Timeout alcanzado: {e}")  # Maneja errores de tiempo de espera
        except Exception as e:
            print(f"⚠️ Ocurrió un error inesperado: {e}")  # Maneja cualquier otro error

async def main():
    while True:
        opcion = mostrar_menu()
        
        if opcion == "0":
            print("¡Hasta luego!")
            break
            
        try:
            opcion = int(opcion)
            if 1 <= opcion <= len(PROVINCIAS):
                provincia = PROVINCIAS[opcion - 1]
                await scrapear_agencias_completo(provincia)
                
                continuar = input("\n¿Desea buscar otra provincia? (s/n): ").lower()
                if continuar != 's':
                    print("¡Hasta luego!")
                    break
            else:
                print("Opción inválida. Por favor, seleccione un número válido.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

if __name__ == "__main__":
    asyncio.run(main())  # Ejecuta la función main si el script se ejecuta directamente
