🌐 Este README esta disponible en [Español](README.md)

# Travel Agency Scraper in Argentina 🇦🇷

This project allows you to extract information from registered travel agencies in [https://www.agenciasdeviajes.ar/](https://www.agenciasdeviajes.ar/) using `Playwright` in an environment like Google Colab.

## 📌 Description

The script automates navigation through the official travel agency page, searching by province and extracting useful information such as:

- Agency name
- Phone number
- Email
- Location
- Province

The data is automatically saved in:

- A `.CSV` file (local)
- An `.XLSX` file in Google Drive

There are two versions of files with the `.py` extension:

- `web_scraping-rnav.py`: A version to run on your PC, without a connection to Google Drive
- `web_scraping-rnav_colab-jupiter.py`: A version to run on Google Colab or Jupyter

## 🧰 Technologies Used

- `Playwright` → To automate web navigation
- `asyncio` → To manage asynchronous tasks
- `pandas` → To export data to Excel
- `google.colab` → To mount Google Drive
- `nest_asyncio` → Allows asynchronous loops to run within Colab notebooks

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

## 🧠 How It Works

1. The user enters the **province** to query.
2. The browser opens in the background and navigates to the site.
3. The province is typed into the search bar.
4. All result pages are traversed.
5. For each agency, data is extracted from its HTML block.
6. If a **pop-up modal** appears, it is automatically closed to avoid interrupting navigation.
7. Before saving the results, an email normalization process is performed.
8. Finally, the results are saved in CSV and XLSX.

## ⚙️ Handling Modals in Scraping

During the scraping process, sometimes the website may display a modal (a pop-up window) that blocks access to content or interrupts navigation. Modals are commonly used to show welcome messages, advertisements, or notifications. To ensure that the scraper can continue execution smoothly, special handling was implemented to detect and close these modals if present.

---

### **What does the code do regarding modals?**

In the code, the `evaluate` function is used to check if an open modal exists and close it. This process is done as follows:

```python
# Close the modal (if open) to continue navigating
await page.evaluate("""
    () => {
        const modal = document.querySelector('[role=dialog]');  // Search for the modal in the DOM
        if (modal) {  // If the modal exists
            window.dispatchEvent(new CustomEvent('close-modal', { detail: { id: 'video1year' }}));  // Close the modal
        }
    }
""")
```

---

#### **Code Explanation**:

1. **`document.querySelector('[role=dialog]')`**  
   This selector is used to search for a modal in the page's DOM. The attribute `[role=dialog]` is commonly used to represent modals since its semantic function is to display a dialog box.

2. **`window.dispatchEvent(new CustomEvent('close-modal'))`**  
   If the modal is found, a close event is sent using `dispatchEvent` to simulate the action of closing the modal. This allows the scraper to continue working without being blocked by the modal.

3. **Why is this important?**  
   Without this modal handling, if the page presents a modal, it could block data extraction or interrupt navigation to the next page. This is avoided by automatically closing the modal if it is present.

## 📦 Running the Script

```python
await scrapear_agencias_completo()
```

# 🧠 Line-by-Line Explanation of the Code

This script automates the scraping of travel agencies from [https://www.agenciasdeviajes.ar](https://www.agenciasdeviajes.ar) using `Playwright` and runs perfectly in Google Colab.

---

```python
import asyncio                              # To handle asynchronous tasks
import csv                                  # To save data as a CSV file
import pandas as pd                         # For data manipulation and exporting to Excel
from google.colab import drive              # To mount Google Drive in Colab
from playwright.async_api import async_playwright, TimeoutError  # Main web automation library
```

```python
drive.mount('/content/drive')              # Mount Google Drive to save files directly there
```

---

### Main Function

```python
async def scrapear_agencias_completo():
    province = input("📍 Enter the province you want to search: ").strip()  # Ask the user for the province to search
```

```python
    async with async_playwright() as p:                      # Initialize Playwright
        browser = await p.chromium.launch(headless=True)     # Launch the Chromium browser in headless mode
        context = await browser.new_context()                # Create a new context (like an isolated tab)
        page = await context.new_page()                      # Open a new page
```

---

### Go to the Web and Search

```python
        await page.goto("https://www.agenciasdeviajes.ar/#buscador", timeout=30000)  # Load the page
        await page.wait_for_selector("input[placeholder*='City or Province']", timeout=20000)
        await page.fill("input[placeholder*='City or Province']", province)        # Type the province
        await page.wait_for_timeout(2000)                                             # Wait for it to load
        await page.wait_for_selector("h3.text-lg", timeout=20000)                    # Wait for results to appear
```

---

### Extract Results

```python
        agencies = []             # List to store the data
        page_number = 1           # Page counter

        while True:
            h3_agencies = await page.query_selector_all("h3.text-lg")  # Find the titles (agency names)
```

```python
            for h3 in h3_agencies:
                name = await h3.inner_text()      # Extract the agency name
                phone = ""
                email = ""
                location = ""

                container = await h3.evaluate_handle("node => node.parentElement.parentElement")  # Go to the info container
                container_element = container.as_element()

                if container_element:
                    paragraphs = await container_element.query_selector_all("p.leading-relaxed.text-sm")  # Look for data paragraphs

                    for p in paragraphs:
                        text = await p.inner_text()
                        if "Phone:" in text:
                            phone = text.replace("Phone:", "").strip()
                        if "Email:" in text:
                            email = text.replace("Email:", "").strip()
                        if "Location:" in text:
                            location = text.replace("Location:", "").strip()
```

```python
                agencies.append({                               # Add the data to the list
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "location": location,
                    "province": province
                })
```

---

### Close Modal (if it appears)

```python
            await page.evaluate("""                            # Execute JavaScript to close a pop-up modal
                () => {
                    const modal = document.querySelector('[role=dialog]');
                    if (modal) {
                        window.dispatchEvent(new CustomEvent('close-modal', { detail: { id: 'video1year' }}));
                    }
                }
            """)
```

---

### Navigation Between Pages

```python
            next_button = page.locator("button[dusk='nextPage.after']")    # Look for the "Next" button
            if await next_button.count() == 0 or not await next_button.is_enabled():  # If there are no more pages
                break

            await next_button.scroll_into_view_if_needed()    # Ensure the button is visible
            await next_button.click()                         # Click on "Next"
            await page.wait_for_timeout(2500)               # Wait for it to load
            page_number += 1
```

---

### Saving Data

```python
        await browser.close()   # Close the browser
```

```python
        # Save CSV locally
        csv_filename = f"{province.lower().replace(' ', '_')}_travel_agencies.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "phone", "email", "location", "province"])
            writer.writeheader()
            writer.writerows(agencies)
```

```python
        # Save Excel in Drive
        df = pd.DataFrame(agencies)
        xlsx_path = f"/content/drive/MyDrive/EC/WebScraping/RNAV/{province.lower().replace(' ', '_')}_travel_agencies.xlsx"
        df.to_excel(xlsx_path, index=False)
```

---

### Error Handler

```python
    except KeyboardInterrupt:
        print("❌ Execution interrupted by the user.")
    except TimeoutError as e:
        print(f"❌ Timeout reached: {e}")
    except Exception as e:
        print(f"⚠️ An unexpected error occurred: {e}")
```

---

## ✉️ Normalization and Correction of Emails

During the scraping process, extracted emails are automatically normalized to correct common errors such as:

- Missing the `@` symbol
- Incomplete domains like `gmail` instead of `@gmail.com`
- Substitutions like `(at)`, `[at]`, etc.
- Invalid special characters

This normalization is done with the function:

```python
normalizar_correo(correo: str) -> str
```

If an email cannot be validated automatically, it is stored along with the agency name for later review.

---

### 🛠 Manual Correction of Emails

At the end of scraping, if there are invalid emails, they are listed and the option to correct them manually is offered with:

```python
corregir_correos_invalidos()
```

This process allows:

- Viewing the name of the agency associated with the invalid email
- Entering a valid correction
- Automatically validating the new email
- Updating the CSV file with the corresponding correction

---

### ⚠️ User Notice Before Saving

If **one or more emails cannot be automatically normalized**, the system will inform the user.  
Before saving the final file, the option to **modify them manually** will be offered, thus ensuring that the information is as complete and accurate as possible.

---

## 📜 License

This project is published for educational and practice purposes.

## 📌 Contact

ecarracedo@gmail.com

## 📋 Changelog

### [1.4.0] - 2025-04-16
#### Added
- Association of invalid emails with the agency name during scraping
- Option to manually correct invalid emails, clearly identifying which agency they belong to
- Improved validation of manually entered emails
- Automatic update of the CSV file with corrections
- Improved output format for displaying invalid emails (more readable and professional)

#### Fixed
- Issue where the agency name was not correctly saved when an invalid email was detected

### [1.3.0] - 2024-03-21
#### Added
- Improvements in email normalization:
  - Detection and correction of missing @ in common domains
  - Detection and correction of missing .com in common domains
  - Replacement of common symbols used instead of @
  - Better handling of special characters

### [1.2.0] - 2024-03-21
#### Added
- Email normalization (removal of special characters and accents)

### [1.1.0] - 2024-03-21
#### Added
- Interactive menu with all provinces of Argentina
- Option to rerun the script with another province
- Better error handling when selecting provinces

### [1.0.0] - 2024-03-20
#### Added
- Initial version of the scraper
- Data extraction from travel agencies
- Saving in CSV and Excel format
- Automatic handling of pop-up modals
