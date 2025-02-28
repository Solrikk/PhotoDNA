
[![GitHub license](https://img.shields.io/github/license/Solrikk/PhotoDNA?style=flat&logo=github)](https://github.com/Solrikk/PhotoDNA/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=flat&logo=python)](https://www.python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?style=flat&logo=tensorflow)](https://www.tensorflow.org)


# PhotoDNA

```
photo_dna/
  ├─ __init__.py
  ├─ main.py
  ├─ constants.py
  ├─ image_matcher.py
  ├─ browser_utils.py
  ├─ vk_utils.py
  ├─ search_utils.py
  ├─ utils.py
  ├─ processing.py
  └─ gui.py
```

## Установка

1. **Клонирование репозитория:**

   ```bash
   git clone https://github.com/Solrikk/PhotoDNA.git
   cd PhotoDNA
   ```
2. **Создание виртуального окружения:**

```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\Scripts\activate     # для Windows
```

3. **Установка зависимостей:**

```bash
pip install -r requirements.txt
```

4. **Загрузка языковой модели для spaCy:**

```bash
python -m spacy download ru_core_news_sm
```
