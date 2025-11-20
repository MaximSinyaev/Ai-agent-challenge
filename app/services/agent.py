from typing import Dict, List, Optional
from datetime import datetime
import uuid
import json
from app.models.schemas import Agent, AgentConfig, ChatMessage, MessageRole, ResponseFormat, ResponseFormatType
from app.services.agent_loader import agent_loader
from app.database import get_db, AgentRepository
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.openrouter import openrouter_service


class AgentService:
    """Сервис для управления AI агентами"""
    
    def __init__(self):
        # Больше не используем хранилище в памяти, переходим на БД
        pass
    
    async def load_predefined_agents(self, db: AsyncSession):
        """Загружает предустановленных агентов из YAML файла в БД"""
        try:
            repository = AgentRepository(db)
            
            # Очищаем старых предустановленных агентов
            await repository.clear_predefined_agents()
            
            # Загружаем агентов из YAML
            predefined_agents_dict = agent_loader.load_agents()
            predefined_agents = list(predefined_agents_dict.values())
            
            # Сохраняем в БД как предустановленных
            if predefined_agents:
                await repository.bulk_create_agents(predefined_agents, is_predefined=True)
                print(f"Загружено {len(predefined_agents)} предустановленных агентов в БД")
            else:
                await self._create_fallback_agent(repository)
                
        except Exception as e:
            print(f"Ошибка загрузки предустановленных агентов: {e}")
            repository = AgentRepository(db)
            await self._create_fallback_agent(repository)
    
    async def _create_fallback_agent(self, repository: AgentRepository):
        """Создает базового агента если не удалось загрузить из YAML"""
        default_config = AgentConfig(
            name="Default Assistant", 
            description="Default AI assistant agent.",
            system_prompt="You are a helpful AI assistant. Answer the user's questions to the best of your ability.",
            temperature=0.7,
            max_tokens=1000
        )
        agent = await self.create_agent_from_config(repository, default_config, agent_id="default")
        print("Создан fallback агент")
    
    async def create_agent_from_config(self, repository: AgentRepository, config: AgentConfig, agent_id: str = None) -> Agent:
        """Создает нового агента из конфигурации"""
        agent_id = agent_id or str(uuid.uuid4())
        
        agent = Agent(
            id=agent_id,
            name=config.name,
            description=config.description,
            system_prompt=config.system_prompt,
            model=config.model or settings.ASSISTANT.DEFAULT_MODEL,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            response_format=config.response_format,
            created_at=datetime.now().isoformat()
        )
        
        return await repository.create_agent(agent)
    
    async def get_agent(self, db: AsyncSession, agent_id: str) -> Optional[Agent]:
        """Получает агента по ID"""
        repository = AgentRepository(db)
        return await repository.get_agent_by_id(agent_id)
    
    async def list_agents(self, db: AsyncSession) -> List[Agent]:
        """Возвращает список всех агентов"""
        repository = AgentRepository(db)
        return await repository.get_all_agents()
    
    async def create_agent(self, db: AsyncSession, config: AgentConfig, agent_id: str = None) -> Agent:
        """Создает нового агента"""
        repository = AgentRepository(db)
        return await self.create_agent_from_config(repository, config, agent_id)
    
    async def update_agent(self, db: AsyncSession, agent_id: str, config: AgentConfig) -> Optional[Agent]:
        """Обновляет агента"""
        repository = AgentRepository(db)
        
        # Создаем объект Agent из конфигурации
        agent = Agent(
            id=agent_id,
            name=config.name,
            description=config.description,
            system_prompt=config.system_prompt,
            model=config.model or settings.ASSISTANT.DEFAULT_MODEL,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            response_format=config.response_format,
            created_at=datetime.now().isoformat()
        )
        
        return await repository.update_agent(agent_id, agent)
    
    async def delete_agent(self, db: AsyncSession, agent_id: str) -> bool:
        """Удаляет агента"""
        repository = AgentRepository(db)
        return await repository.delete_agent(agent_id)
    
    def is_orchestrator_agent(self, agent: Agent) -> bool:
        """Проверяет, является ли агент оркестратором субагентов"""
        return agent.id == "subagent_orchestrator"
    
    async def orchestrate_subagents(self, db: AsyncSession, user_message: str, conversation_history: List[ChatMessage] = None) -> Dict:
        """Оркестрирует взаимодействие между субагентами"""
        try:
            # Получаем субагентов
            task_solver = await self.get_agent(db, "task_solver")
            result_processor = await self.get_agent(db, "result_processor")
            
            if not task_solver or not result_processor:
                raise Exception("Subagents not found")
            
            # Шаг 1: Отправляем задачу первому субагенту (task_solver)
            task_messages = self.prepare_messages_for_agent(
                agent=task_solver,
                user_message=user_message,
                conversation_history=conversation_history
            )
            
            task_result = await openrouter_service.chat_completion(
                messages=task_messages,
                model=task_solver.model,
                temperature=task_solver.temperature,
                max_tokens=task_solver.max_tokens
            )
            
            # Парсим JSON ответ от task_solver
            try:
                task_output = json.loads(task_result["message"])
            except json.JSONDecodeError:
                raise Exception("Task solver returned invalid JSON")
            
            # Шаг 2: Отправляем результат второму субагенту (result_processor)
            # Создаем сообщение для result_processor с JSON данными от task_solver
            processor_input = f"Process this task result:\n{json.dumps(task_output, indent=2)}"
            
            processor_messages = self.prepare_messages_for_agent(
                agent=result_processor,
                user_message=processor_input,
                conversation_history=None  # Не передаем историю для процессора
            )
            
            processor_result = await openrouter_service.chat_completion(
                messages=processor_messages,
                model=result_processor.model,
                temperature=result_processor.temperature,
                max_tokens=result_processor.max_tokens
            )
            
            # Парсим JSON ответ от result_processor
            try:
                final_output = json.loads(processor_result["message"])
            except json.JSONDecodeError:
                raise Exception("Result processor returned invalid JSON")
            
            # Возвращаем комбинированный результат
            return {
                "message": json.dumps(final_output, indent=2),
                "model": f"{task_solver.model} + {result_processor.model}",
                "usage": {
                    "task_solver": task_result.get("usage"),
                    "result_processor": processor_result.get("usage")
                },
                "orchestration_steps": [
                    {
                        "step": 1,
                        "agent": "task_solver",
                        "output": task_output
                    },
                    {
                        "step": 2,
                        "agent": "result_processor", 
                        "output": final_output
                    }
                ]
            }
            
        except Exception as e:
            raise Exception(f"Orchestration failed: {str(e)}")
    
    def prepare_messages_for_agent(
        self, 
        agent: Agent, 
        user_message: str,
        conversation_history: List[ChatMessage] = None
    ) -> List[ChatMessage]:
        """Подготавливает сообщения для отправки агенту"""
        messages = []
        
        # Готовим системный промпт с учетом формата ответа
        system_prompt = self._build_system_prompt(agent)
        
        # Добавляем системное сообщение
        if system_prompt:
            messages.append(ChatMessage(
                role=MessageRole.SYSTEM,
                content=system_prompt
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
        """Подготавливает сообщения для отправки агенту"""
        messages = []
        
        # Готовим системный промпт с учетом формата ответа
        system_prompt = self._build_system_prompt(agent)
        
        # Добавляем системное сообщение
        if system_prompt:
            messages.append(ChatMessage(
                role=MessageRole.SYSTEM,
                content=system_prompt
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
    
    def _build_system_prompt(self, agent: Agent) -> str:
        """Строит системный промпт с учетом формата ответа"""
        prompt = agent.system_prompt or ""
        
        if agent.response_format and agent.response_format.type != ResponseFormatType.PLAIN_TEXT:
            format_instruction = self._get_format_instruction(agent.response_format)
            prompt += f"\n\n{format_instruction}"
        
        return prompt
    
    def _get_format_instruction(self, response_format: ResponseFormat) -> str:
        """Генерирует инструкции по формату ответа"""
        if response_format.type == ResponseFormatType.JSON:
            instruction = "ВАЖНО: Отвечай ТОЛЬКО в формате JSON. Не добавляй никаких дополнительных объяснений вне JSON структуры."
            
            if response_format.json_schema:
                instruction += f"\n\nТребуемая JSON схема:\n```json\n{response_format.json_schema}\n```"
            
            if response_format.examples:
                instruction += "\n\nПримеры ответов:"
                for i, example in enumerate(response_format.examples, 1):
                    instruction += f"\n\nПример {i}:\n```json\n{example}\n```"
            
            if response_format.description:
                instruction += f"\n\nОписание формата: {response_format.description}"
                
            return instruction
        
        elif response_format.type == ResponseFormatType.MARKDOWN:
            return "Отвечай в формате Markdown с правильным форматированием заголовков, списков и кода."
        
        elif response_format.type == ResponseFormatType.CODE_BLOCK:
            return "Отвечай в формате блока кода с указанием языка программирования."
        
        return ""


# Глобальный экземпляр сервиса
agent_service = AgentService()