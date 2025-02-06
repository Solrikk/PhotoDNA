import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.action_chains import ActionChains

def setup_browser():
    o = EdgeOptions()
    o.add_argument('--start-maximized')
    o.add_argument('--no-sandbox')
    o.add_argument('--disable-dev-shm-usage')
    o.add_argument('--disable-blink-features=AutomationControlled')
    o.add_experimental_option('excludeSwitches', ['enable-automation'])
    o.add_experimental_option('useAutomationExtension', False)
    o.add_argument('--disable-gpu')
    o.add_argument('--disable-software-rasterizer')
    try:
        d = EdgeChromiumDriverManager()
        p = d.install()
        s = EdgeService(p)
        b = webdriver.Edge(service=s, options=o)
        logging.info(p)
    except Exception as e:
        logging.error(str(e))
        raise e
    b.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return b

def click_element_js(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        ActionChains(driver).move_to_element(element).perform()
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        logging.warning(str(e))
