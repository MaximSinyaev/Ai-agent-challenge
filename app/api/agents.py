from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import Agent, CreateAgentRequest, AgentConfig
from app.services.agent import agent_service
from app.database import get_db

router = APIRouter()


@router.post("/agents", response_model=Agent)
async def create_agent(request: CreateAgentRequest, db: AsyncSession = Depends(get_db)):
    """
    Создает нового агента
    """
    try:
        agent = await agent_service.create_agent(db, request.config)
        return agent
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents", response_model=List[Agent])
async def list_agents(db: AsyncSession = Depends(get_db)):
    """
    Возвращает список всех агентов
    """
    try:
        agents = await agent_service.list_agents(db)
        return agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """
    Получает агента по ID
    """
    agent = await agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/agents/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, config: AgentConfig, db: AsyncSession = Depends(get_db)):
    """
    Обновляет агента
    """
    try:
        agent = await agent_service.update_agent(db, agent_id, config)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """
    Удаляет агента
    """
    if agent_id == "default":
        raise HTTPException(status_code=400, detail="Cannot delete default agent")
    
    success = await agent_service.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found or is predefined")
    
    return {"message": "Agent deleted successfully"}