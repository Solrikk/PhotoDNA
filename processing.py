import os
import logging
import time
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from io import BytesIO
from PIL import Image
import requests
from constants import RESULTS_FILE, SIMILARITY_THRESHOLD, MAX_TOTAL_RECORDS
from image_matcher import ImageMatcher
from browser_utils import setup_browser
from vk_utils import extract_vk_album_photos, extract_vk_photo_url
from search_utils import search_yandex_image
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
from openpyxl.utils import get_column_letter

def process_images(album_url):
    if not (album_url.startswith("https://vk.com/album") or album_url.startswith("https://vk.com/photo")):
        logging.error("Некорректная ссылка")
        messagebox.showerror("Ошибка", "Некорректная ссылка")
        return
    m = ImageMatcher()
    d = setup_browser()
    a = []
    c = [0]
    try:
        if album_url.startswith("https://vk.com/album"):
            pu = extract_vk_album_photos(d, album_url)
            if not pu:
                logging.info("Нет фото")
                return
            for i, p in enumerate(pu, 1):
                try:
                    logging.info(f"{p}")
                    iu = extract_vk_photo_url(d, p)
                    if not iu:
                        continue
                    r = requests.get(iu, timeout=10)
                    im = Image.open(BytesIO(r.content)).convert('RGB')
                    tmp = f"temp_{i}.jpg"
                    im.save(tmp)
                    se = m.get_embedding(tmp)
                    if se is None:
                        os.remove(tmp)
                        continue
                    search_yandex_image(d, tmp, m, se, f"Фото_{i}", a, c, iu)
                    os.remove(tmp)
                    if c[0] >= MAX_TOTAL_RECORDS:
                        break
                    time.sleep(1)
                except Exception as e:
                    logging.error(str(e))
                    continue
        elif album_url.startswith("https://vk.com/photo"):
            iu = extract_vk_photo_url(d, album_url)
            if not iu:
                logging.info("Нет фото")
                return
            try:
                r = requests.get(iu, timeout=10)
                im = Image.open(BytesIO(r.content)).convert('RGB')
                tmp = "temp_single.jpg"
                im.save(tmp)
                se = m.get_embedding(tmp)
                if se is None:
                    os.remove(tmp)
                    return
                search_yandex_image(d, tmp, m, se, "Фото_одиночное", a, c, iu)
                os.remove(tmp)
            except Exception as e:
                logging.error(str(e))
        if a:
            df = pd.DataFrame(a)
            if 'Схожесть' in df.columns:
                df = df[df['Схожесть'].astype(float) > SIMILARITY_THRESHOLD].reset_index(drop=True)
            for col in ['Дата публикации', 'Текст поста', 'Переслано от', 'Заголовок', 'IP адрес']:
                if col not in df.columns:
                    df[col] = ''
            f = RESULTS_FILE
            with pd.ExcelWriter(f, engine='openpyxl') as w:
                df.to_excel(w, index=False, sheet_name='Результаты')
                wb = w.book
                ws = w.sheets['Результаты']
                hf = Font(bold=True, color="FFFFFF")
                hc = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
                tb = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
                aw = Alignment(wrap_text=True)
                for col_idx in range(1, len(df.columns) + 1):
                    cell = ws.cell(row=1, column=col_idx)
                    cell.font = hf
                    cell.fill = hc
                    cell.border = tb
                    col_letter = get_column_letter(col_idx)
                    ml = max(df.iloc[:, col_idx - 1].astype(str).map(len).max(), len(str(cell.value)))
                    awidth = min(ml + 2, 50)
                    ws.column_dimensions[col_letter].width = awidth
                    for row_idx in range(2, len(df) + 2):
                        ccell = ws.cell(row=row_idx, column=col_idx)
                        ccell.alignment = aw
                        ccell.border = tb
                        if df.columns[col_idx - 1] in ['URL сайта', 'URL исходного фото', 'URL найденного фото']:
                            urlv = ccell.value
                            if isinstance(urlv, str) and urlv.startswith("http"):
                                ccell.value = "Ссылка"
                                ccell.hyperlink = urlv
                                ccell.style = "Hyperlink"
                if 'Схожесть' in df.columns:
                    sci = df.columns.get_loc('Схожесть') + 1
                    for row_idx in range(2, len(df) + 2):
                        sv = df.iloc[row_idx - 2]['Схожесть']
                        try:
                            sf = float(sv)
                        except:
                            sf = 0.0
                        cell = ws.cell(row=row_idx, column=sci)
                        if sf >= SIMILARITY_THRESHOLD:
                            fx = int((sf - SIMILARITY_THRESHOLD) / (1.0 - SIMILARITY_THRESHOLD) * 255)
                            fx = min(fx, 255)
                            color = f"{255:02X}{255 - fx:02X}{255 - fx:02X}"
                            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
            logging.info(f)
            messagebox.showinfo("Завершено", f"Данные записаны в {f}")
        else:
            logging.info("Нет данных")
            messagebox.showinfo("Завершено", "Нет данных")
    except Exception as e:
        logging.error(str(e))
        messagebox.showerror("Ошибка", str(e))
    finally:
        d.quit()
        logging.info("Браузер закрыт")
