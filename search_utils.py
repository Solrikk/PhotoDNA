
import os
import time
import logging
import requests
from PIL import Image
from io import BytesIO
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from browser_utils import click_element_js, get_ip_address

WAIT_TIME = 5
SIMILARITY_THRESHOLD = 0.89
MAX_ADDITIONAL_SEARCHES_PER_IMAGE = 1
MAX_TOTAL_RECORDS = 2000

def perform_additional_search(driver, query, matcher, data_list,
                          record_counter, processed_ips, source_embedding):
    if not query:
        logging.warning("Пустой запрос. Пропуск дополнительного поиска.")
        return
    if len(query) > 100:
        logging.warning(f"Запрос слишком длинный: {query[:100]}... Пропуск.")
        return
    try:
        driver.get('https://yandex.ru/')
        wait = WebDriverWait(driver, WAIT_TIME)
        search_input = wait.until(
            EC.presence_of_element_located((By.NAME, "text")))
        search_input.clear()
        search_input.send_keys(query)
        search_input.submit()
        logging.info(f"Выполнен дополнительный поиск по запросу: {query}")
        driver.save_screenshot(f'yandex_additional_search_{query[:50]}.png')
        time.sleep(2)
        items = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "li.serp-item")))
        logging.info(
            f"Найдено {len(items)} результатов для дополнительного поиска по запросу: {query}"
        )
        for item in items:
            try:
                link_element = item.find_element(By.CSS_SELECTOR, 'a.Link')
                site_link = link_element.get_attribute('href')
                if site_link:
                    ip_address = get_ip_address(site_link)
                    if ip_address and ip_address not in processed_ips:
                        processed_ips.add(ip_address)
                        response = requests.get(site_link, timeout=5)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        img_tag = soup.find('img')
                        if img_tag and img_tag.get('src'):
                            img_url = requests.compat.urljoin(
                                site_link, img_tag.get('src'))
                            comparison_embedding = matcher.download_and_process_image(
                                img_url)
                            if comparison_embedding is not None:
                                similarity = matcher.compare_images(
                                    source_embedding, comparison_embedding)
                                if similarity > SIMILARITY_THRESHOLD:
                                    row_data = {
                                        'Запрос': query,
                                        'URL сайта': site_link,
                                        'IP адрес': ip_address,
                                        'Схожесть': f"{similarity:.4f}",
                                        'URL исходного фото': '',
                                        'URL найденного фото': img_url
                                    }
                                    data_list.append(row_data)
                                    record_counter[0] += 1
                                    logging.info(
                                        f"Добавлены данные из дополнительного поиска: {site_link} (Схожесть: {similarity:.4f})"
                                    )
                                    if record_counter[0] >= MAX_TOTAL_RECORDS:
                                        return
            except Exception as e:
                logging.warning(
                    f"Ошибка при обработке дополнительного результата: {str(e)}"
                )
                continue
    except Exception as e:
        logging.error(
            f"Ошибка при выполнении дополнительного поиска для запроса '{query}': {str(e)}"
        )


def collect_similar_images(driver, wait, matcher, source_embedding, image_name,
                       data_list, record_counter, original_photo_url):
    try:
        try:
            time.sleep(1)
            more_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "CbirSites-MoreButton")))
            click_element_js(driver, more_button)
            logging.info("Нажата кнопка 'Показать все' на Яндексе.")
            driver.save_screenshot('yandex_step_clicked_more.png')
            time.sleep(1)
        except Exception as e:
            logging.error(f"Не удалось нажать кнопку 'Показать все': {str(e)}")
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        scroll_attempt = 0
        max_scroll_attempts = 5
        while scroll_attempt < max_scroll_attempts:
            current_height = driver.execute_script(
                "return window.pageYOffset;")
            scroll_height = driver.execute_script(
                "return document.body.scrollHeight;")
            step = (scroll_height - current_height) / 2
            for i in range(2):
                driver.execute_script(
                    f"window.scrollTo(0, {current_height + step * (i+1)});")
                time.sleep(0.2)
            logging.info(f"Прокрутка вниз... Попытка {scroll_attempt + 1}")
            time.sleep(1)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempt += 1
                logging.info("Новый контент не загружен.")
            else:
                last_height = new_height
                scroll_attempt = 0
        logging.info("Прокрутка завершена.")
        items = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "li.CbirSites-Item")))
        logging.info(
            f"Найдено {len(items)} элементов с классом 'CbirSites-Item'")
        processed_ips = set()
        for idx, item in enumerate(items):
            try:
                img_element = item.find_element(By.TAG_NAME, 'img')
                thumbnail_url = img_element.get_attribute('src')
                site_link_element = item.find_element(
                    By.CSS_SELECTOR, 'a.Link_view_outer.CbirSites-ItemDomain')
                site_link = site_link_element.get_attribute('href')
                logging.info(f"Обработка элемента {idx + 1}/{len(items)}")
                logging.info(f"URL миниатюры: {thumbnail_url}")
                logging.info(f"URL сайта: {site_link}")
                similarity = 0.0
                row_data = {
                    'Источник': 'Яндекс',
                    'Название изображения': image_name,
                    'URL миниатюры': thumbnail_url,
                    'URL сайта': site_link,
                    'Схожесть': '',
                    'URL исходного фото': original_photo_url,
                    'URL найденного фото': ''
                }
                if thumbnail_url and site_link:
                    comparison_embedding = matcher.download_and_process_image(
                        thumbnail_url)
                    if comparison_embedding is not None:
                        similarity = matcher.compare_images(
                            source_embedding, comparison_embedding)
                        row_data['Схожесть'] = f"{similarity:.4f}"
                        logging.info(f"Оценка схожости: {similarity}")
                if similarity > SIMILARITY_THRESHOLD:
                    try:
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(site_link)
                        wait_short = WebDriverWait(driver, WAIT_TIME)
                        wait_short.until(
                            EC.presence_of_element_located(
                                (By.TAG_NAME, 'body')))
                        time.sleep(5)
                        page_content = driver.page_source
                        soup = BeautifulSoup(page_content, 'html.parser')
                        publication_date = matcher.extract_publication_date(
                            soup)
                        row_data[
                            'Дата публикации'] = publication_date if publication_date else ''
                        post_text = ''
                        forward_from = ''
                        post_body = soup.find('div', class_='post-body')
                        if post_body:
                            post_text_element = post_body.find(
                                'div', class_='post-text')
                            if post_text_element:
                                post_text = post_text_element.get_text(
                                    separator=' ', strip=True)
                            forward_info = post_body.find('div',
                                                      class_='post-from')
                            if forward_info:
                                forward_from = forward_info.get_text(
                                    strip=True).replace('Forward from: ', '')
                        row_data['Текст поста'] = post_text
                        row_data['Переслано от'] = forward_from
                        title = matcher.generate_title(post_text)
                        row_data['Заголовок'] = title if title else ''
                        ip_address = get_ip_address(site_link)
                        row_data['IP адрес'] = ip_address if ip_address else ''
                        row_data['URL найденного фото'] = thumbnail_url
                        data_list.append(row_data)
                        record_counter[0] += 1
                        logging.info(
                            f"Добавлены данные для: {image_name} (Всего записей: {record_counter[0]})"
                        )
                        search_queries = []
                        if title:
                            search_queries.append(f'"{title}"')
                        if post_text:
                            search_queries.append(post_text)
                        if forward_from:
                            search_queries.append(forward_from)
                        additional_searches_done = 0
                        for query in search_queries:
                            if record_counter[0] >= MAX_TOTAL_RECORDS:
                                break
                            if additional_searches_done >= MAX_ADDITIONAL_SEARCHES_PER_IMAGE:
                                break
                            perform_additional_search(driver, query, matcher,
                                                  data_list,
                                                  record_counter,
                                                  processed_ips,
                                                  source_embedding)
                            additional_searches_done += 1
                        if record_counter[0] >= MAX_TOTAL_RECORDS:
                            logging.info(
                                f"Достигнуто максимальное количество записей: {MAX_TOTAL_RECORDS}"
                            )
                            break
                    except Exception as e:
                        logging.error(
                            f"Ошибка при обработке ссылки с высокой схожестью {site_link}: {str(e)}"
                        )
                    finally:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                logging.error(
                    f"Ошибка при обработке элемента {idx + 1}: {str(e)}")
                continue
    except Exception as e:
        logging.error(f"Ошибка при сборе изображений: {str(e)}")


def search_yandex_image(driver, image_path, matcher, source_embedding,
                     image_name, data_list, record_counter,
                     original_photo_url):
    try:
        driver.get('https://yandex.ru/images/')
        logging.info("Переход на Яндекс Картинки.")
        driver.save_screenshot('yandex_step_navigate.png')
        wait = WebDriverWait(driver, WAIT_TIME)
        try:
            consent_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Согласен')]")))
            consent_button.click()
            logging.info("Закрыто окно согласия на Яндексе.")
            driver.save_screenshot('yandex_step_closed_consent.png')
        except:
            logging.info("Окно согласия на Яндексе не найдено.")
            driver.save_screenshot('yandex_step_no_consent.png')
        try:
            upload_input = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@type='file']")))
            upload_input.send_keys(os.path.abspath(image_path))
            logging.info(f"Изображение загружено на Яндекс: {image_path}")
            driver.save_screenshot('yandex_step_uploaded_image.png')
        except Exception as e:
            logging.error(
                "Не удалось найти или взаимодействовать с полем загрузки на Яндексе."
            )
            driver.save_screenshot('yandex_step_upload_error.png')
            raise e
        time.sleep(2)
        try:
            popup_close = wait.until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "NeuroOnboarding-Close")))
            popup_close.click()
            logging.info("Закрыто всплывающее окно на Яндексе.")
            driver.save_screenshot('yandex_step_closed_popup.png')
        except:
            logging.info(
                "Всплывающее окно на Яндексе не найдено или уже закрыто.")
            driver.save_screenshot('yandex_step_no_popup.png')
        collect_similar_images(driver, wait, matcher, source_embedding,
                           image_name, data_list, record_counter,
                           original_photo_url)
    except Exception as e:
        logging.error(f"Ошибка при поиске на Яндексе: {str(e)}")
        driver.save_screenshot('yandex_step_search_error.png')
