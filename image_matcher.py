import logging
import numpy as np
import requests
import spacy
from io import BytesIO
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import TfidfVectorizer
import dateparser
from bs4 import BeautifulSoup

class ImageMatcher:
    def __init__(self):
        logging.info("Загрузка модели ResNet50...")
        self.model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
        logging.info("Загрузка модели spaCy...")
        try:
            self.nlp = spacy.load("ru_core_news_sm")
        except OSError:
            logging.info("Установка ru_core_news_sm...")
            from spacy.cli import download
            download("ru_core_news_sm")
            self.nlp = spacy.load("ru_core_news_sm")
        logging.info("Инициализация TF-IDF...")
        self.vectorizer = TfidfVectorizer(max_features=10, stop_words='russian')

    def preprocess_image(self, img_path):
        try:
            if isinstance(img_path, str):
                img = image.load_img(img_path, target_size=(224, 224))
            else:
                img = img_path.resize((224, 224), Image.Resampling.LANCZOS)
            x = np.asarray(img, dtype=np.float32)
            x = np.expand_dims(x, axis=0)
            return preprocess_input(x)
        except Exception as e:
            logging.warning(str(e))
            return None

    def get_embedding(self, img):
        try:
            preprocessed = self.preprocess_image(img)
            if preprocessed is not None:
                return self.model.predict(preprocessed, verbose=0)
            return None
        except Exception as e:
            logging.warning(str(e))
            return None

    @staticmethod
    def compare_images_batch(embedding1, embeddings_list):
        try:
            return 1 - np.array([cosine(embedding1.flatten(), emb.flatten()) for emb in embeddings_list])
        except Exception as e:
            logging.warning(str(e))
            return np.zeros(len(embeddings_list))

    def compare_images(self, embedding1, embedding2):
        try:
            return float(1 - cosine(embedding1.flatten(), embedding2.flatten()))
        except Exception as e:
            logging.warning(str(e))
            return 0.0

    def download_and_process_image(self, url):
        try:
            r = requests.get(url, timeout=10)
            img = Image.open(BytesIO(r.content)).convert('RGB')
            return self.get_embedding(img)
        except Exception as e:
            logging.warning(str(e))
            return None

    def fetch_page_text(self, url):
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
            return ' '.join(soup.stripped_strings)
        except Exception as e:
            logging.warning(str(e))
            return ""

    def generate_title(self, text):
        try:
            if '—' in text:
                t = text.split('—')[0].strip()
            else:
                t = text.strip()
            if not t:
                return None
            logging.info(f"Извлечён заголовок: {t}")
            return t
        except Exception as e:
            logging.warning(str(e))
            return None

    def extract_image_info(self, soup, image_url):
        try:
            tags = soup.find_all('img', src=image_url)
            for img in tags:
                t = img.get('title')
                a = img.get('alt')
                if t:
                    return t
                if a:
                    return a
            return None
        except:
            return None

    def extract_publication_date(self, soup):
        try:
            m = soup.find('meta', attrs={'property': 'article:published_time'})
            if m and m.get('content'):
                return m.get('content')
            for tag in soup.find_all(['span', 'div', 'p']):
                text = tag.get_text(strip=True)
                d = dateparser.parse(text, languages=['ru'])
                if d:
                    return d.isoformat()
            return None
        except Exception as e:
            logging.warning(str(e))
            return None
