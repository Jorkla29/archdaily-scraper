from playwright.sync_api import sync_playwright
import time
import os, json, hashlib

def listar_proyectos(categories_slugs, countries_slugs):
    lista_proyectos = []

    filtros = []
    if categories_slugs and countries_slugs:
        for cat in categories_slugs:
            for country in countries_slugs:
                filtros.append(f"/search/projects/categories/{cat}/country/{country}")
    elif categories_slugs:
        for cat in categories_slugs:
            filtros.append(f"/search/projects/categories/{cat}")
    elif countries_slugs:
        for country in countries_slugs:
            filtros.append(f"/search/projects/country/{country}")
    else:
        filtros.append("/search/projects")

    hash_input = json.dumps(filtros, sort_keys=True).encode()
    hash_key = hashlib.md5(hash_input).hexdigest()
    cache_file = f"proyectos_basicos_{hash_key}.json"

    if os.path.exists(cache_file):
        print(f"⚡ Usando cache: {cache_file}")
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://www.archdaily.com/search/projects?ad_medium=filters")
            page.click("text=Accept", timeout=5000)
        except:
            pass

        for path in filtros:
            url = f"https://www.archdaily.com{path}?ad_medium=filters"
            print(f"\n🔍 Accediendo a: {url}")
            page.goto(url)

            try:
                page.wait_for_selector("div.gridview__item", timeout=10000)
                print("✅ Contenido cargado")
            except:
                print("❌ No se encontró contenido para este filtro.")
                continue

            max_intentos = 10
            intento = 0
            previous_count = 0

            while intento < max_intentos:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.25)
                current_count = len(page.query_selector_all("div.gridview__item"))
                print(f"🔄 Scroll... proyectos visibles: {current_count}")
                if current_count == previous_count:
                    intento += 1
                else:
                    intento = 0
                previous_count = current_count

            print("🛑 Scroll completo")

            projects = page.query_selector_all("div.gridview__item")
            print(f"🔢 Proyectos encontrados: {len(projects)}")

            for proyecto in projects:
                try:
                    titulo_element = proyecto.query_selector("h3")
                    enlace_element = proyecto.query_selector("a[href]")
                    if not titulo_element or not enlace_element:
                        continue
                    titulo = titulo_element.inner_text().strip()
                    link = enlace_element.get_attribute("href")
                    lista_proyectos.append({
                        "Título": titulo,
                        "Enlace": link
                    })
                except:
                    continue

        browser.close()
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(lista_proyectos, f, ensure_ascii=False, indent=2)
    return lista_proyectos


def scrapear_detalles(lista_basica, progreso_callback=None):
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for item in lista_basica:
            try:
                if progreso_callback:
                    progreso_callback(lista_basica.index(item) + 1, len(lista_basica), item["Título"])
                link = item["Enlace"]
                titulo = item["Título"]

                detalle = browser.new_page()
                detalle.goto(link)
                detalle.wait_for_timeout(1000)

                categorias = [
                    el.inner_text().strip()
                    for el in detalle.query_selector_all(".afd-specs__header-category a")
                ]
                categoria = ", ".join(categorias)
                categoria_principal = categorias[0] if categorias else ""
                ubicacion_el = detalle.query_selector(".afd-specs__header-location")
                ubicacion = ubicacion_el.inner_text().strip() if ubicacion_el else ""

                arquitecto_el = detalle.query_selector(".afd-specs__architects a")
                arquitecto = arquitecto_el.inner_text().strip() if arquitecto_el else ""
                arquitecto_link = arquitecto_el.get_attribute("href") if arquitecto_el else ""

                area_el = detalle.locator("li:has(span.afd-specs__key:has-text('Area')) span.afd-specs__value").first
                area = area_el.inner_text().strip() if area_el else ""

                anio_el = detalle.locator("li:has(span.afd-specs__key:has-text('Year')) span.afd-specs__value").first
                anio = anio_el.inner_text().strip() if anio_el else ""

                foto_el = detalle.query_selector(".afd-specs__photographers a")
                fotografo = foto_el.inner_text().strip() if foto_el else ""

                web = ""
                if arquitecto_link:
                    try:
                        detalle.goto(arquitecto_link)
                        detalle.wait_for_timeout(1000)
                        web_el = detalle.query_selector("a.js-office-website")
                        web = web_el.get_attribute("href") if web_el else ""
                    except:
                        pass

                detalle.close()

                data.append({
                    "Título": titulo,
                    "Enlace": link,
                    "Categoría": categoria,
                    "Categoría Principal": categoria_principal,
                    "Ubicación": ubicacion,
                    "Arquitecto": arquitecto,
                    "Área": area,
                    "Año": anio,
                    "Fotógrafo": fotografo,
                    "Web/Email": web
                })

            except Exception as e:
                print(f"⚠️ Error al procesar proyecto completo: {e}")
                continue

        browser.close()
    return data