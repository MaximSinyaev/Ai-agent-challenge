from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from enum import Enum


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


class AgentConfig(BaseModel):
    """Конфигурация агента для веб-интерфейса"""
    name: str
    description: str
    system_prompt: str
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    response_format: Optional[ResponseFormat] = None


class ChatMessage(BaseModel):
    """Сообщение в чате"""
    role: str  # "user" или "assistant"
    content: str
    timestamp: Optional[str] = None
    agent_id: Optional[str] = None
    model: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None  # Полный ответ от API
    parsed_data: Optional[Any] = None  # Распарсенные структурированные данные
    format_valid: Optional[bool] = None  # Валиден ли формат ответа