from sqlalchemy import Column, String, Float, Integer, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from app.config import settings

Base = declarative_base()


class AgentDB(Base):
    """Модель агента в базе данных"""
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    model = Column(String, nullable=False, default=settings.ASSISTANT.DEFAULT_MODEL)
    temperature = Column(Float, nullable=False, default=0.7)
    max_tokens = Column(Integer, nullable=False, default=1000)
    
    # Response format fields
    response_format_type = Column(String, nullable=True)  # plain_text, json, markdown, code_block
    response_format_schema = Column(Text, nullable=True)  # JSON schema as text
    response_format_examples = Column(Text, nullable=True)  # Examples as JSON text
    response_format_description = Column(Text, nullable=True)
    
    # Metadata
    is_predefined = Column(Boolean, default=False)  # Предустановленный или созданный пользователем
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Agent(id='{self.id}', name='{self.name}')>"