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

# URL pública de ArchDaily con filtro deseado
SEARCH_URL = "https://www.archdaily.com/search/projects/country/united-states/ "

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

# Ejecutar el proceso completo
def main():
    print("Cargando la página y obteniendo HTML renderizado...")
    get_rendered_html(SEARCH_URL)
    project_links = get_project_links_from_dom()
    
    all_projects = []
    for i, url in enumerate(project_links):
        try:
            print(f"[{i+1}/{len(project_links)}] Procesando: {url}")
            project = scrape_project(url)
            all_projects.append(project)
            time.sleep(2)  # Evitar ser bloqueado por demasiadas solicitudes rápidas
        except Exception as e:
            print(f"Error procesando {url}: {e}")
    
    # Guardar los datos en un archivo Excel
    df = pd.DataFrame(all_projects)
    df.to_excel("proyectos_California.xlsx", index=False)
    print("Datos guardados en 'proyectos_nude_interiors.xlsx'")

if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()  # Asegurarse de cerrar el navegador al final