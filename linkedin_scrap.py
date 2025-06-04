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
    # Opcional: ejecutar en modo headless para mayor velocidad
    # chrome_options.add_argument("--headless")

    driver_path = "C:\\chromedriver-win64\\chromedriver.exe"
    service = Service(driver_path)
    wd = webdriver.Chrome(service=service, options=chrome_options)

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

def extract_job_details(wd, job_element, search_keyword, search_count, logging):
    """Extrae los detalles de un trabajo específico"""
    try:
        # Hacer scroll al elemento para asegurarse de que es visible
        wd.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", job_element)
        time.sleep(1)
        
        # Hacer clic en el trabajo
        wd.execute_script("arguments[0].click();", job_element)
        
        # Esperar a que se cargue el panel de detalles
        WebDriverWait(wd, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-unified-top-card__job-title, .job-details-jobs-unified-top-card__job-title"))
        )
        
        time.sleep(2)  # Tiempo adicional para asegurar que todo se cargue
        
    except Exception as e:
        logging.warning(f"Error al hacer clic en el trabajo: {e}")
        return None

    # Extraer job_id de la URL o del elemento
    try:
        job_id = wd.current_url.split("/view/")[1].split("/")[0] if "/view/" in wd.current_url else ''
        if not job_id:
            # Intentar obtener del atributo del elemento
            job_urn = job_element.get_attribute("data-occludable-entity-urn")
            job_id = job_urn.split(":")[-1] if job_urn else ''
    except:
        job_id = ''

    # Extraer título del trabajo
    try:
        job_title_selectors = [
            "h2.jobs-unified-top-card__job-title a",
            "h2.jobs-unified-top-card__job-title",
            ".job-details-jobs-unified-top-card__job-title a",
            ".job-details-jobs-unified-top-card__job-title"
        ]
        job_title = ''
        for selector in job_title_selectors:
            try:
                job_title = wd.find_element(By.CSS_SELECTOR, selector).text.strip()
                if job_title:
                    break
            except:
                continue
    except:
        job_title = ''

    # Extraer información primaria (empresa, ubicación, remoto)
    try:
        primary_selectors = [
            ".jobs-unified-top-card__primary-description span",
            ".job-details-jobs-unified-top-card__primary-description span"
        ]
        company = location = remote = ''
        for selector in primary_selectors:
            try:
                primary_info = wd.find_elements(By.CSS_SELECTOR, selector)
                if primary_info:
                    company = primary_info[0].text.strip() if len(primary_info) > 0 else ''
                    location = primary_info[1].text.strip() if len(primary_info) > 1 else ''
                    remote = primary_info[2].text.strip() if len(primary_info) > 2 else ''
                    break
            except:
                continue
    except:
        company = location = remote = ''

    # Extraer insights (tiempo de publicación, aplicantes)
    try:
        insight_selectors = [
            ".jobs-unified-top-card__job-insight span",
            ".job-details-jobs-unified-top-card__job-insight span"
        ]
        update_time = applicants = ''
        for selector in insight_selectors:
            try:
                insights = wd.find_elements(By.CSS_SELECTOR, selector)
                if insights:
                    update_time = insights[0].text.strip() if len(insights) > 0 else ''
                    applicants_text = insights[1].text.strip() if len(insights) > 1 else ''
                    applicants = applicants_text.split(' ')[0] if applicants_text else ''
                    break
            except:
                continue
    except:
        update_time = applicants = ''

    # Extraer información del trabajo (tiempo, posición, salario)
    job_time = job_position = job_pay = ''
    try:
        job_info_selectors = [
            ".jobs-unified-top-card__job-insight-text-container",
            ".job-details-jobs-unified-top-card__job-insight-text-container"
        ]
        for selector in job_info_selectors:
            try:
                job_info_element = wd.find_element(By.CSS_SELECTOR, selector)
                job_info_text = job_info_element.text.strip()
                if job_info_text:
                    job_info = job_info_text.split(' · ')
                    if len(job_info) == 1:
                        job_time = job_info[0]
                    elif "$" in job_info[0]:
                        job_pay, job_time = job_info[0], job_info[1]
                        job_position = job_info[2] if len(job_info) > 2 else ''
                    else:
                        job_time = job_info[0]
                        job_position = job_info[1] if len(job_info) > 1 else ''
                    break
            except:
                continue
    except:
        pass

    # Extraer información de la empresa
    try:
        company_info_selectors = [
            ".jobs-unified-top-card__company-info",
            ".job-details-jobs-unified-top-card__company-info"
        ]
        company_size = company_industry = ''
        for selector in company_info_selectors:
            try:
                company_info_element = wd.find_element(By.CSS_SELECTOR, selector)
                company_info = company_info_element.text.strip().split(' · ')
                if company_info:
                    company_size = company_info[0] if len(company_info) > 0 else ''
                    company_industry = company_info[1] if len(company_info) > 1 else ''
                    break
            except:
                continue
    except:
        company_size = company_industry = ''

    # Extraer descripción del trabajo
    try:
        job_details_selectors = [
            "div.jobs-description__content div.jobs-box__html-content",
            ".jobs-description-content__text",
            ".jobs-box__html-content"
        ]
        job_details = ''
        for selector in job_details_selectors:
            try:
                job_details_element = wd.find_element(By.CSS_SELECTOR, selector)
                job_details = job_details_element.text.replace("\n", " ").strip()
                if job_details:
                    break
            except:
                continue
    except:
        job_details = ''

    # Crear registro del trabajo
    date_time = datetime.datetime.now().strftime("%d%b%Y-%H:%M:%S")
    search_keyword_clean = search_keyword.replace("%20", " ")
    
    job_data = [
        date_time, search_keyword_clean, search_count, job_id, job_title, company,
        location, remote, update_time, applicants, job_pay, job_time, job_position,
        company_size, company_industry, job_details
    ]
    
    logging.info(f"Trabajo extraído: {job_title} en {company}")
    return job_data

def page_search(wd, search_location, search_keyword, search_remote, search_posted, search_page, search_count, file, logging):
    url_search = f"https://www.linkedin.com/jobs/search/?f_TPR={search_posted}&f_WRA={search_remote}&geoId=92000000&keywords={search_keyword}&location={search_location}&start={search_page}"
    wd.get(url_search)

    try:
        WebDriverWait(wd, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list")))
    except TimeoutException:
        logging.warning("Timeout esperando los resultados.")
        return search_page + 25, search_count, url_search

    # Obtener el conteo de resultados
    try:
        search_count_element = wd.find_element(By.CLASS_NAME, "results-context-header__job-count")
        search_count_text = search_count_element.text
        search_count = int(search_count_text.replace(',', '').strip())
    except:
        logging.warning("No se pudo obtener el conteo de resultados.")
        return search_page + 25, search_count, url_search

    logging.info(f"Cargando página {round(search_page/25) + 1} de {round(search_count/25)} para {search_keyword} ({search_count} resultados)...")

    # Obtener lista de trabajos
    job_selectors = [
        "li[data-occludable-entity-urn]",
        ".jobs-search-results__list-item",
        ".job-search-card"
    ]
    
    jobs = []
    for selector in job_selectors:
        try:
            jobs = wd.find_elements(By.CSS_SELECTOR, selector)
            if jobs:
                logging.info(f"Encontrados {len(jobs)} trabajos usando selector: {selector}")
                break
        except:
            continue
    
    if not jobs:
        logging.warning("No se encontraron trabajos en esta página.")
        return search_page + 25, search_count, url_search

    list_jobs = []
    
    # Iterar por cada trabajo individualmente
    for index, job in enumerate(jobs):
        try:
            logging.info(f"Procesando trabajo {index + 1} de {len(jobs)}")
            
            # Extraer detalles del trabajo
            job_data = extract_job_details(wd, job, search_keyword, search_count, logging)
            
            if job_data:
                list_jobs.append(job_data)
            
            # Pequeña pausa entre trabajos para evitar ser detectado
            time.sleep(1)
            
        except Exception as e:
            logging.warning(f"Error procesando trabajo {index + 1}: {e}")
            continue

    # Guardar los trabajos en el archivo CSV
    if list_jobs:
        with open(file, "a", encoding="utf-8", newline='') as f:
            w = csv.writer(f)
            w.writerows(list_jobs)
        logging.info(f"Página {round(search_page/25) + 1} completada. {len(list_jobs)} trabajos guardados.")
    else:
        logging.warning("No se pudieron extraer trabajos de esta página.")

    return search_page + 25, search_count, url_search

# MAIN SCRIPT
if __name__ == "__main__":
    logging = create_logfile()
    date = datetime.date.today().strftime('%d-%b-%y')
    file = f"output/{date}.csv"
    create_file(file, logging)
    
    try:
        wd = login(logging)
        
        search_keywords = ['Data Analyst', 'Data Scientist', 'Data Engineer']
        search_location = "Worldwide"
        search_remote = "true"
        search_posted = "r86400"  # Últimas 24 horas

        for search_keyword in search_keywords:
            logging.info(f"Iniciando búsqueda para: {search_keyword}")
            search_keyword_encoded = search_keyword.lower().replace(" ", "%20")
            search_page = 0
            search_count = 1
            max_pages = 10  # Limitar a 10 páginas para evitar problemas
            
            while search_page < search_count and search_page < max_pages * 25:
                try:
                    search_page, search_count, url_search = page_search(
                        wd, search_location, search_keyword_encoded, search_remote, 
                        search_posted, search_page, search_count, file, logging
                    )
                    
                    # Pausa entre páginas
                    time.sleep(3)
                    
                except Exception as e:
                    logging.error(f"Error en página {search_page} para {search_keyword}: {e}")
                    search_page += 25
                    time.sleep(5)  # Pausa más larga si hay error
            
            logging.info(f"Búsqueda completada para: {search_keyword}")
            
    except Exception as e:
        logging.error(f"Error general en el script: {e}")
    finally:
        try:
            wd.quit()
            logging.info("Driver cerrado correctamente.")
        except:
            pass