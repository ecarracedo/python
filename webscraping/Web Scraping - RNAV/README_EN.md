🌐 Este README también está disponible en [Español](README.md)

# Travel Agency Scraper in Argentina 🇦🇷

This project allows extracting information from travel agencies registered on [https://www.agenciasdeviajes.ar/](https://www.agenciasdeviajes.ar/) using `Playwright` in an environment like Google Colab.

## 📌 Description

The script automates navigation through the official travel agency website, searching by province and extracting useful information such as:

- Agency name
- Phone number
- Email
- Location
- Province

Data is automatically saved to:

- A local `.CSV` file
- An `.XLSX` file in Google Drive

There are two versions of Python files:

- `web_scraping-rnav.py`: A version to run on your PC, without Google Drive connection
- `web_scraping-rnav_colab-jupiter.py`: A version to run on Google Colab or Jupyter

## 🧰 Technologies Used

- `Playwright` → For web automation
- `asyncio` → For managing asynchronous tasks
- `pandas` → For exporting data to Excel
- `google.colab` → For mounting Google Drive
- `nest_asyncio` → Allows running async loops inside Colab notebooks

## ⚙️ Prerequisites

Before running the script, make sure to install and configure:

```bash
pip install playwright nest_asyncio pandas
playwright install
```

Additionally, mount Google Drive in Colab with:

```python
from google.colab import drive
drive.mount('/content/drive')
```

## 🧠 How it Works

1. The user enters the **province** to search for.
2. The browser opens in the background and navigates to the site.
3. The province is entered in the search box.
4. All result pages are traversed.
5. For each agency, data is extracted from its HTML block.
6. If a **pop-up modal** appears, it is automatically closed to prevent navigation interruption.
7. Finally, results are saved in CSV and XLSX formats.

## ⚙️ Modal Handling in Scraping

During the scraping process, the webpage might display a modal (pop-up window) that blocks access to content or interrupts navigation. Modals are commonly used to show welcome messages, advertisements, or notifications. To ensure the scraper can continue running without issues, special handling was implemented to detect and close these modals if present.

---

### **What does the code do regarding modals?**

In the code, the `evaluate` function is used to check if a modal is open and close it. This process is done as follows:

```python
# Close the modal (if open) to continue navigation
await page.evaluate("""
    () => {
        const modal = document.querySelector('[role=dialog]');  // Look for modal in DOM
        if (modal) {  // If modal exists
            window.dispatchEvent(new CustomEvent('close-modal', { detail: { id: 'video1year' }}));  // Close modal
        }
    }
""")
```

---

#### **Code Explanation**:

1. **`document.querySelector('[role=dialog]')`**  
   This selector is used to find a modal in the webpage's DOM. The `[role=dialog]` attribute is commonly used to represent modals, as its semantic function is to show a dialog box.

2. **`window.dispatchEvent(new CustomEvent('close-modal'))`**  
   If the modal is found, a close event is sent using `dispatchEvent` to simulate closing the modal. This allows the scraper to continue working without being blocked by the modal.

3. **Why is this important?**  
   Without this modal handling, if the page displays a modal, it could block data extraction or interrupt navigation to the next page. This is prevented by automatically closing the modal if present.

## 📦 Script Execution

```python
await scrape_agencies_complete()
```

# 🧠 Line by Line Code Explanation

This script automates the scraping of travel agencies from [https://www.agenciasdeviajes.ar](https://www.agenciasdeviajes.ar) using `Playwright` and runs perfectly on Google Colab.

---

```python
import asyncio                              # For handling asynchronous tasks
import csv                                  # For saving data as CSV file
import pandas as pd                         # For data manipulation and Excel export
from google.colab import drive              # For mounting Google Drive in Colab
from playwright.async_api import async_playwright, TimeoutError  # Main web automation library
```

```python
drive.mount('/content/drive')              # Mounts Google Drive to save files directly there
```

---

### Main Function

```python
async def scrape_agencies_complete():
    province = input("📍 Enter the province you want to search: ").strip()  # Asks user for province to search
```

```python
    async with async_playwright() as p:                      # Initializes Playwright
        browser = await p.chromium.launch(headless=True)     # Launches Chromium browser in headless mode
        context = await browser.new_context()                # Creates new context (like an isolated tab)
        page = await context.new_page()                      # Opens new page
```

---

### Go to Web and Search

```python
        await page.goto("https://www.agenciasdeviajes.ar/#buscador", timeout=30000)  # Loads the page
        await page.wait_for_selector("input[placeholder*='Ciudad o Provincia']", timeout=20000)
        await page.fill("input[placeholder*='Ciudad o Provincia']", province)        # Writes the province
        await page.wait_for_timeout(2000)                                             # Waits for loading
        await page.wait_for_selector("h3.text-lg", timeout=20000)                    # Waits for results to appear
```

---

### Extract Results

```python
        agencies = []             # List where data will be stored
        page_num = 1              # Page counter

        while True:
            h3_agencies = await page.query_selector_all("h3.text-lg")  # Finds titles (agency names)
```

```python
            for h3 in h3_agencies:
                name = await h3.inner_text()      # Extracts agency name
                phone = ""
                email = ""
                location = ""

                container = await h3.evaluate_handle("node => node.parentElement.parentElement")  # Goes to info container
                container_element = container.as_element()

                if container_element:
                    paragraphs = await container_element.query_selector_all("p.leading-relaxed.text-sm")  # Finds data paragraphs

                    for p in paragraphs:
                        text = await p.inner_text()
                        if "Teléfono:" in text:
                            phone = text.replace("Teléfono:", "").strip()
                        if "Correo electrónico:" in text:
                            email = text.replace("Correo electrónico:", "").strip()
                        if "Localidad:" in text:
                            location = text.replace("Localidad:", "").strip()
```

```python
                agencies.append({                               # Adds data to the list
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "location": location,
                    "province": province
                })
```

---

### Modal Closing (if appears)

```python
            await page.evaluate("""                            # Executes JavaScript code to close pop-up modal
                () => {
                    const modal = document.querySelector('[role=dialog]');
                    if (modal) {
                        window.dispatchEvent(new CustomEvent('close-modal', { detail: { id: 'video1year' }}));
                    }
                }
            """)
```

---

### Page Navigation

```python
            next_button = page.locator("button[dusk='nextPage.after']")    # Finds "Next" button
            if await next_button.count() == 0 or not await next_button.is_enabled():  # If no more pages
                break

            await next_button.scroll_into_view_if_needed()    # Ensures button is visible
            await next_button.click()                         # Clicks "Next"
            await page.wait_for_timeout(2500)               # Waits for loading
            page_num += 1
```

---

### Data Saving

```python
        await browser.close()   # Closes browser
```

```python
        # Save local CSV
        csv_filename = f"{province.lower().replace(' ', '_')}_travel_agencies.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "phone", "email", "location", "province"])
            writer.writeheader()
            writer.writerows(agencies)
```

```python
        # Save Excel to Drive
        df = pd.DataFrame(agencies)
        xlsx_path = f"/content/drive/MyDrive/EC/WebScraping/RNAV/{province.lower().replace(' ', '_')}_travel_agencies.xlsx"
        df.to_excel(xlsx_path, index=False)
```

---

### Error Handling

```python
    except KeyboardInterrupt:
        print("❌ Execution interrupted by user.")
    except TimeoutError as e:
        print(f"❌ Timeout reached: {e}")
    except Exception as e:
        print(f"⚠️ An unexpected error occurred: {e}")
```
## ✉️ Normalización y corrección de correos electrónicos

Durante el proceso de scraping, los correos electrónicos extraídos son normalizados automáticamente para corregir errores comunes como:

- Faltante del símbolo `@`
- Dominios incompletos como `gmail` en lugar de `@gmail.com`
- Sustituciones como `(at)`, `[arroba]`, etc.
- Caracteres especiales no válidos

Esta normalización se realiza con la función:

```python
normalizar_correo(correo: str) -> str
---

### Execution

```python
await scrape_agencies_complete()   # Executes the entire process
```

---

## 📜 License

This project is published for educational and practice purposes. 

## 📌 Contact

ecarracedo@gmail.com

## 📋 Changelog

### [1.4.0] - 2025-04-16  
#### Added  
- Association of invalid email addresses with the corresponding agency name during scraping  
- Option to manually correct invalid emails, clearly identifying which agency each one belongs to  
- Improved validation of manually entered email addresses  
- Automatic update of the CSV file with corrections  
- Enhanced display format for invalid emails (more readable and professional)

#### Fixed  
- Issue where the agency name was not correctly stored when an invalid email was detected

### [1.3.0] - 2024-03-21
#### Added
- Email normalization improvements:
  - Detection and correction of missing @ in common domains
  - Detection and correction of missing .com in common domains
  - Replacement of common symbols used instead of @
  - Better handling of special characters

### [1.2.0] - 2024-03-21
#### Added
- Email normalization (removal of special characters and accents)

### [1.1.0] - 2024-03-21
#### Added
- Interactive menu with all Argentine provinces
- Option to run the script again with another province
- Improved error handling in province selection

### [1.0.0] - 2024-03-20
#### Added
- Initial scraper version
- Travel agency data extraction
- CSV and Excel file saving
- Automatic handling of pop-up modals