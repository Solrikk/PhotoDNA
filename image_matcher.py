import os
import numpy as np
import requests
from PIL import Image
from io import BytesIO
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from scipy.spatial.distance import cosine
from bs4 import BeautifulSoup
import spacy
import dateparser
import logging

class ImageMatcher:

    def __init__(self):
        logging.info("Загрузка модели ResNet50...")
        self.model = ResNet50(weights='imagenet',
                              include_top=False,
                              pooling='avg')
        logging.info("Загрузка модели spaCy...")
        try:
            self.nlp = spacy.load("ru_core_news_sm")
        except OSError:
            logging.info(
                "Модель spaCy 'ru_core_news_sm' не найдена. Загружаю...")
            from spacy.cli import download
            download("ru_core_news_sm")
            self.nlp = spacy.load("ru_core_news_sm")
        logging.info("Инициализация TF-IDF векторизатора...")
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(max_features=10,
                                          stop_words='russian')

    def preprocess_image(self, img_path):
        try:
            if isinstance(img_path, str):
                img = image.load_img(img_path, target_size=(224, 224))
            else:
                img = img_path.resize((224, 224), Image.Resampling.NEAREST)
            x = np.asarray(img, dtype=np.float32)
            x = np.expand_dims(x, axis=0)
            return preprocess_input(x)
        except Exception as e:
            logging.warning(
                f"Ошибка при предварительной обработке изображения: {str(e)}")
            return None

    def get_embedding(self, img):
        try:
            preprocessed = self.preprocess_image(img)
            if preprocessed is not None:
                return self.model.predict(preprocessed, verbose=0)
            return None
        except Exception as e:
            logging.warning(f"Ошибка при получении эмбеддинга: {str(e)}")
            return None

    @staticmethod
    def compare_images_batch(embedding1, embeddings_list):
        try:
            similarities = 1 - np.array([
                cosine(embedding1.flatten(), emb.flatten())
                for emb in embeddings_list
            ])
            return similarities
        except Exception as e:
            logging.warning(
                f"Ошибка при пакетном сравнении изображений: {str(e)}")
            return np.zeros(len(embeddings_list))

    def compare_images(self, embedding1, embedding2):
        try:
            return float(1 -
                         cosine(embedding1.flatten(), embedding2.flatten()))
        except Exception as e:
            logging.warning(f"Ошибка при сравнении изображений: {str(e)}")
            return 0.0

    def download_and_process_image(self, url):
        try:
            response = requests.get(url, timeout=5)
            img = Image.open(BytesIO(response.content)).convert('RGB')
            return self.get_embedding(img)
        except Exception as e:
            logging.warning(f"Ошибка при обработке URL {url}: {str(e)}")
            return None

    def fetch_page_text(self, url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            texts = soup.stripped_strings
            return ' '.join(texts)
        except Exception as e:
            logging.warning(f"Ошибка при получении страницы {url}: {str(e)}")
            return ""

    def generate_title(self, text):
        try:
            if '—' in text:
                title = text.split('—')[0].strip()
            else:
                title = text.strip()
            if not title:
                logging.warning("Заголовок пуст после извлечения.")
                return None
            logging.info(f"Извлечённый заголовок: {title}")
            return title
        except Exception as e:
            logging.warning(f"Ошибка при генерации заголовка: {str(e)}")
            return None

    def extract_image_info(self, soup, image_url):
        try:
            img_tags = soup.find_all('img', src=image_url)
            for img in img_tags:
                title = img.get('title')
                alt = img.get('alt')
                if title:
                    return title
                if alt:
                    return alt
            return None
        except:
            return None

    def extract_publication_date(self, soup):
        try:
            meta_date = soup.find('meta',
                                  attrs={'property': 'article:published_time'})
            if meta_date and meta_date.get('content'):
                return meta_date.get('content')
            for tag in soup.find_all(['span', 'div', 'p']):
                text = tag.get_text(strip=True)
                date = dateparser.parse(text, languages=['ru'])
                if date:
                    return date.isoformat()
            return None
        except Exception as e:
            logging.warning(f"Ошибка при извлечении даты публикации: {str(e)}")
            return None
