# ALISA SCHOOL · Backend с Google Gemini AI

Бэкенд на **Python + FastAPI**, подключающий сайт ALISA SCHOOL к Google Gemini.
Позволяет генерировать подробные ИИ-объяснения для каждой темы и задавать вопросы ассистенту.

## Структура

```
site/backend/
├── main.py           # FastAPI-приложение (API + раздача сайта)
├── gemini_client.py  # Обёртка над Gemini API
├── requirements.txt  # Зависимости
├── .env              # GEMINI_API_KEY (секрет, не коммитить)
└── .env.example      # Шаблон для копирования
```

## Установка

### 1. Получите ключ Gemini API

1. Откройте https://aistudio.google.com/apikey
2. Нажмите **Create API key**
3. Скопируйте ключ

### 2. Впишите ключ

Отредактируйте файл `site/backend/.env`:

```
GEMINI_API_KEY=ваш_настоящий_ключ
GEMINI_MODEL=gemini-3.6-flash
```

### 3. Установите зависимости (один раз)

```bash
cd site/backend
python3 -m venv .venv
source .venv/bin/activate          # на Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> Примечание для macOS: если установка `cryptography` падает с ошибкой
> «No developer tools found», установите его отдельно через
> `pip install --only-binary :all: cryptography` или поставьте Xcode Command Line Tools.
>
> На Apple Silicon (M1/M2/...): если возникает `ImportError: incompatible architecture (have 'x86_64', need 'arm64')`,
> значит пакеты поставились под Rosetta. Переустановите бинарные пакеты нативно:
> ```bash
> arch -arm64 .venv/bin/python3 -m pip install --force-reinstall --only-binary :all: pydantic-core pydantic cffi cryptography grpcio
> ```
> и запускайте сервер через `arch -arm64 uvicorn main:app --port 8000`.

### 4. Запустите сервер

```bash
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000
```

Откройте в браузере: **http://127.0.0.1:8000** — сайт загрузится с AI-функциями.

## Эндпоинты API

| Метод | Путь           | Описание                                          |
|-------|----------------|---------------------------------------------------|
| GET   | `/`            | Раздаёт сайт `js/Алиса School .html`              |
| GET   | `/api/health`  | Проверка работы и статуса ключа                   |
| POST  | `/api/explain` | ИИ-объяснение темы: `{grade, subject, topic}`     |
| POST  | `/api/ask`     | Ответ ассистента: `{grade, subject, question, topic}` |
| POST  | `/api/task`    | Генерация задачки: `{subject, level}`             |

Документация Swagger: **http://127.0.0.1:8000/docs**

## Как работает интеграция

- Кнопка **«🤖 AI объяснить»** у каждой темы генерирует развёрнутое объяснение от Gemini.
- Блок **«AI-ассистент»** на странице предметов отвечает на любые вопросы школьника по предмету.
- Все запросы идут на `127.0.0.1:8000/api/...`.

## Безопасность ключа

Ключ хранится только в `site/backend/.env` и **не** попадает на фронтенд —
браузер работает с ним только через бэкенд. Не публикуйте `.env` в репозиторий.