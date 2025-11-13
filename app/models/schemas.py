from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class MessageRole(str, Enum):
    """Роли сообщений"""
    USER = "user"
    ASSISTANT = "assistant" 
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Модель сообщения в чате"""
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    """Запрос для чата"""
    message: str
    model: Optional[str] = None
    agent_id: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ChatResponse(BaseModel):
    """Ответ от чата"""
    message: str
    model: str
    agent_id: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None


class AgentConfig(BaseModel):
    """Конфигурация агента"""
    name: str
    description: str
    system_prompt: str
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000


class Agent(BaseModel):
    """Модель агента"""
    id: str
    name: str
    description: str
    system_prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    created_at: str


class CreateAgentRequest(BaseModel):
    """Запрос на создание агента"""
    config: AgentConfig


class ModelInfo(BaseModel):
    """Информация о модели"""
    id: str
    name: str
    description: Optional[str] = None
    context_length: Optional[int] = None
    pricing: Optional[Dict[str, Any]] = None