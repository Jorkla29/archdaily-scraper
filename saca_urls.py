import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Recibir URL desde argumento
url_base = sys.argv[1]

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

driver.get(url_base)
time.sleep(2)  # esperar a que cargue JS

project_urls = []
links = driver.find_elements(By.CSS_SELECTOR, '.afd-search-list__title a')
for link in links:
    href = link.get_attribute('href')
    if href:
        project_urls.append(href)

driver.quit()

# Imprimir JSON por stdout para n8n
print(json.dumps(project_urls))