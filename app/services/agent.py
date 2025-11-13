from typing import Dict, List, Optional
from datetime import datetime
import uuid
from app.models.schemas import Agent, AgentConfig, ChatMessage, MessageRole


class AgentService:
    """Сервис для управления AI агентами"""
    
    def __init__(self):
        # Временное хранилище агентов в памяти
        # В реальном проекте здесь будет база данных
        self._agents: Dict[str, Agent] = {}
        
        # Создаем агента по умолчанию
        self._create_default_agent()
    
    def _create_default_agent(self):
        """Создает агента по умолчанию"""
        default_config = AgentConfig(
            name="Default Assistant", 
            description="Default AI assistant agent.",
            system_prompt="You are a helpful AI assistant. Answer the user's questions to the best of your ability.",
            temperature=0.7,
            max_tokens=1000
        )
        self.create_agent(default_config, agent_id="default")
    
    def create_agent(self, config: AgentConfig, agent_id: str = None) -> Agent:
        """Создает нового агента"""
        agent_id = agent_id or str(uuid.uuid4())
        
        agent = Agent(
            id=agent_id,
            name=config.name,
            description=config.description,
            system_prompt=config.system_prompt,
            model=config.model or "kwaipilot/kat-coder-pro:free",
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            created_at=datetime.now().isoformat()
        )
        
        self._agents[agent_id] = agent
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Получает агента по ID"""
        return self._agents.get(agent_id)
    
    def list_agents(self) -> List[Agent]:
        """Возвращает список всех агентов"""
        return list(self._agents.values())
    
    def delete_agent(self, agent_id: str) -> bool:
        """Удаляет агента"""
        if agent_id in self._agents and agent_id != "default":
            del self._agents[agent_id]
            return True
        return False
    
    def prepare_messages_for_agent(
        self, 
        agent: Agent, 
        user_message: str,
        conversation_history: List[ChatMessage] = None
    ) -> List[ChatMessage]:
        """Подготавливает сообщения для отправки агенту"""
        messages = []
        
        # Добавляем системное сообщение
        if agent.system_prompt:
            messages.append(ChatMessage(
                role=MessageRole.SYSTEM,
                content=agent.system_prompt
            ))
        
        # Добавляем историю разговора (если есть)
        if conversation_history:
            messages.extend(conversation_history)
        
        # Добавляем текущее сообщение пользователя
        messages.append(ChatMessage(
            role=MessageRole.USER,
            content=user_message
        ))
        
        return messages


# Глобальный экземпляр сервиса
agent_service = AgentService()