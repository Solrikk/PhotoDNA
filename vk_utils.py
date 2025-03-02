
import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def vk_login(driver):
    try:
        vk_login = os.getenv('VK_LOGIN')
        vk_password = os.getenv('VK_PASSWORD')

        if not vk_login or not vk_password:
            raise Exception("VK_LOGIN или VK_PASSWORD не найдены в переменных окружения")

        wait = WebDriverWait(driver, 5)
        other_login_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Войти другим способом')]")))
        other_login_btn.click()

        phone_input = wait.until(
            EC.presence_of_element_located((By.NAME, "login")))
        phone_input.clear()
        phone_input.send_keys(vk_login)

        password_input = wait.until(
            EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(vk_password)
        password_input.submit()

        time.sleep(2)

    except Exception as e:
        logging.error(f"Ошибка при авторизации ВКонтакте: {str(e)}")
        raise


def extract_vk_album_photos(driver, album_url):
    try:
        driver.get(album_url)
        logging.info(f"Переход на страницу альбома ВКонтакте: {album_url}")
        try:
            login_button = driver.find_element(
                By.XPATH, "//button[contains(., 'Войти другим способом')]")
            if login_button:
                logging.info("Требуется авторизация ВКонтакте")
                vk_login(driver)
                driver.get(album_url)
        except:
            logging.info("Авторизация не требуется")

        wait = WebDriverWait(driver, 5)
        time.sleep(2)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/photo-']")))
        time.sleep(5)
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        scroll_attempt = 0
        max_scroll_attempts = 3
        while scroll_attempt < max_scroll_attempts:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempt += 1
                logging.info(
                    f"Попытка прокрутки {scroll_attempt}/{max_scroll_attempts} не удалась. Новый контент не найден."
                )
            else:
                last_height = new_height
                scroll_attempt = 0
                logging.info(
                    f"Успешная прокрутка. Текущая высота: {new_height}")
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        photo_links = soup.find_all(
            'a', href=lambda href: href and href.startswith('/photo-'))
        photo_urls = ["https://vk.com" + link['href'] for link in photo_links]
        photo_urls = list(dict.fromkeys(photo_urls))
        logging.info(f"Найдено {len(photo_urls)} фотографий в альбоме.")
        return photo_urls
    except Exception as e:
        logging.error(
            f"Ошибка при извлечении фото из альбома ВКонтакте: {str(e)}")
        return []


def extract_vk_photo_url(driver, photo_url):
    try:
        driver.get(photo_url)
        logging.info(f"Переход на страницу фотографии ВКонтакте: {photo_url}")
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.ID, "pv_photo")))
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        pv_photo_div = soup.find('div', id='pv_photo')
        if pv_photo_div:
            img_tag = pv_photo_div.find('img')
            if img_tag and img_tag.get('src'):
                img_url = img_tag['src']
                logging.info(f"Найден URL фотографии: {img_url}")
                return img_url
        logging.warning("Не удалось найти URL фотографии на странице.")
        return None
    except Exception as e:
        logging.error(
            f"Ошибка при извлечении URL фотографии ВКонтакте: {str(e)}")
        return None
