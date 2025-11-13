import httpx
from typing import Dict, List, Any, Optional
import streamlit as st

class APIClient:
    """Клиент для взаимодействия с AI Agent Backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_version: str = "v1"):
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.timeout = 30.0
    
    @property
    def api_base_url(self) -> str:
        """Полный URL API с версионированием"""
        return f"{self.base_url}/api/{self.api_version}"
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполняет HTTP запрос к API"""
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"HTTP ошибка: {e}")
        except Exception as e:
            raise Exception(f"Ошибка запроса: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Проверка состояния backend сервиса"""
        # Health check без версионирования
        url = f"{self.base_url}/health"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request("GET", url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"HTTP ошибка: {e}")
        except Exception as e:
            raise Exception(f"Ошибка запроса: {e}")
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Получение списка агентов"""
        return self._make_request("GET", "/agents")
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Получение агента по ID"""
        return self._make_request("GET", f"/agents/{agent_id}")
    
    def create_agent(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание нового агента"""
        return self._make_request("POST", "/agents", json=request_data)
    
    def update_agent(self, agent_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление агента"""
        return self._make_request("PUT", f"/agents/{agent_id}", json=config)
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Удаление агента"""
        return self._make_request("DELETE", f"/agents/{agent_id}")
    
    def send_chat_message(
        self,
        message: str = None,
        agent_id: str = None,
        temperature: float = None,
        max_tokens: int = None,
        model: str = None,
        request_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Отправка сообщения в чат"""
        if request_data is None:
            request_data = {
                "message": message,
                "agent_id": agent_id,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "model": model
            }
            # Удаляем None значения
            request_data = {k: v for k, v in request_data.items() if v is not None}
        
        return self._make_request("POST", "/chat", json=request_data)
    
    def send_message(
        self,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Альтернативный метод для отправки сообщения (для обратной совместимости)"""
        return self.send_chat_message(request_data=request_data)
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Получение списка доступных моделей"""
        return self._make_request("GET", "/models")
    
    def ping(self) -> bool:
        """Простая проверка доступности API"""
        try:
            # Пинг без версионирования
            url = f"{self.base_url}/"
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request("GET", url)
                response.raise_for_status()
                return response.json().get("status") == "healthy"
        except:
            return False