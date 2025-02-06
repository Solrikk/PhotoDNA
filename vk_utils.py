import logging
import time
import requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constants import WAIT_TIME

def extract_vk_album_photos(driver, url):
    driver.get(url)
    logging.info(url)
    w = WebDriverWait(driver, WAIT_TIME)
    w.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/photo-']")))
    time.sleep(5)
    h = driver.execute_script("return document.body.scrollHeight")
    sa = 0
    ms = 50
    while sa < ms:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        nh = driver.execute_script("return document.body.scrollHeight")
        if nh == h:
            sa += 1
        else:
            h = nh
            sa = 0
    s = driver.page_source
    soup = BeautifulSoup(s, 'html.parser')
    l = soup.find_all('a', href=lambda x: x and x.startswith('/photo-'))
    r = ["https://vk.com" + i['href'] for i in l]
    r = list(dict.fromkeys(r))
    logging.info(len(r))
    return r

def extract_vk_photo_url(driver, url):
    driver.get(url)
    logging.info(url)
    w = WebDriverWait(driver, WAIT_TIME)
    w.until(EC.presence_of_element_located((By.ID, "pv_photo")))
    time.sleep(5)
    s = driver.page_source
    soup = BeautifulSoup(s, 'html.parser')
    d = soup.find('div', id='pv_photo')
    if d:
        img_tag = d.find('img')
        if img_tag and img_tag.get('src'):
            u = img_tag['src']
            logging.info(u)
            return u
    return None
