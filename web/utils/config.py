import os
from pathlib import Path
from typing import Optional

class WebConfig:
    """Конфигурация веб-интерфейса"""
    
    def __init__(self):
        # Backend URL
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000/")
        
        # Настройки интерфейса
        self.page_title = "AI Agent Interface"
        self.page_icon = "🤖"
        
        # Настройки чата
        self.default_temperature = 0.7
        self.default_max_tokens = 1000
        self.max_history_length = 50
        
        # Настройки кеширования
        self.cache_ttl_agents = 60  # секунд
        self.cache_ttl_models = 300  # секунд
        
        # Путь к файлам
        self.web_dir = Path(__file__).parent.parent
        self.assets_dir = self.web_dir / "assets"
        
        # Создаем директорию для ассетов если её нет
        self.assets_dir.mkdir(exist_ok=True)
    
    @property
    def is_backend_local(self) -> bool:
        """Проверяет, локальный ли backend"""
        return "localhost" in self.backend_url or "127.0.0.1" in self.backend_url