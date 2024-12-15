# Formula Manager

Formula Manager - это веб-приложение для управления и сравнения математических формул. Система предоставляет удобный интерфейс для создания, редактирования и поиска математических формул с использованием нотации LaTeX, а также функционал для поиска похожих формул на основе их математической эквивалентности.

## Возможности

- ✏️ Создание и редактирование математических формул с помощью интуитивного LaTeX-редактора
- 🔍 Поиск формул по описанию или содержанию
- 🔄 Сравнение формул для поиска похожих выражений
- 🚀 REST API для интеграции с другими сервисами

## Технологический стек

- **Frontend**: React, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, PostgreSQL
- **Инфраструктура**: Docker, Docker Compose
- **Обработка математики**: KaTeX, React Math Keyboard

## Быстрый старт

### Предварительные требования

1. Установите Docker и Docker Compose
   - Windows/Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Linux: [Docker Engine](https://docs.docker.com/engine/install/) и [Docker Compose](https://docs.docker.com/compose/install/)

### Установка

1. Скачайте архив проекта [здесь](https://github.com/SafeKitty-Team/formulService/releases/download/done/demo.zip)
2. Распакуйте архив в удобное место
3. Откройте терминал и перейдите в папку с проектом
4. Выполните команду:
   ```bash
   docker-compose up --build
   ```
5. Откройте приложение в браузере по адресу `http://localhost:8000`

## API документация

Бэкенд предоставляет REST API со следующими эндпоинтами:

### Эндпоинты

```
GET /formulas - Получить все формулы
POST /manage_formula - Создать/Обновить/Удалить формулу
POST /find_similar - Найти похожие формулы
POST /convert_ast_to_latex - Конвертировать AST в LaTeX
```

Полная документация по API доступна по адресу `http://localhost:8000/docs` при запущенном приложении.

## Настройка для разработки

Для запуска приложения в режиме разработки:

1. Frontend:
   ```bash
   cd frontend
   npm install
   npm start
   ```

2. Backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
