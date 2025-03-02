import os
import logging

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['OMP_NUM_THREADS'] = '1'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

from gui import create_gui
from processing import cleanup_temp_files

if __name__ == "__main__":
    try:
        create_gui()
    except Exception as e:
        logging.error(f"Критическая ошибка при запуске приложения: {str(e)}")
    finally:
        cleanup_temp_files()
