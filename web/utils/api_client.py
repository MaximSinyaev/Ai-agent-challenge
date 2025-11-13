import httpx
import asyncio
from typing import Dict, List, Any, Optional
import streamlit as st

class APIClient:
    """Клиент для взаимодействия с AI Agent Backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 30.0
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполняет HTTP запрос к API"""
        url = f"{self.base_url}{endpoint}"
        
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
        return self._make_request("GET", "/health")
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Получение списка агентов"""
        return self._make_request("GET", "/agents")
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Получение агента по ID"""
        return self._make_request("GET", f"/agents/{agent_id}")
    
    def create_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Создание нового агента"""
        return self._make_request("POST", "/agents", json={"config": config})
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Удаление агента"""
        return self._make_request("DELETE", f"/agents/{agent_id}")
    
    def send_chat_message(
        self,
        message: str,
        agent_id: str = "default",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Отправка сообщения в чат"""
        payload = {
            "message": message,
            "agent_id": agent_id
        }
        
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if model is not None:
            payload["model"] = model
        
        return self._make_request("POST", "/chat", json=payload)
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Получение списка доступных моделей"""
        return self._make_request("GET", "/models")
    
    def ping(self) -> bool:
        """Простая проверка доступности API"""
        try:
            response = self._make_request("GET", "/")
            return response.get("status") == "healthy"
        except:
            return False