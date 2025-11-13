# AI Agent Challenge

A full-featured AI agent system with Backend API and modern web interface.

## 🚀 Architecture

The project consists of two main components:

### **AI Agent Backend**
RESTful API server built with FastAPI and OpenRouter integration:
- Multi-agent system for creating and managing AI agents
- Support for 300+ AI models through OpenRouter
- Flexible configuration with Dynaconf
- Auto-generated API documentation

### **Web Interface**
Modern web interface built with Streamlit:
- Intuitive chat interface with native Streamlit components
- Agent management (create, configure, delete)
- Model browser with filtering and statistics
- Settings and session management

## 🌟 Key Features

- **Multi-Agent System** - Create and manage multiple AI agents with different personalities
- **Web Interface** - User-friendly graphical interface for all operations
- **OpenRouter Integration** - Access to 300+ AI models from various providers
- **Flexible Configuration** - Easy setup with Dynaconf configuration management
- **RESTful API** - Complete API with automatic documentation
- **Docker Support** - Containerized deployment ready
- **Extensible Architecture** - Modular design for easy feature additions

## 🚀 Быстрый старт

### Вариант 1: Запуск с веб-интерфейсом (рекомендуется)

```bash
# 1. Клонируем репозиторий
git clone <repository>
cd ai-agent-challenge

# 2. Устанавливаем зависимости backend
pip install -r requirements.txt

# 3. Настраиваем конфигурацию
cp app/config/.secrets.toml.example app/config/.secrets.toml
# Отредактируйте .secrets.toml, добавив ваш OpenRouter API ключ

# 4. Запускаем backend
./run_server.sh

# 5. В новом терминале запускаем веб-интерфейс
cd web
pip install -r requirements.txt
./run_web.sh
```

**Готово!** Откройте http://localhost:8501 для веб-интерфейса

### Вариант 2: Только Backend API

```bash
# 1-3. Те же шаги что и выше
# 4. Запускаем только backend
./run_server.sh
```

**API доступен на:** http://localhost:8000 (документация: /docs)

### 2. Настройка

Создайте файл с секретными настройками:

```bash
cp app/config/.secrets.toml.example app/config/.secrets.toml
```

Отредактируйте `app/config/.secrets.toml`:
```toml
[default]
    OPEN_ROUTER_API_KEY = "your_openrouter_api_key_here"
```

Установите переменную окружения (или создайте `.env` файл):
```bash
export APPLICATION_ENV=LOCAL
# или создайте .env файл с APPLICATION_ENV=LOCAL
```

### 3. Запуск

```bash
# Для разработки с автоперезагрузкой
uvicorn app.main:app --reload

# Или с помощью Python
python -m app.main
```

### 4. Тестирование

```bash
# Автоматическое тестирование API
python test_api.py

# Или вручную с curl
./examples.sh
```

## API Endpoints

### Основные endpoints

| Метод | URL       | Описание                         |
| ----- | --------- | -------------------------------- |
| `GET` | `/`       | Health check                     |
| `GET` | `/health` | Подробная информация о состоянии |
| `GET` | `/docs`   | Swagger документация             |

### Чат

| Метод  | URL     | Описание                      |
| ------ | ------- | ----------------------------- |
| `POST` | `/chat` | Отправить сообщение AI агенту |

**Пример запроса:**
```json
{
  "message": "Привет! Как дела?",
  "agent_id": "default",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

### Агенты

| Метод    | URL            | Описание                |
| -------- | -------------- | ----------------------- |
| `GET`    | `/agents`      | Получить список агентов |
| `POST`   | `/agents`      | Создать нового агента   |
| `GET`    | `/agents/{id}` | Получить агента по ID   |
| `DELETE` | `/agents/{id}` | Удалить агента          |

**Пример создания агента:**
```json
{
  "config": {
    "name": "Code Assistant", 
    "description": "Помощник для программирования",
    "system_prompt": "Ты опытный программист...",
    "temperature": 0.3,
    "max_tokens": 2000
  }
}
```

### Модели

| Метод | URL       | Описание                               |
| ----- | --------- | -------------------------------------- |
| `GET` | `/models` | Список доступных моделей из OpenRouter |

## Архитектура

```
ai-agent-challenge/
├── app/                     # 🔧 Backend API
│   ├── main.py              # FastAPI приложение
│   ├── config/              # Конфигурация Dynaconf
│   │   ├── config.py        # Настройки Dynaconf
│   │   ├── settings.toml    # Основные настройки
│   │   └── .secrets.toml    # Секретные настройки
│   ├── api/                 # API роутеры
│   │   ├── chat.py          # Чат endpoints
│   │   ├── agents.py        # Агенты endpoints  
│   │   └── models.py        # Модели endpoints
│   ├── models/              # Pydantic модели
│   │   └── schemas.py       # Схемы данных
│   └── services/            # Бизнес логика
│       ├── openrouter.py    # OpenRouter интеграция
│       └── agent.py         # Управление агентами
├── web/                     # 🌐 Web Interface
│   ├── app.py               # Главное Streamlit приложение
│   ├── requirements.txt     # Web зависимости
│   ├── run_web.sh          # Скрипт запуска веб-интерфейса
│   ├── components/          # UI компоненты
│   │   ├── chat.py          # Интерфейс чата
│   │   ├── sidebar.py       # Боковая панель
│   │   └── agent_manager.py # Управление агентами
│   ├── utils/               # Утилиты веб-приложения
│   │   ├── api_client.py    # HTTP клиент для Backend
│   │   └── config.py       # Конфигурация веб-приложения
│   ├── pages/               # Дополнительные страницы
│   │   ├── 1_🎯_Модели.py   # Браузер моделей
│   │   └── 2_⚙️_Настройки.py# Настройки
│   └── .streamlit/          # Конфигурация Streamlit
│       └── config.toml      
├── run_server.sh            # Скрипт запуска backend
├── test_api.py              # Автотесты API
├── examples.sh              # Примеры curl команд
├── requirements.txt         # Backend зависимости
├── Dockerfile               # Docker образ backend
├── docker-compose.yml       # Docker Compose
└── README.md               # Документация
```

## 🌐 Веб-интерфейс

### Основные возможности

- **💬 Чат-интерфейс:** Удобный интерфейс для общения с AI агентами
- **🤖 Управление агентами:** Создание, настройка и удаление агентов
- **🎯 Браузер моделей:** Просмотр доступных AI моделей с фильтрацией
- **⚙️ Настройки:** Конфигурация параметров и сессии
- **📊 Статистика:** Отслеживание использования

### Использование

1. **Запустите backend и веб-интерфейс** (см. Быстрый старт)
2. **Откройте в браузере:** http://localhost:8501
3. **Начните чат:** Выберите агента и отправьте сообщение
4. **Создавайте агентов:** Используйте вкладку "Управление агентами"
5. **Настройте параметры:** Используйте боковую панель

## 🐳 Docker развертывание

### Backend

```bash
# Сборка и запуск backend
docker build -t ai-agent-backend .
docker run -p 8000:8000 -e OPEN_ROUTER_API_KEY=your_key ai-agent-backend
```

### Веб-интерфейс

```bash
# Сборка и запуск веб-интерфейса
cd web
docker build -t ai-agent-web .
docker run -p 8501:8501 ai-agent-web
```

### Полная система

```bash
# Запуск полной системы через Docker Compose
docker-compose up --build
```

## Расширение функциональности

Архитектура спроектирована для легкого расширения:

### 1. Добавление нового типа агента

Создайте новый класс в `app/services/agent.py` или отдельный файл.

### 2. Добавление стриминга

Добавьте в `openrouter.py` метод для streaming:

```python
async def chat_completion_stream(self, messages, **kwargs):
    # Реализация стриминга
    pass
```

### 3. Добавление цепочек мышления

Создайте новый сервис `app/services/chain_of_thought.py`.

### 4. Добавление базы данных

Замените in-memory хранилище в `AgentService` на SQLAlchemy или другую ORM.

## Примеры использования

### Создание специализированного агента

```python
import aiohttp

async def create_coding_agent():
    data = {
        "config": {
            "name": "Python Expert",
            "description": "Эксперт по Python",
            "system_prompt": "Ты опытный Python разработчик...",
            "temperature": 0.2,
            "max_tokens": 2000
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8000/agents", json=data) as response:
            return await response.json()
```

### Чат с агентом

```python
async def chat_with_agent(agent_id, message):
    data = {
        "message": message,
        "agent_id": agent_id
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8000/chat", json=data) as response:
            return await response.json()
```

## Развитие проекта

Следующие шаги для развития:

1. **Стриминг ответов** - Server-Sent Events для real-time ответов
2. **История разговоров** - Сохранение и восстановление контекста
3. **RAG интеграция** - Поиск и использование внешних знаний
4. **Цепочки мышления** - Многошаговые рассуждения
5. **Разные провайдеры** - Поддержка других API (Anthropic, Google, etc.)
6. **База данных** - Persistent storage для агентов и истории
7. **Аутентификация** - Система пользователей и API ключей
8. **Мониторинг** - Метрики, логирование, трейсинг

## Лицензия

MIT License