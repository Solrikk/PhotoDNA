import logging
import time
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constants import WAIT_TIME, SIMILARITY_THRESHOLD, MAX_TOTAL_RECORDS, MAX_ADDITIONAL_SEARCHES_PER_IMAGE
from browser_utils import click_element_js
from utils import get_ip_address
from selenium.common.exceptions import TimeoutException

def perform_additional_search(driver, query, matcher, data_list, record_counter, processed_ips, source_embedding):
    if not query:
        return
    if len(query) > 100:
        return
    try:
        driver.get('https://yandex.ru/')
        w = WebDriverWait(driver, WAIT_TIME)
        i = w.until(EC.presence_of_element_located((By.NAME, "text")))
        i.clear()
        i.send_keys(query)
        i.submit()
        logging.info(query)
        time.sleep(2)
        items = w.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.serp-item")))
        for it in items:
            try:
                l = it.find_element(By.CSS_SELECTOR, 'a.Link').get_attribute('href')
                if l:
                    ip = get_ip_address(l)
                    if ip and ip not in processed_ips:
                        processed_ips.add(ip)
                        r = requests.get(l, timeout=10)
                        s = BeautifulSoup(r.content, 'html.parser')
                        img_tag = s.find('img')
                        if img_tag and img_tag.get('src'):
                            img_url = requests.compat.urljoin(l, img_tag.get('src'))
                            c = matcher.download_and_process_image(img_url)
                            if c is not None:
                                sim = matcher.compare_images(source_embedding, c)
                                if sim > SIMILARITY_THRESHOLD:
                                    data_list.append({
                                        'Запрос': query,
                                        'URL сайта': l,
                                        'IP адрес': ip,
                                        'Схожесть': f"{sim:.4f}",
                                        'URL исходного фото': '',
                                        'URL найденного фото': img_url
                                    })
                                    record_counter[0] += 1
                                    if record_counter[0] >= MAX_TOTAL_RECORDS:
                                        return
            except Exception as e:
                logging.warning(str(e))
    except Exception as e:
        logging.error(str(e))

def collect_similar_images(driver, w, matcher, source_embedding, image_name, data_list, record_counter, original_photo_url):
    try:
        time.sleep(5)
        try:
            mb = w.until(EC.element_to_be_clickable((By.CLASS_NAME, "CbirSites-MoreButton")))
            click_element_js(driver, mb)
            time.sleep(5)
        except TimeoutException:
            pass
        lh = driver.execute_script("return document.body.scrollHeight")
        sa = 0
        ms = 15
        while sa < ms:
            ch = driver.execute_script("return window.pageYOffset;")
            sh = driver.execute_script("return document.body.scrollHeight;")
            st = (sh - ch) / 4
            for i in range(4):
                driver.execute_script(f"window.scrollTo(0, {ch + st * (i+1)});")
                time.sleep(1)
            time.sleep(3)
            nh = driver.execute_script("return document.body.scrollHeight")
            if nh == lh:
                sa += 1
            else:
                lh = nh
                sa = 0
        items = w.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.CbirSites-Item")))
        pi = set()
        for idx, it in enumerate(items):
            try:
                ie = it.find_element(By.TAG_NAME, 'img')
                tu = ie.get_attribute('src')
                sl = it.find_element(By.CSS_SELECTOR, 'a.Link_view_outer.CbirSites-ItemDomain').get_attribute('href')
                s = 0.0
                row = {
                    'Источник': 'Яндекс',
                    'Название изображения': image_name,
                    'URL миниатюры': tu,
                    'URL сайта': sl,
                    'Схожесть': '',
                    'URL исходного фото': original_photo_url,
                    'URL найденного фото': ''
                }
                if tu and sl:
                    c = matcher.download_and_process_image(tu)
                    if c is not None:
                        s = matcher.compare_images(source_embedding, c)
                        row['Схожесть'] = f"{s:.4f}"
                if s > SIMILARITY_THRESHOLD:
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(sl)
                    ws = WebDriverWait(driver, WAIT_TIME)
                    ws.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    time.sleep(5)
                    pc = driver.page_source
                    sp = BeautifulSoup(pc, 'html.parser')
                    pd = matcher.extract_publication_date(sp)
                    if pd:
                        row['Дата публикации'] = pd
                    else:
                        row['Дата публикации'] = ''
                    pt = ''
                    fr = ''
                    pb = sp.find('div', class_='post-body')
                    if pb:
                        pte = pb.find('div', class_='post-text')
                        if pte:
                            pt = pte.get_text(separator=' ', strip=True)
                        fi = pb.find('div', class_='post-from')
                        if fi:
                            fr = fi.get_text(strip=True).replace('Forward from: ', '')
                    row['Текст поста'] = pt
                    row['Переслано от'] = fr
                    tt = matcher.generate_title(pt)
                    if tt:
                        row['Заголовок'] = tt
                    else:
                        row['Заголовок'] = ''
                    ip = get_ip_address(sl)
                    if ip:
                        row['IP адрес'] = ip
                    else:
                        row['IP адрес'] = ''
                    row['URL найденного фото'] = tu
                    data_list.append(row)
                    record_counter[0] += 1
                    sq = []
                    if tt:
                        sq.append(f'"{tt}"')
                    if pt:
                        sq.append(pt)
                    if fr:
                        sq.append(fr)
                    ad = 0
                    for q in sq:
                        if record_counter[0] >= MAX_TOTAL_RECORDS:
                            break
                        if ad >= MAX_ADDITIONAL_SEARCHES_PER_IMAGE:
                            break
                        perform_additional_search(driver, q, matcher, data_list, record_counter, pi, source_embedding)
                        ad += 1
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    if record_counter[0] >= MAX_TOTAL_RECORDS:
                        break
            except Exception as e:
                logging.error(str(e))
                continue
    except Exception as e:
        logging.error(str(e))

def search_yandex_image(driver, image_path, matcher, source_embedding, image_name, data_list, record_counter, original_photo_url):
    from selenium.common.exceptions import TimeoutException
    driver.get('https://yandex.ru/images/')
    w = WebDriverWait(driver, WAIT_TIME)
    try:
        b = w.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Согласен')]")))
        b.click()
    except TimeoutException:
        pass
    try:
        inp = w.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
        from os.path import abspath
        inp.send_keys(abspath(image_path))
    except Exception as e:
        logging.error(str(e))
        return
    time.sleep(2)
    try:
        pc = w.until(EC.element_to_be_clickable((By.CLASS_NAME, "NeuroOnboarding-Close")))
        pc.click()
    except:
        pass
    collect_similar_images(driver, w, matcher, source_embedding, image_name, data_list, record_counter, original_photo_url)
