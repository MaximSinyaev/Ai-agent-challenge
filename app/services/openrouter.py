from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.config import settings
from app.models.schemas import ChatMessage, ModelInfo


class OpenRouterService:
    """Сервис для работы с OpenRouter API"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.OPENROUTER.BASE_URL,
            api_key=settings.OPEN_ROUTER_API_KEY,
        )
    
    async def chat_completion(
        self, 
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Отправляет запрос на генерацию текста
        """
        # Подготовка сообщений для OpenAI API
        openai_messages = [
            {"role": msg.role.value, "content": msg.content} 
            for msg in messages
        ]
        
        # Параметры запроса
        params = {
            "model": model or settings.ASSISTANT.DEFAULT_MODEL,
            "messages": openai_messages,
            "extra_headers": {
                "HTTP-Referer": settings.SITE_URL,
                "X-Title": settings.SITE_NAME,
            },
            "extra_body": {},
        }
        
        # Добавляем опциональные параметры
        if temperature is not None:
            params["temperature"] = temperature
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
            
        # Добавляем дополнительные параметры
        params.update(kwargs)
        
        try:
            completion = self.client.chat.completions.create(**params)
            
            return {
                "message": completion.choices[0].message.content,
                "model": completion.model,
                "usage": completion.usage.model_dump() if completion.usage else None,
                "finish_reason": completion.choices[0].finish_reason
            }
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")
    
    async def get_models(self) -> List[ModelInfo]:
        """
        Получает список доступных моделей
        """
        try:
            # OpenRouter API endpoint для получения моделей
            models = self.client.models.list()
            
            model_list = []
            for model in models.data:
                model_info = ModelInfo(
                    id=model.id,
                    name=getattr(model, 'name', model.id),
                    description=getattr(model, 'description', None),
                    context_length=getattr(model, 'context_length', None),
                )
                model_list.append(model_info)
            
            return model_list
        except Exception as e:
            raise Exception(f"Failed to fetch models: {str(e)}")


# Глобальный экземпляр сервиса
openrouter_service = OpenRouterService()