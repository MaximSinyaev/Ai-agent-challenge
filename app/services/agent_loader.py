from typing import Dict, List
import yaml
import os
from pathlib import Path
from app.models.schemas import Agent, ResponseFormat, ResponseFormatType
from app.config import settings
from datetime import datetime


class AgentLoader:
    """Сервис для загрузки предустановленных агентов из YAML файла"""
    
    def __init__(self, yaml_file_path: str = None):
        if yaml_file_path is None:
            # Путь к файлу с предустановленными агентами
            current_dir = Path(__file__).parent.parent  # поднимаемся на уровень выше (из services в app)
            yaml_file_path = current_dir / "data" / "predefined_agents.yaml"
        
        self.yaml_file_path = Path(yaml_file_path)
    
    def load_agents(self) -> Dict[str, Agent]:
        """Загружает агентов из YAML файла"""
        if not self.yaml_file_path.exists():
            print(f"YAML file not found: {self.yaml_file_path}")
            return {}
        
        try:
            with open(self.yaml_file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            agents = {}
            agents_config = data.get('agents', {})
            
            for agent_key, agent_data in agents_config.items():
                agent = self._create_agent_from_config(agent_data)
                if agent:
                    agents[agent.id] = agent
            
            print(f"Loaded {len(agents)} agents from YAML file")
            return agents
            
        except Exception as e:
            print(f"Error loading agents from YAML: {e}")
            return {}
    
    def _create_agent_from_config(self, config: Dict) -> Agent:
        """Создает объект Agent из конфигурации YAML"""
        try:
            # Обрабатываем response_format
            response_format = None
            if config.get('response_format'):
                response_format = self._parse_response_format(config['response_format'])
            
            agent = Agent(
                id=config['id'],
                name=config['name'],
                description=config['description'],
                system_prompt=config['system_prompt'],
                model=config.get('model') or settings.ASSISTANT.DEFAULT_MODEL,
                temperature=config.get('temperature', 0.7),
                max_tokens=config.get('max_tokens', 1000),
                response_format=response_format,
                created_at=datetime.now().isoformat()
            )
            
            return agent
            
        except Exception as e:
            print(f"Error creating agent from config: {e}")
            return None
    
    def _parse_response_format(self, format_config: Dict) -> ResponseFormat:
        """Парсит конфигурацию формата ответа"""
        try:
            format_type = ResponseFormatType(format_config.get('type', 'plain_text'))
            
            return ResponseFormat(
                type=format_type,
                json_schema=format_config.get('json_schema'),
                examples=format_config.get('examples'),
                description=format_config.get('description')
            )
            
        except Exception as e:
            print(f"Error parsing response format: {e}")
            return None
    
    def save_agents_to_yaml(self, agents: Dict[str, Agent]) -> bool:
        """Сохраняет агентов в YAML файл (для будущего использования)"""
        try:
            # Конвертируем агентов обратно в YAML структуру
            yaml_data = {
                'agents': {}
            }
            
            for agent_id, agent in agents.items():
                agent_config = {
                    'id': agent.id,
                    'name': agent.name,
                    'description': agent.description,
                    'system_prompt': agent.system_prompt,
                    'model': agent.model,
                    'temperature': agent.temperature,
                    'max_tokens': agent.max_tokens
                }
                
                if agent.response_format:
                    agent_config['response_format'] = {
                        'type': agent.response_format.type.value,
                        'json_schema': agent.response_format.json_schema,
                        'examples': agent.response_format.examples,
                        'description': agent.response_format.description
                    }
                else:
                    agent_config['response_format'] = None
                
                yaml_data['agents'][agent_id] = agent_config
            
            with open(self.yaml_file_path, 'w', encoding='utf-8') as file:
                yaml.dump(yaml_data, file, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving agents to YAML: {e}")
            return False


# Глобальный экземпляр загрузчика
agent_loader = AgentLoader()