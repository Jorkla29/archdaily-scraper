from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Usar webdriver-manager para obtener automáticamente ChromeDriver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()

# Inicia el navegador
driver = webdriver.Chrome(service=service, options=options)

# Prueba cargando una página
driver.get("https://www.google.com")
print(driver.title)

# Cierra el navegador
driver.quit()