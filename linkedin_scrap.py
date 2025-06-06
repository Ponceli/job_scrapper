import os
import csv
import time
import random
from dotenv import load_dotenv
import logging
import datetime
import re # Importar para regex si es necesario
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver import ActionChains

load_dotenv()

class PageReloadedException(Exception):
    """Excepción personalizada para indicar que la página se recargó inesperadamente."""
    pass

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
              'job_time', 'job_position', 'company_size', 'company_industry', 'job_details', 'job_url']
    with open(file, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
    logging.info(f"{file} Creado")

def login(logging):
    url_login = "https://www.linkedin.com/login"
    LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME", "kideve4885@cigidea.com")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "Eligay123")

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # chrome_options.add_argument("--headless") # Descomentar para ejecutar en modo sin cabeza
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
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    driver_path = "C:\\chromedriver-win64\\chromedriver.exe"
    service = Service(driver_path)
    wd = webdriver.Chrome(service=service, options=chrome_options)
    
    wd.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wd.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]});")
    wd.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en-US', 'en', 'fr-FR']});")
    wd.execute_script("Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});")
    
    logging.info(f"LOGUEANDOME A LINKEDIN COMO {LINKEDIN_USERNAME}...")
    wd.get(url_login)
    time.sleep(random.uniform(7, 12))

    try:
        WebDriverWait(wd, 40).until(EC.presence_of_element_located((By.ID, "username")))
        wd.find_element(By.ID, "username").send_keys(LINKEDIN_USERNAME)
        wd.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        
        time.sleep(random.uniform(1.5, 3.5))
        wd.find_element(By.XPATH, "//button[@type='submit']").click()
        logging.info("Login completado.")
    except Exception as e:
        logging.error("No se encontró el formulario de login o falló el clic.")
        logging.error(e)
        raise

    try:
        WebDriverWait(wd, 35).until(EC.presence_of_element_located((By.ID, "global-nav-search")))
        logging.info("Navegación exitosa a la página principal después del login.")
    except TimeoutException:
        logging.error("Timeout al esperar la barra de búsqueda global después del login. Posiblemente el login falló o hay un CAPTCHA.")
        raise
    time.sleep(random.uniform(10, 18))
    return wd

def get_all_job_cards_on_page(wd, logging):
    """
    Obtiene todos los elementos (tarjetas) de los trabajos actualmente visibles en la página.
    Se ha vuelto al selector original de <li> con data-occludable-job-id.
    Retorna una lista de elementos WebElement de las tarjetas de trabajo.
    """
    job_cards = []
    try:
        # **CAMBIO CLAVE AQUÍ: VOLVEMOS AL SELECTOR ORIGINAL DEL <li> PADRE**
        # Y esperamos por la presencia de CUALQUIERA de estos elementos, lo que indica que la lista está cargada.
        WebDriverWait(wd, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.scaffold-layout__list-item[data-occludable-job-id]")))
        
        # Obtenemos todos los elementos <li> con el atributo data-occludable-job-id
        all_potential_cards = wd.find_elements(By.CSS_SELECTOR, "li.scaffold-layout__list-item[data-occludable-job-id]")
        
        for card in all_potential_cards:
            # El job_id ahora se obtiene del atributo data-occludable-job-id del <li>
            current_job_id = card.get_attribute("data-occludable-job-id")
            if card.is_displayed() and current_job_id: # Verificar que esté visible y tenga ID
                try:
                    ActionChains(wd).move_to_element(card).perform()
                    time.sleep(random.uniform(0.1, 0.4))
                    job_cards.append(card)
                except StaleElementReferenceException:
                    logging.warning("StaleElementReferenceException al intentar mover el mouse a una tarjeta. Saltando esta tarjeta.")
                    continue
    except Exception as e:
        logging.error(f"Error obteniendo las tarjetas de trabajos visibles: {e}")

    logging.info(f"Encontradas {len(job_cards)} tarjetas de trabajos actualmente visibles y válidas en la página.")
    return job_cards


def scrape_job_details(wd, job_card_element, search_keyword, search_count, logging):
    """
    Scrapea los detalles de un trabajo específico haciendo clic en su tarjeta en la lista
    y extrayendo la información del panel lateral.
    """
    job_id = ''
    job_url = ''
    initial_url_of_list_page = wd.current_url

    try:
        # **CAMBIO CLAVE AQUÍ: El job_id ahora se obtiene de data-occludable-job-id del <li>**
        job_id = job_card_element.get_attribute("data-occludable-job-id")
        
        # El selector para la URL se mantiene, ya que sigue siendo un 'a' con ese href dentro de la tarjeta
        link_element_in_card = job_card_element.find_element(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
        job_url = link_element_in_card.get_attribute('href')
    except (NoSuchElementException, Exception) as e:
        logging.warning(f"No se pudo obtener job_id o URL de la tarjeta antes del clic: {e}. Se intentará de nuevo después del clic.")

    logging.info(f"Haciendo clic en la tarjeta del trabajo (ID: {job_id if job_id else 'desconocido'}).")
    try:
        # Intenta un clic normal, luego con JS si falla
        try:
            job_card_element.click()
        except StaleElementReferenceException:
            logging.warning("StaleElementReferenceException al intentar clic normal. Intentando clic con JavaScript.")
            wd.execute_script("arguments[0].click();", job_card_element)
        except Exception as e:
            logging.warning(f"Error al intentar clic normal: {e}. Intentando clic con JavaScript.")
            wd.execute_script("arguments[0].click();", job_card_element)
            
        time.sleep(random.uniform(6, 9))

        # Espera a que la sección de detalles del trabajo se cargue en el panel lateral
        WebDriverWait(wd, 45).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__job-details--container h1.t-24.t-bold.inline"))
        )
        logging.info("Detalles del trabajo en el panel lateral cargados exitosamente.")
        time.sleep(random.uniform(3.5, 6))

        # --- VERIFICACIÓN CRÍTICA: Comprueba la URL después de cargar el panel de detalles ---
        # Si la URL ha cambiado a la página de detalles del trabajo, no se ha mantenido en la lista de resultados.
        # Esto indica una redirección completa de la página, lo que no queremos.
        if "/jobs/view/" in wd.current_url and wd.current_url != initial_url_of_list_page:
            logging.error(f"¡ADVERTENCIA CRÍTICA! La URL de la página cambió a la página de detalles del trabajo ({wd.current_url}). "
                          f"Esto significa que no se mantuvo en la página de lista de resultados. Se levantará una excepción para re-evaluar la lista de trabajos.")
            raise PageReloadedException("Página recargada y redirigida a detalles del trabajo.")

    except TimeoutException:
        logging.warning(f"Timeout al esperar que los detalles del trabajo carguen en el panel lateral después del clic para el trabajo con ID: {job_id}. Saltando este trabajo.")
        return None
    except PageReloadedException as e:
        raise e
    except StaleElementReferenceException:
        logging.warning(f"StaleElementReferenceException para ID {job_id}. Se re-obtendrá la lista completa de tarjetas de trabajo y se reanudará desde el siguiente trabajo.")
        return None
    except WebDriverException as e:
        logging.error(f"WebDriverException durante scrape_job_details para ID {job_id}: {e}. La sesión puede haberse perdido.")
        raise e
    except Exception as e:
        logging.warning(f"Error general al intentar hacer clic o cargar detalles del trabajo con ID: {job_id}: {e}. Saltando este trabajo.")
        return None

    if not job_id:
        try:
            current_job_url_after_click = wd.current_url
            match = re.search(r'/jobs/view/(\d+)/', current_job_url_after_click)
            if match:
                job_id = match.group(1)
                logging.info(f"Job ID recuperado de la URL de detalles: {job_id}")
            else:
                logging.warning("No se pudo extraer el Job ID de la URL de detalles.")
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

    job_data = [
        date_time, search_keyword_clean, search_count, job_id, job_title, company,
        location, remote, update_time, applicants, job_pay, job_time, job_position,
        company_size, company_industry, job_details, job_url
    ]

    logging.info(f"Trabajo extraído exitosamente: {job_title} en {company} (ID: {job_id})")
    return job_data

def page_search(wd, search_location, search_keyword, search_remote, search_posted, file, logging):
    url_search = f"https://www.linkedin.com/jobs/search/?f_TPR={search_posted}&f_WRA={search_remote}&geoId=92000000&keywords={search_keyword}&location={search_location}&start=0"
    logging.info(f"Navegando a la URL de búsqueda inicial: {url_search}")
    wd.get(url_search)
    time.sleep(random.uniform(8, 12))

    try:
        # **CAMBIO CLAVE AQUÍ:**
        # Ya no usamos ".jobs-search-results-list" porque su clase padre es dinámica.
        # En su lugar, esperamos directamente por la presencia del primer elemento LI de la tarjeta de trabajo,
        # lo que indica que la lista de resultados se ha cargado.
        WebDriverWait(wd, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.scaffold-layout__list-item[data-occludable-job-id]")))
        logging.info("Lista de resultados de búsqueda inicial encontrada y visible.")
        
        # Simular un ligero scroll inicial o movimiento del ratón para "activar" la página
        wd.execute_script("window.scrollTo(0, 100);")
        time.sleep(random.uniform(1, 2))
        wd.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(1, 2))
        
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            ActionChains(wd).move_by_offset(x, y).perform()
            time.sleep(random.uniform(0.2, 0.5))
            ActionChains(wd).move_by_offset(-x, -y).perform()
            time.sleep(random.uniform(0.2, 0.5))

    except TimeoutException:
        logging.error("¡ERROR CRÍTICO! Timeout esperando la lista de resultados de la búsqueda (primer elemento LI). La página no cargó la lista principal o no es visible.")
        return 0

    search_count = 0
    try:
        search_count_element = wd.find_element(By.CLASS_NAME, "results-context-header__job-count")
        search_count_text = search_count_element.text
        search_count = int("".join(filter(str.isdigit, search_count_text)))
        logging.info(f"Conteo inicial de resultados: {search_count_text}")
    except (NoSuchElementException, ValueError):
        logging.warning("No se pudo obtener el conteo de resultados inicial. Continuando sin él.")

    logging.info(f"Iniciando scraping para '{search_keyword}' en '{search_location}' ({search_count} resultados totales esperados)...")

    scraped_jobs_count = 0
    unique_job_ids = set()
    last_processed_job_id_before_refresh = None
    
    scroll_attempts_without_new_content = 0
    max_scroll_attempts_without_new_content = 25

    while True:
        logging.info(f"Realizando scroll para cargar más trabajos. Total scrapeados hasta ahora: {scraped_jobs_count}.")
        initial_scroll_height = wd.execute_script("return document.body.scrollHeight")
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(7, 10))
        current_scroll_height = wd.execute_script("return document.body.scrollHeight")

        if current_scroll_height == initial_scroll_height:
            scroll_attempts_without_new_content += 1
            logging.info(f"No se cargaron nuevos elementos al hacer scroll. Intento {scroll_attempts_without_new_content}/{max_scroll_attempts_without_new_content}. Altura: {current_scroll_height}")
            if scroll_attempts_without_new_content >= max_scroll_attempts_without_new_content:
                logging.info("Máximo de intentos de scroll sin nuevo contenido alcanzado. Terminando el scraping de esta página.")
                break
        else:
            scroll_attempts_without_new_content = 0

        all_job_cards_on_page = get_all_job_cards_on_page(wd, logging)
        logging.info(f"Total de tarjetas de trabajo válidas visibles en la página después del scroll: {len(all_job_cards_on_page)}")

        current_batch_processed_count = 0
        should_re_evaluate_list = False

        start_index = 0
        if last_processed_job_id_before_refresh:
            found_previous_job_index = -1
            for idx, card in enumerate(all_job_cards_on_page):
                # **CAMBIO CLAVE AQUÍ: Usamos data-occludable-job-id del LI**
                if card.get_attribute("data-occludable-job-id") == last_processed_job_id_before_refresh:
                    found_previous_job_index = idx
                    break
            
            if found_previous_job_index != -1:
                start_index = found_previous_job_index + 1
                logging.info(f"Reanudando el scraping desde el trabajo después de ID: {last_processed_job_id_before_refresh}.")
            else:
                logging.warning(f"No se encontró el trabajo previamente procesado/que causó el refresco (ID: {last_processed_job_id_before_refresh}) en la lista actual. "
                                 "Reiniciando el procesamiento desde el principio de la lista visible.")
            last_processed_job_id_before_refresh = None

        if start_index >= len(all_job_cards_on_page) and len(all_job_cards_on_page) > 0:
            logging.info("Ya se han procesado todos los trabajos visibles en este lote. Realizando scroll adicional o terminando.")
            if current_scroll_height == initial_scroll_height and scroll_attempts_without_new_content >= max_scroll_attempts_without_new_content:
                break
            else:
                continue

        if not all_job_cards_on_page and scroll_attempts_without_new_content >= max_scroll_attempts_without_new_content:
            logging.info("No hay tarjetas de trabajo visibles y el scroll no añadió contenido. Terminando el scraping de esta página.")
            break

        for i in range(start_index, len(all_job_cards_on_page)):
            job_card_element = all_job_cards_on_page[i]
            # **CAMBIO CLAVE AQUÍ: Usamos data-occludable-job-id del LI**
            current_job_id_from_card = job_card_element.get_attribute("data-occludable-job-id")

            if current_job_id_from_card and current_job_id_from_card in unique_job_ids:
                logging.info(f"Trabajo con ID {current_job_id_from_card} ya procesado, saltando.")
                continue

            try:
                logging.info(f"Preparando para scrapear tarjeta de trabajo (ID: {current_job_id_from_card if current_job_id_from_card else 'desconocido'}).")
                job_data = scrape_job_details(wd, job_card_element, search_keyword, search_count, logging)

                if job_data:
                    processed_job_id = job_data[3]
                    if processed_job_id and processed_job_id not in unique_job_ids:
                        scraped_jobs_count += 1
                        unique_job_ids.add(processed_job_id)
                        current_batch_processed_count += 1
                        
                        with open(file, "a", encoding="utf-8", newline='') as f:
                            w = csv.writer(f)
                            w.writerow(job_data)
                    elif not processed_job_id:
                        logging.warning(f"Trabajo procesado sin un ID válido. No se añadió a la lista de únicos.")
                else:
                    logging.info(f"Detalles del trabajo no extraídos o saltados para el trabajo con ID: {current_job_id_from_card if current_job_id_from_card else 'desconocido'}.")

                time.sleep(random.uniform(5, 8))

            except PageReloadedException:
                logging.error(f"¡EXCEPCIÓN CRÍTICA! Se detectó una recarga de página durante el raspado de detalles para ID {current_job_id_from_card}. "
                               f"Se re-obtendrá la lista de tarjetas y se reanudará desde el siguiente trabajo.")
                last_processed_job_id_before_refresh = current_job_id_from_card
                should_re_evaluate_list = True
                break
            except StaleElementReferenceException:
                logging.warning(f"StaleElementReferenceException para ID {current_job_id_from_card}. "
                               f"Se re-obtendrá la lista completa de tarjetas de trabajo y se reanudará desde el siguiente trabajo.")
                last_processed_job_id_before_refresh = current_job_id_from_card # Corregido para que se guarde el ID correcto
                should_re_evaluate_list = True
                break
            except WebDriverException as e:
                logging.error(f"WebDriverException inesperada durante el scraping para ID {current_job_id_from_card}: {e}. "
                               f"Finalizando el scraping para esta palabra clave para reintentar la conexión.")
                raise e
            except Exception as e:
                logging.error(f"Error general procesando tarjeta de trabajo con ID {current_job_id_from_card}: {e}. Continuando con la siguiente.")
                continue

        if should_re_evaluate_list:
            continue

        if current_batch_processed_count == 0 and scroll_attempts_without_new_content >= max_scroll_attempts_without_new_content:
            logging.info("No se procesaron nuevos trabajos en este ciclo y el scroll no añadió contenido significativo después de varios intentos. Terminando.")
            break

    logging.info(f"Scraping completado para '{search_keyword}'. Total de trabajos extraídos: {scraped_jobs_count}.")
    return scraped_jobs_count

# SCRIPT PRINCIPAL
if __name__ == "__main__":
    logging = create_logfile()
    date = datetime.date.today().strftime('%d-%b-%y')
    file = f"output/{date}_linkedin_jobs.csv"

    search_params = [
        {"location": "Spain", "keyword": "Data%20Scientist", "remote": "true", "posted": "r86400"},
        {"location": "Spain", "keyword": "Data%20Engineer", "remote": "true", "posted": "r86400"},
        {"location": "Spain", "keyword": "Python%20Developer", "remote": "true", "posted": "r86400"},
        {"location": "Spain", "keyword": "Scrum%20Master", "remote": "true", "posted": "r86400"},
        {"location": "Spain", "keyword": "Product%20Manager", "remote": "true", "posted": "r86400"},
        {"location": "Rubio", "keyword": "Ingeniero%20de%20Sistemas", "remote": "false", "posted": "r2592000"},
        {"location": "Caracas", "keyword": "Desarrollador%20Web", "remote": "true", "posted": "r604800"},
        {"location": "Bogota", "keyword": "Analista%20de%20datos", "remote": "false", "posted": "r604800"},
    ]

    wd = None
    try:
        create_file(file, logging)
        wd = login(logging)

        for params in search_params:
            location = params["location"]
            keyword = params["keyword"]
            remote_status = params["remote"]
            posted_time = params["posted"]

            logging.info(f"Iniciando búsqueda para: Keyword='{keyword}', Ubicación='{location}', Remoto='{remote_status}', Publicado='{posted_time}'")
            try:
                page_search(wd, location, keyword, remote_status, posted_time, file, logging)
            except WebDriverException as e:
                logging.error(f"WebDriverException capturada durante la búsqueda de '{keyword}': {e}. Re-conectando el navegador.")
                if wd:
                    try:
                        wd.quit()
                    except:
                        pass
                wd = login(logging)
            except Exception as e:
                logging.error(f"Error inesperado durante la búsqueda de '{keyword}': {e}")

    except Exception as main_e:
        logging.critical(f"Error crítico en el script principal: {main_e}")
    finally:
        if wd:
            logging.info("Cerrando el navegador.")
            wd.quit()
        logging.info("Proceso completado.")