import os
import logging
import glob

def cleanup_temp_files():
    """Удаление временных файлов"""
    try:
        for temp_file in glob.glob("temp_image_*.jpg"):
            try:
                os.remove(temp_file)
                logging.info(f"Удален временный файл: {temp_file}")
            except Exception as inner_e:
                logging.warning(f"Не удалось удалить файл {temp_file}: {str(inner_e)}")
    except Exception as e:
        logging.error(f"Ошибка при очистке временных файлов: {str(e)}")
