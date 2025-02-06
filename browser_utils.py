# browser_utils.py
import os
import socket
import logging
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def setup_browser():
    options = EdgeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    
    try:
        driver_manager = EdgeChromiumDriverManager()
        driver_path = driver_manager.install()
        service = EdgeService(driver_path)
        driver = webdriver.Edge(service=service, options=options)
        logging.info(f"Edge драйвер успешно установлен: {driver_path}")
    except Exception as e:
        logging.error(f"Ошибка при инициализации драйвера: {str(e)}")
        raise e

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def click_element_js(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        ActionChains(driver).move_to_element(element).perform()
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        logging.warning(f"Ошибка при клике на элемент: {str(e)}")

def get_ip_address(url):
    import requests
    try:
        hostname = requests.utils.urlparse(url).hostname
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return None
