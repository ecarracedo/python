import asyncio  # Importa la biblioteca para programación asíncrona
import csv  # Importa la biblioteca para manejar archivos CSV
import pandas as pd  # Importa pandas para análisis de datos
import os  # Importa el módulo de sistema operativo para operaciones de archivos
import re  # Importa el módulo re para operaciones de expresiones regulares
#from google.colab import drive  # Importación de Google Drive (comentada)
from playwright.async_api import async_playwright, TimeoutError  # Importa playwright para web scraping
from email_validator import validate_email, EmailNotValidError

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

# Lista para almacenar correos inválidos
correos_invalidos = []
nombre_agencia_actual = ""

def corregir_correos_invalidos():
    global correos_invalidos

    if not correos_invalidos:
        print("\n✅ No hay correos inválidos para corregir.")
        return

    correcciones = {}

    for i, item in enumerate(correos_invalidos, 1):
        nombre_agencia = item["nombre_agencia"]
        correo_invalido = item["correo"]

        print(f"\n[{i}] Agencia: {nombre_agencia}")
        print(f"Correo inválido: {correo_invalido}")
        nuevo_correo = input("Ingrese el correo corregido (o Enter para dejarlo en blanco): ").strip()

        if nuevo_correo:
            correcciones[nombre_agencia] = nuevo_correo

    # Actualizar el archivo CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "resultados")
    csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv')]

    if not csv_files:
        print("❌ No se encontró archivo CSV para actualizar.")
        return

    csv_file = os.path.join(results_dir, csv_files[-1])
    df = pd.read_csv(csv_file)

    cambios = 0
    for i, row in df.iterrows():
        nombre = row["nombre"]
        if nombre in correcciones:
            df.at[i, "correo"] = correcciones[nombre]
            cambios += 1

    if cambios:
        df.to_csv(csv_file, index=False)
        print(f"\n✅ Se corrigieron {cambios} correos en: {csv_file}")
    else:
        print("\n⚠️ No se realizaron cambios en el archivo.")

    # Limpiar correos corregidos
    correos_invalidos = [c for c in correos_invalidos if c["nombre_agencia"] not in correcciones]

def mostrar_correos_invalidos():
    global correos_invalidos
    if correos_invalidos:
        print("\n⚠️ Correos electrónicos inválidos encontrados:\n")
        for i, item in enumerate(correos_invalidos, 1):
            nombre = item.get("nombre_agencia", "(Sin nombre)")
            correo = item.get("correo", "")
            print(f"{i}. 🏢 Agencia: {nombre}\n   📧 Correo: {correo}\n")
    else:
        print("\n✅ No se encontraron correos electrónicos inválidos en esta búsqueda.")

        
def mostrar_menu():
    print("\n=== MENÚ DE PROVINCIAS ===")
    for i, provincia in enumerate(PROVINCIAS, 1):
        print(f"{i}. {provincia}")
    print("0. Salir")
    return input("\nSeleccione una provincia (número): ")


def normalizar_correo(correo):
    global correos_invalidos
    """Normaliza y valida un correo electrónico."""
    if not correo:
        return ""
    
    correo_original = correo  # Guardamos el correo original para el registro
    
    # Elimina espacios en blanco
    correo = correo.strip()
    
    # Reemplaza símbolos comunes que se usan en lugar de @
    correo = correo.replace('(at)', '@')
    correo = correo.replace('[at]', '@')
    correo = correo.replace('(arroba)', '@')
    correo = correo.replace('[arroba]', '@')
    
    # Verifica si falta el @ y lo agrega en casos comunes
    if 'gmail.com' in correo and '@' not in correo:
        correo = correo.replace('gmail.com', '@gmail.com')
    elif 'hotmail.com' in correo and '@' not in correo:
        correo = correo.replace('hotmail.com', '@hotmail.com')
    elif 'yahoo.com' in correo and '@' not in correo:
        correo = correo.replace('yahoo.com', '@yahoo.com')
    
    # Verifica si falta el .com en dominios comunes
    if '@gmail' in correo and not correo.endswith('.com'):
        correo += '.com'
    elif '@hotmail' in correo and not correo.endswith('.com'):
        correo += '.com'
    elif '@yahoo' in correo and not correo.endswith('.com'):
        correo += '.com'
    
    # Elimina caracteres especiales excepto @ y .
    correo = re.sub(r'[^a-zA-Z0-9@.]', '', correo)
    
    # Convierte a minúsculas
    correo = correo.lower()
    
    # Validación final con email-validator
    try:
        # Validar el correo
        emailinfo = validate_email(correo, check_deliverability=False)
        # Normalizar el correo (por ejemplo, convierte 'Gmail.com' a 'gmail.com')
        correo = emailinfo.normalized
    except EmailNotValidError:
        # Si el correo no es válido, lo agregamos a la lista de inválidos
        if correo_original:
            correos_invalidos.append({"nombre_agencia": nombre_agencia_actual, "correo": correo_original})
            
        return ""
    
    return correo

async def scrapear_agencias_completo(provincia):
    global correos_invalidos
    global nombre_agencia_actual
    correos_invalidos = []  # Reiniciamos la lista para cada provincia
    
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
                                nombre_agencia_actual = nombre  # Seteamos esta variable global temporal
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
            
            # Después de guardar los archivos, mostramos los correos inválidos
            
            mostrar_correos_invalidos()

            if correos_invalidos:
                intentar_corregir = input("\n¿Desea intentar corregir los correos inválidos encontrados antes de guardar? (s/n): ").lower()
                if intentar_corregir == 's':
                    corregir_correos_invalidos()

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
