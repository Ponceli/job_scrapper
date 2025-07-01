import os
import csv
import time
import random
from dotenv import load_dotenv
import logging
import datetime
import re
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException
import json

load_dotenv()

class PageReloadedException(Exception):
    """Excepción personalizada para indicar que la página se recargó inesperadamente."""
    pass

def create_logfile():
    """
    Crea un archivo de log con la fecha y hora actuales en un directorio 'log'.
    Configura el sistema de logging para el script de manera más explícita.
    """
    date_time = datetime.datetime.today().strftime('%d-%b-%y_%H-%M-%S')
    log_directory = 'log'
    os.makedirs(log_directory, exist_ok=True)
    logfile = os.path.join(log_directory, f'{date_time}.log')

    # Obtener el logger raíz
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) # Cambiar a logging.DEBUG para más verbosidad

    # Crear un manejador de archivos para escribir los logs en el archivo
    file_handler = logging.FileHandler(logfile, mode='w', encoding='utf-8')
    
    # Crear un formateador para los mensajes de log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    file_handler.setFormatter(formatter)

    # Eliminar cualquier manejador existente para evitar duplicados o conflictos
    # Esto es similar a 'force=True' pero más granular y seguro
    if logger.hasHandlers():
        logger.handlers.clear()

    # Añadir el manejador de archivos al logger
    logger.addHandler(file_handler)

    # Opcional: Añadir un manejador de consola para ver los logs en la terminal también
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.info(f'Archivo de log {logfile} creado y configurado.')
    return logging # Devuelve el módulo logging ya configurado

def create_file(file, logging):
    """
    Crea o sobrescribe un archivo CSV con los encabezados definidos para almacenar los datos de los trabajos.
    """
    if os.path.exists(file):
        os.remove(file)
        logging.info(f"{file} borrado para una nueva ejecución.")
    else:
        logging.info(f"{file} no existe, se creará uno nuevo.")

    os.makedirs(os.path.dirname(file), exist_ok=True)
    header = ['date_time', 'search_keyword', 'search_count', 'job_id', 'job_title',
              'company', 'location', 'remote', 'update_time', 'applicants', 'job_pay',
              'job_time', 'job_position', 'company_size', 'company_industry', 'job_details', 'job_url']
    with open(file, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
    logging.info(f"Archivo CSV '{file}' creado con éxito.")

def login(logging):
    url_login = "https://www.linkedin.com/login"
    LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME", "")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--enable-webgl-developer-extensions")
    chrome_options.add_argument("--disable-component-update")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument("--disable-features=RendererCodeIntegrity")
    chrome_options.add_argument("--disable-setuid-sandbox")

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.60",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    driver_path = "C:\\chromedriver-win64\\chromedriver.exe"
    service = Service(driver_path)
    wd = webdriver.Chrome(service=service, options=chrome_options)
    
    wd.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wd.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]});")
    wd.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en-US', 'en', 'fr-FR']});")
    wd.execute_script("Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});")
    
    logging.info(f"Iniciando sesión en LinkedIn como {LINKEDIN_USERNAME}...")
    wd.get(url_login)
    time.sleep(random.uniform(7, 12))

    try:
        WebDriverWait(wd, 40).until(EC.presence_of_element_located((By.ID, "username")))
        wd.find_element(By.ID, "username").send_keys(LINKEDIN_USERNAME)
        wd.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        
        time.sleep(random.uniform(1.5, 1.5))
        wd.find_element(By.XPATH, "//button[@type='submit']").click()
        logging.info("Login: Credenciales enviadas.")
    except Exception as e:
        logging.error("Login: No se encontró el formulario de login o falló el envío de credenciales.")
        logging.error(f"Error detallado durante el login: {e}")
        wd.save_screenshot("debug_screenshot_login_fail.png")
        logging.info("Login: Captura de pantalla de fallo de login guardada en debug_screenshot_login_fail.png")
        raise

    try:
        WebDriverWait(wd, 35).until(EC.presence_of_element_located((By.ID, "global-nav-search")))
        logging.info("Login: Navegación exitosa a la página principal después del login.")
    except TimeoutException:
        logging.error("Login: Timeout al esperar la barra de búsqueda global después del login. Posiblemente el login falló, hay un CAPTCHA, o la página está muy lenta.")
        wd.save_screenshot("debug_screenshot_post_login_timeout.png")
        logging.info("Login: Captura de pantalla de timeout post-login guardada en debug_screenshot_post_login_timeout.png")
        raise
    time.sleep(random.uniform(10, 18))
    return wd

def get_all_job_cards_on_page(wd, logging):
    job_cards = []
    try:
        WebDriverWait(wd, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.scaffold-layout__list-item[data-occludable-job-id]")))
        
        all_potential_cards = wd.find_elements(By.CSS_SELECTOR, "li.scaffold-layout__list-item[data-occludable-job-id]")
        
        logging.debug(f"Total de elementos potenciales con data-occludable-job-id: {len(all_potential_cards)}")

        for card in all_potential_cards:
            current_job_id = card.get_attribute("data-occludable-job-id")
            if card.is_displayed() and current_job_id:
                try:
                    wd.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(random.uniform(0.1, 0.4))
                    job_cards.append(card)
                except StaleElementReferenceException:
                    logging.warning(f"StaleElementReferenceException al intentar desplazar a la tarjeta con ID: {current_job_id}. Saltando esta tarjeta.")
                    continue
                except Exception as e:
                    logging.warning(f"Error al procesar la visibilidad y scroll de la tarjeta con ID: {current_job_id}: {e}. Saltando.")
                    continue
            else:
                logging.debug(f"Tarjeta no visible o sin Job ID ('{current_job_id}'). Saltando.")
    except TimeoutException:
        logging.warning("Timeout: No se encontraron tarjetas de trabajo en la página dentro del tiempo esperado. Puede que no haya resultados o la carga es muy lenta.")
    except Exception as e:
        logging.error(f"Error general obteniendo las tarjetas de trabajos visibles: {e}")
        try:
            alternative_cards = wd.find_elements(By.CSS_SELECTOR, "ul.jobs-search-results__list > li")
            logging.info(f"Intentando selector alternativo. Encontradas {len(alternative_cards)} potenciales tarjetas.")
            for card in alternative_cards:
                current_job_id = card.get_attribute("data-occludable-job-id")
                if card.is_displayed() and current_job_id:
                    job_cards.append(card)
        except Exception as alt_e:
            logging.error(f"Error con selector alternativo también: {alt_e}")
            wd.save_screenshot(f"debug_screenshot_get_cards_fail.png")
            logging.info(f"Captura de pantalla guardada en debug_screenshot_get_cards_fail.png")

    logging.info(f"Encontradas {len(job_cards)} tarjetas de trabajos válidas y visibles en la página.")
    return job_cards


def scrape_job_details(wd, job_card_element, search_keyword, search_count, logging):
    job_id = ''
    job_url = ''
    initial_url_of_list_page = wd.current_url

    try:
        job_id = job_card_element.get_attribute("data-occludable-job-id")
        link_element_in_card = job_card_element.find_element(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
        job_url = link_element_in_card.get_attribute('href')
    except (NoSuchElementException, Exception) as e:
        logging.warning(f"No se pudo obtener job_id o URL de la tarjeta antes del clic: {e}. Se intentará de nuevo después del clic. Tarjeta: {job_card_element.text[:50]}...")

    logging.info(f"Preparando para scrapear tarjeta de trabajo (ID: {job_id if job_id else 'desconocido'}).")
    
    try:
        try:
            wd.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card_element)
            time.sleep(random.uniform(0.5, 1.0))
            job_card_element.click()
            logging.debug(f"Clic normal en tarjeta de trabajo (ID: {job_id}) exitoso.")
        except StaleElementReferenceException:
            logging.warning("StaleElementReferenceException al intentar clic normal. Intentando clic con JavaScript.")
            wd.execute_script("arguments[0].click();", job_card_element)
            logging.debug(f"Clic con JavaScript en tarjeta de trabajo (ID: {job_id}) exitoso.")
        except Exception as e:
            logging.warning(f"Error al intentar clic normal: {e}. Intentando clic con JavaScript para ID: {job_id}.")
            wd.execute_script("arguments[0].click();", job_card_element)
            logging.debug(f"Clic con JavaScript (segundo intento) en tarjeta de trabajo (ID: {job_id}) exitoso.")
            
        time.sleep(random.uniform(6, 9))

        WebDriverWait(wd, 45).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__job-details--container h1.t-24.t-bold.inline"))
        )
        logging.info("Detalles del trabajo en el panel lateral cargados exitosamente.")
        time.sleep(random.uniform(3.5, 6))

        if "/jobs/view/" in wd.current_url and wd.current_url != initial_url_of_list_page:
            logging.error(f"¡ADVERTENCIA CRÍTICA! La URL de la página cambió a la página de detalles del trabajo ({wd.current_url}). "
                          f"Esto significa que no se mantuvo en la página de lista de resultados. Se levantará una excepción para re-evaluar la lista de trabajos.")
            wd.save_screenshot(f"debug_screenshot_redirect_to_detail_{job_id}.png")
            logging.info(f"Captura de pantalla guardada en debug_screenshot_redirect_to_detail_{job_id}.png")
            raise PageReloadedException("Página recargada y redirigida a detalles del trabajo.")

    except TimeoutException:
        logging.warning(f"Timeout al esperar que los detalles del trabajo carguen en el panel lateral después del clic para el trabajo con ID: {job_id}. Saltando este trabajo.")
        wd.save_screenshot(f"debug_screenshot_detail_timeout_{job_id}.png")
        logging.info(f"Captura de pantalla guardada en debug_screenshot_detail_timeout_{job_id}.png")
        return None
    except PageReloadedException as e:
        raise e
    except StaleElementReferenceException:
        logging.warning(f"StaleElementReferenceException para ID {job_id} al intentar interactuar con la tarjeta. Se re-obtendrá la lista completa de tarjetas de trabajo y se reanudará desde el siguiente trabajo.")
        return None
    except WebDriverException as e:
        logging.error(f"WebDriverException durante scrape_job_details para ID {job_id}: {e}. La sesión del navegador puede haberse perdido.")
        wd.save_screenshot(f"debug_screenshot_webdriver_exception_{job_id}.png")
        logging.info(f"Captura de pantalla guardada en debug_screenshot_webdriver_exception_{job_id}.png")
        raise e
    except Exception as e:
        logging.warning(f"Error general al intentar hacer clic o cargar detalles del trabajo con ID: {job_id}: {e}. Saltando este trabajo.")
        wd.save_screenshot(f"debug_screenshot_generic_detail_error_{job_id}.png")
        logging.info(f"Captura de pantalla guardada en debug_screenshot_generic_detail_error_{job_id}.png")
        return None

    if not job_id:
        try:
            current_job_url_after_click = wd.current_url
            match = re.search(r'/jobs/view/(\d+)/', current_job_url_after_click)
            if match:
                job_id = match.group(1)
                logging.info(f"Job ID recuperado de la URL de detalles: {job_id}")
            else:
                logging.warning(f"No se pudo extraer el Job ID de la URL de detalles. URL actual: {current_job_url_after_click}")
        except Exception as e:
            logging.warning(f"Error al intentar obtener Job ID de la URL después del clic: {e}")

    job_title = ''
    try:
        element = wd.find_element(By.CSS_SELECTOR, ".jobs-search__job-details--container .job-details-jobs-unified-top-card__job-title h1.t-24.t-bold.inline")
        job_title = element.text.strip()
    except NoSuchElementException:
        logging.warning(f"No se encontró el título del trabajo para ID {job_id}.")

    company = ''
    try:
        element = wd.find_element(By.CSS_SELECTOR, ".jobs-search__job-details--container .job-details-jobs-unified-top-card__company-name a")
        company = element.text.strip()
    except NoSuchElementException:
        logging.warning(f"No se encontró el nombre de la empresa para ID {job_id}.")

    location = ''
    update_time = ''
    applicants = ''
    remote = 'false'

    try:
        tertiary_desc_element = wd.find_element(By.CSS_SELECTOR, ".jobs-search__job-details--container .job-details-jobs-unified-top-card__tertiary-description-container span[dir='ltr']")
        full_text = tertiary_desc_element.text.strip()

        parts = full_text.split('·')
        if len(parts) >= 1:
            location = parts[0].strip()
            if 'remoto' in location.lower() or 'remote' in location.lower():
                remote = 'true'
        if len(parts) >= 2:
            update_time = parts[1].strip()
        if len(parts) >= 3:
            applicants_text = parts[2].strip()
            if 'solicitudes' in applicants_text.lower() or 'applicants' in applicants_text.lower():
                applicants = "".join(filter(str.isdigit, applicants_text))

        if remote == 'false':
            try:
                remote_insight = wd.find_element(By.XPATH, "//li[contains(@class, 'job-details-jobs-unified-top-card__job-insight')]//span[contains(text(), 'En remoto')]")
                if remote_insight and remote_insight.is_displayed():
                    remote = 'true'
            except NoSuchElementException:
                pass
            except Exception as e:
                logging.warning(f"Error al verificar la insignia de remoto: {e}")

    except NoSuchElementException:
        logging.warning(f"No se encontró la descripción terciaria (ubicación, tiempo, aplicantes) para ID {job_id}.")

    company_size = ''
    company_industry = ''
    try:
        company_info_elements = wd.find_elements(By.CSS_SELECTOR, ".jobs-search__job-details--container .job-details-jobs-unified-top-card__job-insight span[dir='ltr']")
        for el in company_info_elements:
            text = el.text.strip().lower()
            if 'empleados' in text or 'employees' in text:
                company_size = el.text.strip()
            if 'industria' in text or 'industry' in text:
                company_industry = el.text.strip()
    except NoSuchElementException:
        pass

    job_pay = ''
    job_time = ''
    job_position = ''

    job_details = ''
    try:
        element = wd.find_element(By.CSS_SELECTOR, "div.jobs-box__html-content#job-details")
        try:
            show_more_button = element.find_element(By.CSS_SELECTOR, "button[data-job-details-show-more-button='true']")
            if show_more_button.is_displayed():
                wd.execute_script("arguments[0].click();", show_more_button)
                time.sleep(random.uniform(0.5, 1.5))
        except NoSuchElementException:
            pass
        job_details = element.text.replace('\n', ' ').strip()
    except NoSuchElementException:
        logging.warning(f"No se encontró la descripción del trabajo para ID {job_id}.")

    date_time = datetime.datetime.now().strftime("%d%b%Y-%H:%M:%S")
    search_keyword_clean = search_keyword.replace("%20", " ")

    job_data_csv = [
        date_time, search_keyword_clean, search_count, job_id, job_title, company,
        location, remote, update_time, applicants, job_pay, job_time, job_position,
        company_size, company_industry, job_details, job_url
    ]

    job_data_json = {
        "id": job_id,
        "input": "LINKEDIN",
        "empresa": company,
        "titulo": job_title,
        "descripcion": job_details,
        "url": job_url
    }

    logging.info(f"Trabajo extraído exitosamente: '{job_title}' en '{company}' (ID: {job_id})")
    return job_data_csv, job_data_json


def page_search(wd, search_location, search_keyword, search_remote, search_posted, file, logging, all_scraped_jobs_json):
    MAX_PAGES_TO_SCRAPE = 3
    current_page_number = 1

    url_search = f"https://www.linkedin.com/jobs/search/?f_TPR={search_posted}&f_WRA={search_remote}&geoId=92000000&keywords={search_keyword}&location={search_location}&start=0"
    logging.info(f"Navegando a la URL de búsqueda inicial: {url_search}")
    wd.get(url_search)
    time.sleep(random.uniform(10, 15))

    logging.info(f"URL actual después de la navegación: {wd.current_url}")

    try:
        WebDriverWait(wd, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.scaffold-layout__list-item[data-occludable-job-id]")))
        logging.info("Lista de resultados de búsqueda inicial encontrada y visible.")
        
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
        time.sleep(random.uniform(1, 2))
        wd.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(1, 2))

    except TimeoutException:
        logging.error("¡ERROR CRÍTICO! Timeout esperando la lista de resultados de la búsqueda (primer elemento LI). La página no cargó la lista principal o no es visible.")
        wd.save_screenshot(f"debug_screenshot_timeout_initial_results_{search_keyword}.png")
        logging.info(f"Captura de pantalla guardada en debug_screenshot_timeout_initial_results_{search_keyword}.png")
        return 0

    search_count = 0
    try:
        search_count_element = wd.find_element(By.CLASS_NAME, "results-context-header__job-count")
        search_count_text = search_count_element.text
        search_count = int("".join(filter(str.isdigit, search_count_text)))
        logging.info(f"Conteo inicial de resultados: {search_count_text}")
    except (NoSuchElementException, ValueError):
        logging.warning("No se pudo obtener el conteo de resultados inicial. Intentando selectores alternativos o asumiendo un conteo bajo.")
        try:
            alt_count_element = wd.find_element(By.XPATH, "//h1[contains(@class, 'jobs-search-results__list-heading') and contains(text(), 'resultados')]")
            search_count_text = alt_count_element.text
            search_count = int("".join(filter(str.isdigit, search_count_text)))
            logging.info(f"Conteo inicial de resultados (alternativo): {search_count_text}")
        except (NoSuchElementException, ValueError):
            logging.warning("No se pudo obtener el conteo de resultados con selectores alternativos. Asumiendo 0 para continuar.")
            search_count = 0

    logging.info(f"Iniciando scraping para '{search_keyword}' en '{search_location}' ({search_count} resultados totales esperados)...")

    scraped_jobs_count = 0
    unique_job_ids = set()
    last_processed_job_id_before_refresh = None
    
    while current_page_number <= MAX_PAGES_TO_SCRAPE:
        logging.info(f"--- Procesando Página {current_page_number} de un máximo de {MAX_PAGES_TO_SCRAPE} ---")
        
        all_job_cards_on_page = get_all_job_cards_on_page(wd, logging)
        logging.info(f"Total de tarjetas de trabajo válidas visibles en la página {current_page_number}: {len(all_job_cards_on_page)}")

        if not all_job_cards_on_page and current_page_number > 1:
            logging.info(f"No hay tarjetas de trabajo visibles en la página {current_page_number}. Terminando el scraping de esta palabra clave.")
            break
        elif not all_job_cards_on_page and current_page_number == 1 and search_count > 0:
            logging.warning(f"No se encontraron tarjetas de trabajo en la primera página a pesar de un conteo de resultados ({search_count}). Posiblemente un problema de carga o filtros incorrectos.")
            wd.save_screenshot(f"debug_screenshot_no_cards_page1_{search_keyword}.png")
            logging.info(f"Captura de pantalla guardada en debug_screenshot_no_cards_page1_{search_keyword}.png")
            break

        should_re_evaluate_list = False

        start_index = 0
        if last_processed_job_id_before_refresh:
            found_previous_job_index = -1
            for idx, card in enumerate(all_job_cards_on_page):
                if card.get_attribute("data-occludable-job-id") == last_processed_job_id_before_refresh:
                    found_previous_job_index = idx
                    break
            
            if found_previous_job_index != -1:
                start_index = found_previous_job_index + 1
                logging.info(f"Reanudando el scraping desde el trabajo después de ID: {last_processed_job_id_before_refresh}. Índice: {start_index}")
            else:
                logging.warning(f"No se encontró el trabajo previamente procesado/que causó el refresco (ID: {last_processed_job_id_before_refresh}) en la lista actual. "
                                 "Reiniciando el procesamiento desde el principio de la lista visible de la página actual para evitar saltos. "
                                 "Esto podría indicar un problema de carga o un cambio drástico en los resultados.")
                start_index = 0
            last_processed_job_id_before_refresh = None

        if start_index >= len(all_job_cards_on_page) and len(all_job_cards_on_page) > 0:
            logging.info(f"Ya se han procesado todos los trabajos visibles en la página {current_page_number} hasta el final de la lista. Pasando a la siguiente página (si aplica).")
        
        for i in range(start_index, len(all_job_cards_on_page)):
            job_card_element = all_job_cards_on_page[i]
            current_job_id_from_card = job_card_element.get_attribute("data-occludable-job-id")

            if not current_job_id_from_card:
                logging.warning(f"Tarjeta de trabajo sin 'data-occludable-job-id' en el índice {i}. Saltando este elemento. HTML Parcial: {job_card_element.get_attribute('outerHTML')[:200]}...")
                continue

            if current_job_id_from_card in unique_job_ids:
                logging.info(f"Trabajo con ID {current_job_id_from_card} ya procesado, saltando.")
                continue
            
            logging.info(f"Procesando trabajo {i+1}/{len(all_job_cards_on_page)} (ID: {current_job_id_from_card}).")

            try:
                job_data_csv, job_data_json = scrape_job_details(wd, job_card_element, search_keyword, search_count, logging)

                if job_data_csv and job_data_json:
                    processed_job_id = job_data_csv[3]
                    if processed_job_id and processed_job_id not in unique_job_ids:
                        scraped_jobs_count += 1
                        unique_job_ids.add(processed_job_id)
                        
                        with open(file, "a", encoding="utf-8", newline='') as f:
                            w = csv.writer(f)
                            w.writerow(job_data_csv)
                        
                        all_scraped_jobs_json.append(job_data_json)
                    elif not processed_job_id:
                        logging.warning(f"Trabajo procesado sin un ID válido. No se añadió a la lista de únicos. (ID de tarjeta: {current_job_id_from_card}).")
                else:
                    logging.info(f"Detalles del trabajo no extraídos o saltados para el trabajo con ID: {current_job_id_from_card}.")

                time.sleep(random.uniform(2, 4))

            except PageReloadedException:
                logging.error(f"¡EXCEPCIÓN CRÍTICA! Se detectó una recarga de página durante el raspado de detalles para ID {current_job_id_from_card}. "
                               f"Se re-obtendrá la lista de tarjetas y se reanudará desde el siguiente trabajo.")
                last_processed_job_id_before_refresh = current_job_id_from_card
                should_re_evaluate_list = True
                break
            except StaleElementReferenceException:
                logging.warning(f"StaleElementReferenceException para ID {current_job_id_from_card}. "
                                 f"Se re-obtendrá la lista completa de tarjetas de trabajo y se reanudará desde el siguiente trabajo.")
                last_processed_job_id_before_refresh = current_job_id_from_card 
                should_re_evaluate_list = True
                break
            except WebDriverException as e:
                logging.critical(f"WebDriverException inesperada durante el scraping para ID {current_job_id_from_card}: {e}. "
                                 f"Finalizando el scraping para esta palabra clave para reintentar la conexión.")
                raise e
            except Exception as e:
                logging.error(f"Error general procesando tarjeta de trabajo con ID {current_job_id_from_card}: {e}. Continuando con la siguiente.")
                continue

        if should_re_evaluate_list:
            logging.info("Re-evaluando la lista de trabajos en la página actual debido a un evento de recarga/estancamiento.")
            continue

        initial_page_url = wd.current_url
        
        current_page_number += 1 
        
        if current_page_number > MAX_PAGES_TO_SCRAPE:
            logging.info(f"Se ha alcanzado el número máximo de páginas ({MAX_PAGES_TO_SCRAPE}) a scrapear. Terminando paginación para '{search_keyword}'.")
            break

        logging.info(f"Intentando pasar a la página {current_page_number} usando el botón 'Siguiente' para '{search_keyword}'...")
        try:
            next_page_button = WebDriverWait(wd, 25).until(
                EC.element_to_be_clickable((By.XPATH, 
                    "//button[@aria-label='Ver siguiente página'] | "
                    "//button[contains(@class, 'jobs-search-pagination__next') and (.//span[text()='Next'] or .//span[text()='Siguiente'])]"
                ))
            )
            
            wd.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
            time.sleep(random.uniform(1.0, 2.0))
            wd.execute_script("arguments[0].click();", next_page_button)
            logging.info(f"Clic en el botón 'Siguiente' exitoso para '{search_keyword}'.")

            WebDriverWait(wd, 30).until(
                lambda driver: driver.current_url != initial_page_url or \
                                EC.presence_of_element_located((By.CSS_SELECTOR, "li.scaffold-layout__list-item[data-occludable-job-id]"))(driver)
            )
            logging.info(f"La página {current_page_number} se cargó correctamente después de hacer clic en 'Siguiente' para '{search_keyword}'.")

            time.sleep(random.uniform(8, 12))

            wd.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
            time.sleep(random.uniform(1, 2))
            wd.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(1, 2))
        
        except TimeoutException:
            logging.warning(f"Timeout: No se encontró el botón 'Siguiente' o la siguiente página no cargó para '{search_keyword}'. Terminando la paginación.")
            wd.save_screenshot(f"debug_screenshot_next_page_timeout_{search_keyword}.png")
            logging.info(f"Captura de pantalla guardada en debug_screenshot_next_page_timeout_{search_keyword}.png")
            break
        except NoSuchElementException:
            logging.info(f"El botón 'Siguiente' no se encontró (fin de los resultados o última página) para '{search_keyword}'. Terminando la paginación.")
            break
        except Exception as e:
            logging.error(f"Error general al intentar pasar a la siguiente página para '{search_keyword}': {e}. Terminando la paginación.")
            wd.save_screenshot(f"debug_screenshot_next_page_error_{search_keyword}.png")
            logging.info(f"Captura de pantalla guardada en debug_screenshot_next_page_error_{search_keyword}.png")
            break

    return scraped_jobs_count

def main():
    logging_instance = create_logfile()
    output_csv_file = "output\\linkedin_jobs.csv"
    output_json_file = "output\\linkedin_jobs.json"
    
    create_file(output_csv_file, logging_instance)
    all_scraped_jobs_data_json = []

    wd = None
    try:
        wd = login(logging_instance)
        
        search_keywords = ["Analista de Datos", "Ingeniero de Software"]
        search_locations = ["España", "Estados Unidos"]
        search_remote = "true"
        search_posted = "2592000000"

        for keyword in search_keywords:
            for location in search_locations:
                logging_instance.info(f"Iniciando scraping para palabra clave: '{keyword}' en ubicación: '{location}'")
                try:
                    scraped_count = page_search(wd, location, keyword, search_remote, search_posted, output_csv_file, logging_instance, all_scraped_jobs_data_json)
                    logging_instance.info(f"Se rasparon {scraped_count} trabajos para '{keyword}' en '{location}'.")
                except WebDriverException as e:
                    logging_instance.critical(f"WebDriver ha fallado para '{keyword}' en '{location}': {e}. Reintentando la conexión del driver.")
                    if wd:
                        wd.quit()
                    time.sleep(random.uniform(15, 30))
                    wd = login(logging_instance)
                except Exception as e:
                    logging_instance.error(f"Error inesperado al procesar '{keyword}' en '{location}': {e}")
                time.sleep(random.uniform(5, 10))
        
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(all_scraped_jobs_data_json, f, ensure_ascii=False, indent=4)
        logging_instance.info(f"Todos los datos scrapeados guardados en '{output_json_file}'.")

    except Exception as e:
        logging_instance.critical(f"¡Error fatal en la ejecución principal!: {e}")
        logging_instance.critical("El script se detendrá.")
    finally:
        if wd:
            logging_instance.info("Cerrando el navegador.")
            wd.quit()

if __name__ == '__main__':
    main()