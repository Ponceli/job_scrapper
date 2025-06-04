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

def page_search(wd, search_location, search_keyword, search_remote, search_posted, search_page, search_count, file, logging):
    click_wait = 4
    url_search = f"https://www.linkedin.com/jobs/search/?f_TPR={search_posted}&f_WRA={search_remote}&geoId=92000000&keywords={search_keyword}&location={search_location}&start={search_page}"
    wd.get(url_search)

    try:
        WebDriverWait(wd, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list")))
    except TimeoutException:
        logging.warning("Timeout esperando los resultados.")
        return search_page + 25, search_count, url_search

    try:
        search_count_text = wd.find_element(By.CLASS_NAME, "results-context-header__job-count").text
        search_count = int(search_count_text.replace(',', '').strip())
    except:
        logging.warning("No se pudo obtener el conteo de resultados.")
        return search_page + 25, search_count, url_search

    logging.info(f"Cargando página {round(search_page/25) + 1} de {round(search_count/25)} para {search_keyword} ({search_count} resultados)...")

    jobs = wd.find_elements(By.CSS_SELECTOR, "li[data-occludable-entity-urn]")
    list_jobs = []

    for index, job in enumerate(jobs):
        try:
            wd.execute_script("arguments[0].scrollIntoView();", job)
            ActionChains(wd).move_to_element(job).click().perform()
            WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-description__content")))
            time.sleep(click_wait)
        except Exception as e:
            logging.warning(f"No se pudo abrir la publicación {index + 1}: {e}")
            continue

        try:
            job_id = wd.current_url.split("/view/")[1].split("/")[0]
        except:
            job_id = ''

        try:
            job_title = wd.find_element(By.CSS_SELECTOR, "h2.jobs-unified-top-card__job-title").text
        except:
            job_title = ''

        try:
            primary_info = wd.find_elements(By.CSS_SELECTOR, ".jobs-unified-top-card__primary-description span")
            company = primary_info[0].text if len(primary_info) > 0 else ''
            location = primary_info[1].text if len(primary_info) > 1 else ''
            remote = primary_info[2].text if len(primary_info) > 2 else ''
        except:
            company = location = remote = ''

        try:
            insights = wd.find_elements(By.CSS_SELECTOR, ".jobs-unified-top-card__job-insight span")
            update_time = insights[0].text if len(insights) > 0 else ''
            applicants = insights[1].text.split(' ')[0] if len(insights) > 1 else ''
        except:
            update_time = applicants = ''

        job_time = job_position = job_pay = ''
        try:
            job_info_text = wd.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__job-insight-text-container").text
            job_info = job_info_text.split(' · ')
            if len(job_info) == 1:
                job_time = job_info[0]
            elif "$" in job_info[0]:
                job_pay, job_time = job_info[0], job_info[1]
                job_position = job_info[2] if len(job_info) > 2 else ''
            else:
                job_time = job_info[0]
                job_position = job_info[1] if len(job_info) > 1 else ''
        except:
            pass

        try:
            company_info = wd.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__company-info").text.split(' · ')
            company_size = company_info[0] if len(company_info) > 0 else ''
            company_industry = company_info[1] if len(company_info) > 1 else ''
        except:
            company_size = company_industry = ''

        try:
            job_details = wd.find_element(By.CSS_SELECTOR, "div.jobs-description__content div.jobs-box__html-content").text.replace("\n", " ")
        except:
            job_details = ''

        date_time = datetime.datetime.now().strftime("%d%b%Y-%H:%M:%S")
        search_keyword_clean = search_keyword.replace("%20", " ")
        list_job = [date_time, search_keyword_clean, search_count, job_id, job_title, company,
                    location, remote, update_time, applicants, job_pay, job_time, job_position,
                    company_size, company_industry, job_details]
        list_jobs.append(list_job)

    with open(file, "a", encoding="utf-8", newline='') as f:
        w = csv.writer(f)
        w.writerows(list_jobs)

    logging.info(f"Página {round(search_page/25) + 1} cargada.")
    return search_page + 25, search_count, url_search

# MAIN SCRIPT
logging = create_logfile()
date = datetime.date.today().strftime('%d-%b-%y')
file = f"output/{date}.csv"
create_file(file, logging)
wd = login(logging)

search_keywords = ['Data Analyst', 'Data Scientist', 'Data Engineer']
search_location = "Worldwide"
search_remote = "true"
search_posted = "r86400"

for search_keyword in search_keywords:
    search_keyword = search_keyword.lower().replace(" ", "%20")
    search_page = 0
    search_count = 1
    max_pages = 10
    while search_page < search_count and search_page < max_pages * 25:
        try:
            search_page, search_count, url_search = page_search(wd, search_location, search_keyword, search_remote, search_posted, search_page, search_count, file, logging)
        except Exception as e:
            logging.error(f"Error en {search_keyword} - {e}")
            search_page += 25

wd.quit()
