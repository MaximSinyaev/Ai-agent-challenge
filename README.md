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

## 🚀 Quick Start

### Method 1: Full Stack (Recommended)

```bash
# 1. Clone the repository
git clone <repository>
cd ai-agent-challenge

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Configure secrets
cp app/config/.secrets.toml.example app/config/.secrets.toml
# Edit .secrets.toml and add your OpenRouter API key

# 4. Start backend server
./run_server.sh

# 5. In a new terminal, start web interface
cd web
pip install -r requirements.txt
./run_web.sh
```

**Done!** Open http://localhost:8501 for the web interface

### Method 2: Backend Only

```bash
# Follow steps 1-3 above, then:
./run_server.sh
```

**API available at:** http://localhost:8000 (docs at /docs)

### 2. Configuration

Create secrets file:
```bash
cp app/config/.secrets.toml.example app/config/.secrets.toml
```

Edit `app/config/.secrets.toml`:
```toml
[default]
    OPEN_ROUTER_API_KEY = "your_openrouter_api_key_here"
```

Set environment variable:
```bash
export APPLICATION_ENV=LOCAL
# or create .env file with APPLICATION_ENV=LOCAL
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

## 📚 API Documentation

The backend provides a complete RESTful API:

- **Chat**: Send messages to AI agents
- **Agents**: Create, list, and manage AI agents
- **Models**: Browse available AI models from OpenRouter

**API Documentation**: http://localhost:8000/docs (when server is running)

## 📁 Project Structure

```
ai-agent-challenge/
├── app/                     # Backend application
│   ├── main.py             # FastAPI application
│   ├── config/             # Configuration (Dynaconf)
│   ├── api/                # API endpoints
│   ├── models/             # Pydantic schemas
│   └── services/           # Business logic
├── web/                    # Web interface
│   ├── app.py              # Streamlit application
│   ├── components/         # UI components
│   ├── pages/              # Additional pages
│   └── utils/              # Utilities
├── requirements.txt        # Backend dependencies
├── Dockerfile             # Backend container
├── docker-compose.yml     # Full stack deployment
└── run_server.sh          # Server launch script
```

## � Docker Deployment

### Full Stack with Docker Compose

```bash
# Create environment file
echo "OPEN_ROUTER_API_KEY=your_api_key_here" > .env

# Deploy complete system
docker-compose up --build
```

Services will be available at:
- **Web Interface**: http://localhost:8501
- **Backend API**: http://localhost:8000

## 🛠️ Requirements

- **Python 3.8+**
- **OpenRouter API Key** (get one at [openrouter.ai](https://openrouter.ai))
- **Docker** (optional, for containerized deployment)

## 🔧 Technologies

- **Backend**: FastAPI, Dynaconf, OpenAI SDK
- **Frontend**: Streamlit with native chat components
- **AI Models**: OpenRouter integration (300+ models)
- **Configuration**: TOML-based with environment-specific settings

---

**Get started in 5 minutes** - Just clone, configure your API key, and run!