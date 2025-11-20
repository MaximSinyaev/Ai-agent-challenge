from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class MessageRole(str, Enum):
    """Роли сообщений"""
    USER = "user"
    ASSISTANT = "assistant" 
    SYSTEM = "system"


class ResponseFormatType(str, Enum):
    """Типы форматов ответов"""
    PLAIN_TEXT = "plain_text"
    JSON = "json"
    MARKDOWN = "markdown"
    CODE_BLOCK = "code_block"


class ResponseFormat(BaseModel):
    """Конфигурация формата ответа"""
    type: ResponseFormatType = ResponseFormatType.PLAIN_TEXT
    json_schema: Optional[Dict[str, Any]] = None
    examples: Optional[List[str]] = None
    description: Optional[str] = None


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
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    """Ответ от чата"""
    message: str
    model: str
    agent_id: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    parsed_data: Optional[Any] = None
    format_valid: Optional[bool] = None
    response_format: Optional[ResponseFormat] = None
    orchestration_steps: Optional[List[Dict[str, Any]]] = None


class AgentConfig(BaseModel):
    """Конфигурация агента"""
    name: str
    description: str
    system_prompt: str
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    response_format: Optional[ResponseFormat] = None


class Agent(BaseModel):
    """Модель агента"""
    id: str
    name: str
    description: str
    system_prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    response_format: Optional[ResponseFormat] = None
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