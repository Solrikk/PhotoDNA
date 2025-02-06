# PhotoDNA

## Установка

1. **Клонирование репозитория:**

   ```bash
   git clone https://github.com/your_username/PhotoDNA.git
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
