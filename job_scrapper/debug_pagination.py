import os
import time
import random
from dotenv import load_dotenv
import logging
import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException

load_dotenv()

def create_logfile():
    date_time = datetime.datetime.today().strftime('%d-%b-%y_%H-%M-%S')
    log_directory = 'log'
    os.makedirs(log_directory, exist_ok=True)
    logfile = os.path.join(log_directory, f'debug_pagination_YOUR_SELECTORS_R4_{date_time}.log')
    logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', force=True)
    logging.info(f'Log file {logfile} created for pagination debugging (Using your selectors R4).')
    return logging

def login(logging):
    url_login = "https://www.linkedin.com/login"
    LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME", "")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
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
    
    logging.info(f"LOGUEANDOME A LINKEDIN COMO {LINKEDIN_USERNAME}...")
    wd.get(url_login)
    time.sleep(random.uniform(7, 12))

    try:
        WebDriverWait(wd, 40).until(EC.presence_of_element_located((By.ID, "username")))
        wd.find_element(By.ID, "username").send_keys(LINKEDIN_USERNAME)
        wd.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        
        time.sleep(random.uniform(1.5, 1.5))
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

def simple_pagination_test(wd, logging, search_keyword, search_location):
    MAX_PAGES_TO_ATTEMPT = 5 
    current_page_number = 1

    url_search = f"https://www.linkedin.com/jobs/search/?keywords={search_keyword}&location={search_location}&start=0" 
    logging.info(f"Navegando a la URL de búsqueda inicial para depuración: {url_search}")
    wd.get(url_search)
    time.sleep(random.uniform(10, 15))

    logging.info(f"URL actual después de la navegación: {wd.current_url}")

    try:
        WebDriverWait(wd, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.scaffold-layout__list-item[data-occludable-job-id]")))
        logging.info("Primeras tarjetas de resultados de búsqueda encontradas y visibles. ¡Página de resultados lista!")
        
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
        time.sleep(random.uniform(1, 2))
        wd.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(1, 2))

    except TimeoutException:
        logging.error("¡ERROR CRÍTICO! Timeout esperando las tarjetas de resultados de la búsqueda. La página no cargó los resultados principales. Esto debe resolverse antes de continuar.")
        wd.save_screenshot(f"debug_screenshot_pagination_initial_fail_{search_keyword}.png")
        return

    # Loop para intentar avanzar de página
    while current_page_number < MAX_PAGES_TO_ATTEMPT:
        logging.info(f"--- Intentando pasar a la página {current_page_number + 1} ---")
        
        initial_url_before_click = wd.current_url
        
        try:
            # === MODIFICACIÓN CLAVE AQUÍ: Usando los selectores que proporcionaste ===
            # Intentar encontrar el botón de la siguiente página usando tus selectores más específicos
            # Li:nth-child(current_page_number + 1) para el selector CSS
            # li[current_page_number + 1] para el XPath

            next_page_button_xpath = f'//*[@id="jobs-search-results-footer"]/div[2]/ul/li[{current_page_number + 1}]/button'
            next_page_button_css = f'#jobs-search-results-footer > div.jobs-search-pagination.jobs-search-results-list__pagination.p4 > ul > li:nth-child({current_page_number + 1}) > button'
            
            next_page_button = None
            try:
                # Intento primero con el XPath que me proporcionaste
                next_page_button = WebDriverWait(wd, 15).until(
                    EC.element_to_be_clickable((By.XPATH, next_page_button_xpath))
                )
                logging.info(f"Botón de la página {current_page_number + 1} encontrado usando tu XPath.")
            except TimeoutException:
                logging.info(f"Tu XPath para la página {current_page_number + 1} no funcionó, intentando con tu Selector CSS.")
                try:
                    # Si no funciona, intento con el Selector CSS
                    next_page_button = WebDriverWait(wd, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, next_page_button_css))
                    )
                    logging.info(f"Botón de la página {current_page_number + 1} encontrado usando tu Selector CSS.")
                except TimeoutException:
                    logging.info(f"Tu Selector CSS para la página {current_page_number + 1} tampoco funcionó. Revertiendo a los selectores generales (aria-label/text).")
                    # Si ninguno de tus selectores funciona, intentamos con los generales (como fallback)
                    general_next_page_button_xpath = (
                        f"//button[@aria-label='Página {current_page_number + 1}'] | "
                        f"//button[contains(@class, 'artdeco-pagination__button')]//span[text()='{current_page_number + 1}'] | "
                        f"//a[contains(@class, 'artdeco-pagination__button')]//span[text()='{current_page_number + 1}']"
                    )
                    next_page_button = WebDriverWait(wd, 15).until(
                        EC.element_to_be_clickable((By.XPATH, general_next_page_button_xpath))
                    )
                    logging.info(f"Botón de la página {current_page_number + 1} encontrado usando selectores generales.")


            # Si encontramos el botón
            if next_page_button:
                wd.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
                time.sleep(random.uniform(1.0, 2.0))
                wd.execute_script("arguments[0].click();", next_page_button)
                logging.info(f"Clic en el botón de la página {current_page_number + 1} exitoso.")

                wait_success = False
                try:
                    # Esperar a que la URL cambie O el número de página activa se actualice
                    WebDriverWait(wd, 20).until(
                        lambda driver: driver.current_url != initial_url_before_click or \
                                       EC.presence_of_element_located((By.XPATH, f"//button[contains(@class, 'artdeco-pagination__button--active')]//span[text()='{current_page_number + 1}']"))(driver)
                    )
                    wait_success = True
                except TimeoutException:
                    logging.warning(f"Timeout: El clic en la página {current_page_number + 1} no resultó en un cambio de URL o activación en 20 segundos.")
                    
                if wait_success:
                    logging.info(f"VERIFICACIÓN: La página {current_page_number + 1} se cargó o se activó correctamente.")
                    current_page_number += 1
                    time.sleep(random.uniform(5, 8)) 

                    try:
                        WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.scaffold-layout__list-item[data-occludable-job-id]")))
                        logging.info(f"VERIFICACIÓN: Se detectaron elementos de trabajos en la página {current_page_number}. Paginación visualmente exitosa.")
                    except TimeoutException:
                        logging.info(f"No se encontraron tarjetas de trabajo en la página {current_page_number} después de navegar o de la carga. Posiblemente última página o un problema de renderizado.")
                        break # Si no hay tarjetas, asumimos el fin de los resultados.
                else:
                    logging.error(f"FALLO DE PAGINACIÓN: El clic en la página {current_page_number + 1} no fue efectivo. No se detectó cambio de URL o activación del botón.")
                    wd.save_screenshot(f"debug_pagination_failed_page_no_change_{current_page_number + 1}.png")
                    break # Si el clic no produce un cambio, no tiene sentido continuar.
            else:
                logging.error(f"FALLO DE PAGINACIÓN CRÍTICO: No se pudo encontrar el botón de la página {current_page_number + 1} con ningún selector. Terminando.")
                break


        except TimeoutException:
            logging.info(f"No se encontró el botón de la página {current_page_number + 1} en el tiempo esperado (Timeout). Posiblemente hemos llegado a la última página de resultados o los selectores no son correctos para las páginas siguientes.")
            break
        except NoSuchElementException:
            logging.info(f"No se encontró el botón de la página {current_page_number + 1} (NoSuchElementException). Posiblemente hemos llegado a la última página de resultados.")
            break
        except Exception as e:
            logging.error(f"Error inesperado durante la navegación a la página {current_page_number + 1}: {e}.")
            wd.save_screenshot(f"debug_pagination_error_general_page_{current_page_number + 1}.png")
            break

    logging.info(f"Depuración de paginación completada. Última página intentada con éxito: {current_page_number}.")


# SCRIPT PRINCIPAL PARA DEPURACIÓN
if __name__ == "__main__":
    logging = create_logfile()

    wd = None
    try:
        wd = login(logging)
        # Puedes cambiar estos parámetros para probar diferentes búsquedas
        simple_pagination_test(wd, logging, search_keyword="Python%20Developer", search_location="Spain")

    except Exception as main_e:
        logging.critical(f"Error crítico en el script principal de depuración: {main_e}")
    finally:
        if wd:
            logging.info("Cerrando el navegador después de la depuración de paginación.")
            wd.quit()
        logging.info("Proceso de depuración de paginación completado.")