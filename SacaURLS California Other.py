import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Configuración de Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Opcional: ejecutar sin abrir ventana del navegador
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

CATEGORY_URLS = [
    "https://www.archdaily.com/search/projects/country/united-states/categories/apartments?ad_medium=filters",
    "https://www.archdaily.com/search/projects/country/united-states/categories/loft?ad_medium=filters",
    "https://www.archdaily.com/search/projects/country/united-states/categories/penthouse?ad_medium=filters"
]

# Función para hacer scroll hasta el final de la página
def scroll_to_load_all_content():
    print("Haciendo scroll para cargar todo el contenido...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Hacer scroll hacia abajo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Esperar a que se cargue nuevo contenido
        
        # Verificar si se cargó más contenido
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # Si la altura no cambia, hemos llegado al final
            break
        last_height = new_height
    print("Scroll completo.")

# Función para cargar la página y extraer el HTML renderizado
def get_rendered_html(search_url):
    driver.get(search_url)
    scroll_to_load_all_content()  # Llamar a la función de scroll
    return driver.page_source

# Nueva función para extraer enlaces de proyectos usando Selenium directamente
def get_project_links_from_dom():
    print("Extrayendo enlaces de proyectos con Selenium...")
    elements = driver.find_elements(By.CSS_SELECTOR, "a.gridview__content")
    project_links = [e.get_attribute("href") for e in elements if e.get_attribute("href")]

    with open("project_links.txt", "w") as f:
        for link in project_links:
            f.write(link + "\n")

    print(f"✅ Se encontraron {len(project_links)} enlaces de proyectos.")
    return project_links

# Función para extraer información de un proyecto
def scrape_project(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, 'html.parser')
    
    project_data = {}
    project_data['Título'] = soup.find('h1', class_='afd-title-big').text.strip() if soup.find('h1', class_='afd-title-big') else "No disponible"
    project_data['Arquitecto'] = soup.find('a', class_='afd-author-name').text.strip() if soup.find('a', class_='afd-author-name') else "No disponible"
    project_data['Ubicación'] = soup.find('div', class_='afd-project-location').text.strip() if soup.find('div', class_='afd-project-location') else "No disponible"
    project_data['Año'] = soup.find('span', class_='afd-project-year').text.strip() if soup.find('span', class_='afd-project-year') else "No disponible"
    project_data['Fotógrafo'] = ', '.join([photo.text.strip() for photo in soup.find_all('a', class_='afd-photographer-name')]) if soup.find_all('a', class_='afd-photographer-name') else "No disponible"
    
    # Descripción
    description = soup.find('div', class_='afd-article-content')
    project_data['Descripción'] = description.text.strip() if description else "No disponible"
    
    return project_data

def main():
    for url in CATEGORY_URLS:
        try:
            print(f"\n📂 Procesando categoría desde: {url}")
            category = url.split("/categories/")[1].split("?")[0]
            print(f"➡️ Categoría detectada: {category}")

            driver.get(url)
            scroll_to_load_all_content()

            print("🔗 Extrayendo enlaces...")
            elements = driver.find_elements(By.CSS_SELECTOR, "a.gridview__content")
            project_links = [e.get_attribute("href") for e in elements if e.get_attribute("href")]

            output_file = f"{category}_links.txt"
            with open(output_file, "w") as f:
                for link in project_links:
                    f.write(link + "\n")

            print(f"✅ Guardado: {output_file} ({len(project_links)} enlaces)")

        except Exception as e:
            print(f"❌ Error procesando {url}: {e}")

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()  # Asegurarse de cerrar el navegador al final