from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
import json
from datetime import datetime

from app.database.models import AgentDB
from app.models.schemas import Agent, AgentConfig, ResponseFormat, ResponseFormatType


class AgentRepository:
    """Репозиторий для работы с агентами в базе данных"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_agents(self) -> List[Agent]:
        """Получить всех агентов"""
        result = await self.db.execute(select(AgentDB))
        agent_dbs = result.scalars().all()
        return [self._db_to_schema(agent_db) for agent_db in agent_dbs]
    
    async def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Получить агента по ID"""
        result = await self.db.execute(
            select(AgentDB).where(AgentDB.id == agent_id)
        )
        agent_db = result.scalar_one_or_none()
        return self._db_to_schema(agent_db) if agent_db else None
    
    async def create_agent(self, agent: Agent) -> Agent:
        """Создать нового агента"""
        agent_db = self._schema_to_db(agent)
        self.db.add(agent_db)
        try:
            await self.db.commit()
            await self.db.refresh(agent_db)
            return self._db_to_schema(agent_db)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(f"Agent with id '{agent.id}' already exists")
    
    async def update_agent(self, agent_id: str, agent: Agent) -> Optional[Agent]:
        """Обновить агента"""
        result = await self.db.execute(
            select(AgentDB).where(AgentDB.id == agent_id)
        )
        agent_db = result.scalar_one_or_none()
        
        if not agent_db:
            return None
        
        # Обновляем поля
        agent_db.name = agent.name
        agent_db.description = agent.description
        agent_db.system_prompt = agent.system_prompt
        agent_db.model = agent.model
        agent_db.temperature = agent.temperature
        agent_db.max_tokens = agent.max_tokens
        
        # Обновляем response format
        if agent.response_format:
            agent_db.response_format_type = agent.response_format.type.value
            agent_db.response_format_schema = json.dumps(agent.response_format.json_schema) if agent.response_format.json_schema else None
            agent_db.response_format_examples = json.dumps(agent.response_format.examples) if agent.response_format.examples else None
            agent_db.response_format_description = agent.response_format.description
        else:
            agent_db.response_format_type = None
            agent_db.response_format_schema = None
            agent_db.response_format_examples = None
            agent_db.response_format_description = None
        
        agent_db.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(agent_db)
        return self._db_to_schema(agent_db)
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Удалить агента"""
        result = await self.db.execute(
            select(AgentDB).where(AgentDB.id == agent_id)
        )
        agent_db = result.scalar_one_or_none()
        
        if not agent_db:
            return False
        
        # Не удаляем предустановленных агентов
        if agent_db.is_predefined:
            return False
        
        await self.db.delete(agent_db)
        await self.db.commit()
        return True
    
    async def clear_predefined_agents(self):
        """Очистить предустановленных агентов (для обновления из YAML)"""
        await self.db.execute(
            delete(AgentDB).where(AgentDB.is_predefined == True)
        )
        await self.db.commit()
    
    async def bulk_create_agents(self, agents: List[Agent], is_predefined: bool = False):
        """Массовое создание агентов"""
        agent_dbs = []
        for agent in agents:
            agent_db = self._schema_to_db(agent)
            agent_db.is_predefined = is_predefined
            agent_dbs.append(agent_db)
        
        self.db.add_all(agent_dbs)
        await self.db.commit()
    
    def _db_to_schema(self, agent_db: AgentDB) -> Agent:
        """Конвертировать модель БД в Pydantic схему"""
        response_format = None
        if agent_db.response_format_type:
            response_format = ResponseFormat(
                type=ResponseFormatType(agent_db.response_format_type),
                json_schema=json.loads(agent_db.response_format_schema) if agent_db.response_format_schema else None,
                examples=json.loads(agent_db.response_format_examples) if agent_db.response_format_examples else None,
                description=agent_db.response_format_description
            )
        
        return Agent(
            id=agent_db.id,
            name=agent_db.name,
            description=agent_db.description,
            system_prompt=agent_db.system_prompt,
            model=agent_db.model,
            temperature=agent_db.temperature,
            max_tokens=agent_db.max_tokens,
            response_format=response_format,
            created_at=agent_db.created_at.isoformat() if agent_db.created_at else datetime.utcnow().isoformat()
        )
    
    def _schema_to_db(self, agent: Agent) -> AgentDB:
        """Конвертировать Pydantic схему в модель БД"""
        agent_db = AgentDB(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            system_prompt=agent.system_prompt,
            model=agent.model,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens
        )
        
        if agent.response_format:
            agent_db.response_format_type = agent.response_format.type.value
            agent_db.response_format_schema = json.dumps(agent.response_format.json_schema) if agent.response_format.json_schema else None
            agent_db.response_format_examples = json.dumps(agent.response_format.examples) if agent.response_format.examples else None
            agent_db.response_format_description = agent.response_format.description
        
        return agent_db