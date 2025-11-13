from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Agent, CreateAgentRequest, AgentConfig
from app.services.agent import agent_service

router = APIRouter()


@router.post("/agents", response_model=Agent)
async def create_agent(request: CreateAgentRequest):
    """
    Создает нового агента
    """
    try:
        agent = agent_service.create_agent(request.config)
        return agent
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents", response_model=List[Agent])
async def list_agents():
    """
    Возвращает список всех агентов
    """
    try:
        agents = agent_service.list_agents()
        return agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """
    Получает агента по ID
    """
    agent = agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """
    Удаляет агента
    """
    if agent_id == "default":
        raise HTTPException(status_code=400, detail="Cannot delete default agent")
    
    success = agent_service.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"message": "Agent deleted successfully"}