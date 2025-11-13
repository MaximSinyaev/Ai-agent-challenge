from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import (
    ChatRequest, 
    ChatResponse, 
    MessageRole, 
    ChatMessage
)
from app.services.openrouter import openrouter_service
from app.services.agent import agent_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Отправляет сообщение AI агенту
    """
    try:
        # Получаем агента
        agent_id = request.agent_id or "default"
        agent = agent_service.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Подготавливаем сообщения
        messages = agent_service.prepare_messages_for_agent(
            agent=agent,
            user_message=request.message
        )
        
        # Параметры для модели
        model = request.model or agent.model
        temperature = request.temperature if request.temperature is not None else agent.temperature
        max_tokens = request.max_tokens or agent.max_tokens
        
        # Отправляем запрос к OpenRouter
        result = await openrouter_service.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return ChatResponse(
            message=result["message"],
            model=result["model"],
            agent_id=agent_id,
            usage=result.get("usage")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))