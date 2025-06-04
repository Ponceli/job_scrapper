import os
import csv
import time
from dotenv import load_dotenv
import logging
import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains

load_dotenv()

def create_logfile():
    date_time = datetime.datetime.today().strftime('%d-%b-%y_%H-%M-%S')
    log_directory = 'log'
    os.makedirs(log_directory, exist_ok=True)
    logfile = os.path.join(log_directory, f'{date_time}.log')
    logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', force=True)
    logging.info(f'Log file {logfile} created')
    return logging

def create_file(file, logging):
    if os.path.exists(file):
        os.remove(file)
        logging.info(f"{file} borrado")
    else:
        logging.info(f"{file} no existe")

    os.makedirs(os.path.dirname(file), exist_ok=True)
    header = ['date_time', 'search_keyword', 'search_count', 'job_id', 'job_title',
              'company', 'location', 'remote', 'update_time', 'applicants', 'job_pay',
              'job_time', 'job_position', 'company_size', 'company_industry', 'job_details']
    with open(file, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        logging.info(f"{file} Creado")

def login(logging):
    url_login = "https://www.linkedin.com/login"
    LINKEDIN_USERNAME = "badag85383@jeanssi.com"
    LINKEDIN_PASSWORD = "Eligay123"

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver_path = "C:\\chromedriver-win64\\chromedriver.exe"
    service = Service(driver_path)
    wd = webdriver.Chrome(service=service, options=chrome_options)
    wd.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    logging.info(f"LOGUEANDOME A LINKEDIN COMO {LINKEDIN_USERNAME}...")
    wd.get(url_login)

    try:
        WebDriverWait(wd, 15).until(EC.presence_of_element_located((By.NAME, "session_key")))
        wd.find_element(By.NAME, "session_key").send_keys(LINKEDIN_USERNAME)
        wd.find_element(By.NAME, "session_password").send_keys(LINKEDIN_PASSWORD)
        wd.find_element(By.XPATH, "//button[@type='submit']").click()
        logging.info("Login completado.")
    except Exception as e:
        logging.error("No se encontró el formulario de login.")
        logging.error(e)
        wd.save_screenshot("login_error.png")
        raise

    WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.ID, "global-nav-search")))
    return wd

def get_job_links(wd, search_location, search_keyword, search_remote, search_posted, search_page, logging):
    """Obtiene todos los enlaces de trabajos de una página sin hacer clic en ellos"""
    url_search = f"https://www.linkedin.com/jobs/search/?f_TPR={search_posted}&f_WRA={search_remote}&geoId=92000000&keywords={search_keyword}&location={search_location}&start={search_page}"
    wd.get(url_search)
    
    try:
        WebDriverWait(wd, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list")))
    except TimeoutException:
        logging.warning("Timeout esperando los resultados.")
        return [], 0

    # Obtener el conteo de resultados
    try:
        search_count_element = wd.find_element(By.CLASS_NAME, "results-context-header__job-count")
        search_count_text = search_count_element.text
        search_count = int(search_count_text.replace(',', '').strip())
    except:
        logging.warning("No se pudo obtener el conteo de resultados.")
        search_count = 0

    logging.info(f"Obteniendo enlaces de página {round(search_page/25) + 1} para {search_keyword} ({search_count} resultados totales)...")

    # Hacer scroll para cargar todos los trabajos
    last_height = wd.execute_script("return document.body.scrollHeight")
    while True:
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = wd.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Obtener todos los enlaces de trabajos
    job_links = []
    try:
        # Diferentes selectores para obtener los enlaces
        job_cards = wd.find_elements(By.CSS_SELECTOR, "div.job-search-card, div.jobs-search-results__list-item")
        
        for card in job_cards:
            try:
                # Buscar el enlace dentro de la tarjeta
                link_element = card.find_element(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
                job_url = link_element.get_attribute('href')
                if job_url and '/jobs/view/' in job_url:
                    job_id = job_url.split('/jobs/view/')[1].split('/')[0].split('?')[0]
                    if job_id.isdigit():
                        job_links.append(job_url)
            except:
                continue
        
        # Si no encuentra enlaces con el método anterior, intentar otro selector
        if not job_links:
            links = wd.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
            for link in links:
                job_url = link.get_attribute('href')
                if job_url and '/jobs/view/' in job_url:
                    job_id = job_url.split('/jobs/view/')[1].split('/')[0].split('?')[0]
                    if job_id.isdigit():
                        job_links.append(job_url)
        
        # Eliminar duplicados manteniendo el orden
        seen = set()
        unique_links = []
        for link in job_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        logging.info(f"Encontrados {len(unique_links)} enlaces únicos de trabajos")
        return unique_links, search_count
        
    except Exception as e:
        logging.error(f"Error obteniendo enlaces de trabajos: {e}")
        return [], search_count

def scrape_job_details(wd, job_url, search_keyword, search_count, logging):
    """Scrape los detalles de un trabajo específico accediendo directamente a su URL"""
    try:
        logging.info(f"Accediendo a: {job_url}")
        wd.get(job_url)
        
        # Esperar a que se cargue la página del trabajo
        WebDriverWait(wd, 15).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.top-card-layout__title")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.topcard__title")),
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-unified-top-card__job-title"))
            )
        )
        
        time.sleep(3)  # Esperar a que se cargue completamente
        
    except Exception as e:
        logging.warning(f"Error cargando la página del trabajo: {e}")
        return None

    # Extraer job_id de la URL
    try:
        job_id = job_url.split('/jobs/view/')[1].split('/')[0].split('?')[0]
    except:
        job_id = ''

    # Extraer título del trabajo
    job_title = ''
    title_selectors = [
        "h1.top-card-layout__title",
        "h1.topcard__title", 
        ".jobs-unified-top-card__job-title a",
        ".jobs-unified-top-card__job-title",
        "h1"
    ]
    
    for selector in title_selectors:
        try:
            element = wd.find_element(By.CSS_SELECTOR, selector)
            job_title = element.text.strip()
            if job_title:
                break
        except:
            continue

    # Extraer información de la empresa
    company = location = remote = ''
    company_selectors = [
        ".top-card-layout__card .topcard__org-name-link",
        ".topcard__org-name-link",
        ".topcard__flavor--company",
        ".jobs-unified-top-card__company-name a",
        ".jobs-unified-top-card__company-name"
    ]
    
    for selector in company_selectors:
        try:
            element = wd.find_element(By.CSS_SELECTOR, selector)
            company = element.text.strip()
            if company:
                break
        except:
            continue

    # Extraer ubicación
    location_selectors = [
        ".top-card-layout__card .topcard__flavor--location",
        ".topcard__flavor--location",
        ".jobs-unified-top-card__bullet"
    ]
    
    for selector in location_selectors:
        try:
            element = wd.find_element(By.CSS_SELECTOR, selector)
            location = element.text.strip()
            if location:
                break
        except:
            continue

    # Extraer información adicional (tiempo de publicación, aplicantes, etc.)
    update_time = applicants = job_time = job_position = job_pay = ''
    
    try:
        # Buscar información de tiempo de publicación
        time_selectors = [
            ".posted-time-ago__text",
            ".topcard__flavor--metadata",
            ".jobs-unified-top-card__subtitle-secondary-grouping"
        ]
        
        for selector in time_selectors:
            try:
                element = wd.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if 'ago' in text.lower() or 'hace' in text.lower():
                    update_time = text
                    break
            except:
                continue
    except:
        pass

    # Extraer número de aplicantes
    try:
        applicant_selectors = [
            ".num-applicants__caption",
            "[data-test-id='job-applicant-count']"
        ]
        
        for selector in applicant_selectors:
            try:
                element = wd.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if 'applicant' in text.lower():
                    applicants = text.split()[0]
                    break
            except:
                continue
    except:
        pass

    # Extraer información de la empresa (tamaño, industria)
    company_size = company_industry = ''
    try:
        company_info_selectors = [
            ".top-card-layout__card .topcard__flavor--company-info",
            ".topcard__flavor--company-info"
        ]
        
        for selector in company_info_selectors:
            try:
                elements = wd.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    company_size = elements[0].text.strip() if len(elements) > 0 else ''
                    company_industry = elements[1].text.strip() if len(elements) > 1 else ''
                    break
            except:
                continue
    except:
        pass

    # Extraer descripción del trabajo
    job_details = ''
    description_selectors = [
        ".show-more-less-html__markup",
        ".description__text",
        ".jobs-description-content__text",
        ".jobs-box__html-content"
    ]
    
    for selector in description_selectors:
        try:
            element = wd.find_element(By.CSS_SELECTOR, selector)
            job_details = element.text.replace('\n', ' ').strip()
            if job_details:
                break
        except:
            continue

    # Crear el registro del trabajo
    date_time = datetime.datetime.now().strftime("%d%b%Y-%H:%M:%S")
    search_keyword_clean = search_keyword.replace("%20", " ")
    
    job_data = [
        date_time, search_keyword_clean, search_count, job_id, job_title, company,
        location, remote, update_time, applicants, job_pay, job_time, job_position,
        company_size, company_industry, job_details
    ]
    
    logging.info(f"Trabajo extraído exitosamente: {job_title} en {company}")
    return job_data

def page_search(wd, search_location, search_keyword, search_remote, search_posted, search_page, search_count, file, logging):
    """Función principal que obtiene enlaces y luego scrape cada trabajo individualmente"""
    
    # Paso 1: Obtener todos los enlaces de trabajos de la página
    job_links, search_count = get_job_links(wd, search_location, search_keyword, search_remote, search_posted, search_page, logging)
    
    if not job_links:
        logging.warning("No se encontraron enlaces de trabajos en esta página.")
        return search_page + 25, search_count, ""
    
    # Paso 2: Scrape cada trabajo individualmente
    scraped_jobs = []
    for i, job_url in enumerate(job_links):
        try:
            logging.info(f"Procesando trabajo {i+1}/{len(job_links)}")
            
            job_data = scrape_job_details(wd, job_url, search_keyword, search_count, logging)
            
            if job_data:
                scraped_jobs.append(job_data)
                
                # Guardar después de cada trabajo para no perder datos
                with open(file, "a", encoding="utf-8", newline='') as f:
                    w = csv.writer(f)
                    w.writerow(job_data)
            
            # Pausa entre trabajos para evitar ser detectado
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"Error procesando trabajo {i+1}: {e}")
            continue
    
    logging.info(f"Página {round(search_page/25) + 1} completada. {len(scraped_jobs)} trabajos extraídos de {len(job_links)} enlaces.")
    
    return search_page + 25, search_count, ""

# MAIN SCRIPT
if __name__ == "__main__":
    logging = create_logfile()
    date = datetime.date.today().strftime('%d-%b-%y')
    file = f"output/{date}.csv"
    create_file(file, logging)
    
    wd = None
    try:
        wd = login(logging)
        
        search_keywords = ['Data Analyst', 'Data Scientist', 'Data Engineer']
        search_location = "Worldwide"
        search_remote = "true"
        search_posted = "r86400"  # Últimas 24 horas

        for search_keyword in search_keywords:
            logging.info(f"=== Iniciando búsqueda para: {search_keyword} ===")
            search_keyword_encoded = search_keyword.lower().replace(" ", "%20")
            search_page = 0
            search_count = 1
            max_pages = 5  # Limitar a 5 páginas para pruebas
            
            while search_page < search_count and search_page < max_pages * 25:
                try:
                    search_page, search_count, _ = page_search(
                        wd, search_location, search_keyword_encoded, search_remote, 
                        search_posted, search_page, search_count, file, logging
                    )
                    
                    # Pausa entre páginas
                    time.sleep(5)
                    
                except Exception as e:
                    logging.error(f"Error en página {search_page} para {search_keyword}: {e}")
                    search_page += 25
                    time.sleep(10)
            
            logging.info(f"=== Búsqueda completada para: {search_keyword} ===")
            time.sleep(10)  # Pausa entre keywords
            
    except Exception as e:
        logging.error(f"Error general en el script: {e}")
    finally:
        if wd:
            try:
                wd.quit()
                logging.info("Driver cerrado correctamente.")
            except:
                pass