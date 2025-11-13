from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import ModelInfo
from app.services.openrouter import openrouter_service

router = APIRouter()


@router.get("/models", response_model=List[ModelInfo])
async def get_models():
    """
    Получает список доступных моделей из OpenRouter
    """
    try:
        models = await openrouter_service.get_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))