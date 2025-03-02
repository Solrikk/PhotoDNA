
# PhotoDNA

![GitHub license](https://img.shields.io/github/license/Solrikk/PhotoDNA?style=flat&logo=github)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=flat&logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?style=flat&logo=tensorflow)

## О проекте

PhotoDNA - это инструмент для поиска, анализа и сравнения изображений с использованием алгоритмов машинного обучения. Система позволяет находить дубликаты и похожие изображения в социальных сетях, определять первоисточники контента и анализировать медиаданные.

## Функциональные возможности

- Поиск похожих изображений по образцу
- Извлечение и анализ метаданных изображений
- Сравнение визуального содержимого с использованием алгоритмов глубокого обучения
- Интеграция с ВКонтакте для анализа альбомов и отдельных фотографий
- Экспорт результатов в Excel с подробной информацией

## Структура проекта

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

## Использование

1. **Запуск графического интерфейса:**

   ```bash
   python main.py
   ```

2. **Ввод данных для анализа:**
   - Введите логин и пароль ВКонтакте
   - Добавьте ссылку на альбом или фотографию в формате:
     - `https://vk.com/album{owner_id}_{album_id}`
     - `https://vk.com/photo{owner_id}_{photo_id}`
   - Нажмите кнопку "Начать обработку"

3. **Результаты:**
   - Результаты анализа сохраняются в Excel-файл с timestamp в имени
   - Записи сортируются по степени схожести изображений
   - Для каждого результата доступны ссылки на оригинал и найденное изображение

## Технические особенности

- Использование ResNet50 для извлечения визуальных признаков изображений
- Сравнение изображений с использованием косинусного расстояния
- Многопоточная обработка для повышения производительности
- Интеграция с Selenium для взаимодействия с веб-страницами
- Анализ текста с использованием spaCy для русского языка

## Требования к системе

- Python 3.7+
- TensorFlow 2.x
- Microsoft Edge или совместимый браузер
- Доступ в интернет

## Автор

[Solrikk](https://github.com/Solrikk)
