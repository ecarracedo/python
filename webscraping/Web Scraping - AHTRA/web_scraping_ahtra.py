from playwright.async_api import async_playwright
import pandas as pd
from tqdm import tqdm
import asyncio
import os

# Diccionario de filiales
filiales = {
    1: "Bariloche & Villa La Angostura",
    2: "Ciudad de Buenos Aires",
    13: "Chubut",
    3: "Córdoba",
    12: "Iguazú",
    9: "Buenos Aires",
    7: "Jujuy",
    24: "Litoral",
    6: "Mar de las Pampas",
    21: "Mendoza",
    11: "Pinamar - Cariló",
    14: "Salta",
    4: "Santa Cruz",
    16: "Tierra del Fuego",
    15: "Tucumán",
    99: "Más Hoteles Asociados"
}

# Mostrar las opciones de filiales ordenadas por ID
print("Elige una filial ingresando el número correspondiente:")
for id_ in sorted(filiales.keys()):  # Ordenar las claves de menor a mayor
    print(f"{id_}: {filiales[id_]}")

# Función para solicitar al usuario la selección de la filial
def seleccionar_filial():
    while True:
        try:
            filial_id = int(input("Introduce el número de la filial que deseas seleccionar: "))
            if filial_id in filiales:
                print(f"\nFilial seleccionada: {filiales[filial_id]} (ID: {filial_id})")
                return filial_id
            else:
                print("ID de filial no válido. Intenta nuevamente.")
        except ValueError:
            print("Por favor, ingresa un número válido.")

# Función para obtener el texto opcional
async def get_optional_text(page, selector):
    try:
        locator = page.locator(selector)
        if await locator.is_visible():
            return (await locator.text_content()).strip()
        else:
            return "No disponible"
    except:
        return "No disponible"

# Función para navegar por los hoteles de una filial
async def navegar_hoteles(filial_id):
    base_url = "https://www.ahtra.com.ar/"
    listado_url = f"{base_url}hoteles_asociados.php?fil={filial_id}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Cambiá a False si querés ver el navegador
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(listado_url)

        hotel_cards = await page.query_selector_all(".row.app-brief #hoteles-foto a")
        total_hoteles = len(hotel_cards)
        print(f"\n🔗 Se encontraron {total_hoteles} hoteles en la filial {filial_id}:\n")

        hoteles_data = []
        for card in tqdm(hotel_cards, desc="Procesando hoteles", unit="hotel"):
            href = await card.get_attribute("href")
            full_link = base_url + href

            new_page = await context.new_page()
            try:
                await new_page.goto(full_link, timeout=10000)

                nombre = await get_optional_text(new_page, "#hotel-interno-nombre-hotel")
                direccion = await get_optional_text(new_page, "#hotel-interno-direccion")
                telefono = await get_optional_text(new_page, "#hotel-interno-teléfono")
                email = await get_optional_text(new_page, "#hotel-interno-mail")
                sitio_web = await get_optional_text(new_page, "#hotel-interno-web a")

                hoteles_data.append({
                    "nombre": nombre,
                    "direccion": direccion,
                    "telefono": telefono,
                    "email": email,
                    "sitio_web": sitio_web,
                    "url": full_link
                })

            except Exception as e:
                print(f"❌ Error al procesar {full_link}: {e}")
                html = await new_page.content()
                with open("error_debug.html", "w", encoding="utf-8") as f:
                    f.write(html)

            await new_page.close()

        df = pd.DataFrame(hoteles_data)
        
        # Obtener el directorio actual del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Crear carpeta resultados en el mismo directorio que el script
        resultados_dir = os.path.join(script_dir, "resultados")
        os.makedirs(resultados_dir, exist_ok=True)
        
        # Obtener el nombre de la filial y crear un nombre de archivo válido
        nombre_filial = filiales[filial_id]
        nombre_archivo = f"{nombre_filial.replace(' ', '_').replace('&', 'y')}_AHTRA_hoteles_detalle.csv"
        
        # Guardar el archivo en la carpeta resultados
        output_path = os.path.join(resultados_dir, nombre_archivo)
        df.to_csv(output_path, index=False)
        print(f"\n✅ Datos guardados en '{output_path}'.")

        await browser.close()

# Ejecutar
filial_id = seleccionar_filial()  # Pedir al usuario que seleccione una filial
asyncio.run(navegar_hoteles(filial_id))
