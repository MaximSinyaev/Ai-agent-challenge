from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.api import chat, agents, models
from app.database import init_db, close_db, get_db
from app.services.agent import agent_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Инициализация приложения...")
    await init_db()
    
    # Загружаем предустановленных агентов
    async for db in get_db():
        await agent_service.load_predefined_agents(db)
        break
    
    yield
    
    # Shutdown
    print("Завершение приложения...")
    await close_db()


# Создаем приложение FastAPI
app = FastAPI(
    title="AI Agent Backend",
    description="Backend для AI агента с поддержкой OpenRouter",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене следует ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры с версионированием API
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(models.router, prefix="/api/v1", tags=["models"])


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Agent Backend",
        "version": "1.0.0"
    }


@app.get("/health")
async def detailed_health():
    """Подробная информация о состоянии сервиса"""
    return {
        "status": "healthy",
        "service": "AI Agent Backend", 
        "version": "1.0.0",
        "openrouter_configured": bool(settings.OPEN_ROUTER_API_KEY),
        "default_model": settings.ASSISTANT.DEFAULT_MODEL
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )