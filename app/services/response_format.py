from typing import Dict, Any, Optional, Tuple
import json
import re
from jsonschema import validate, ValidationError
from app.models.schemas import ResponseFormat, ResponseFormatType


class ResponseFormatService:
    """Сервис для обработки и валидации форматов ответов"""
    
    @staticmethod
    def parse_response(response: str, response_format: Optional[ResponseFormat]) -> Tuple[Any, bool]:
        """
        Парсит ответ согласно указанному формату
        
        Returns:
            Tuple[parsed_data, is_valid]: Распарсенные данные и флаг валидности
        """
        if not response_format or response_format.type == ResponseFormatType.PLAIN_TEXT:
            return response, True
        
        if response_format.type == ResponseFormatType.JSON:
            return ResponseFormatService._parse_json_response(response, response_format)
        
        # Для других форматов пока возвращаем как есть
        return response, True
    
    @staticmethod
    def _parse_json_response(response: str, response_format: ResponseFormat) -> Tuple[Any, bool]:
        """Парсит JSON ответ"""
        try:
            # Попытка извлечь JSON из ответа (на случай если есть дополнительный текст)
            json_content = ResponseFormatService._extract_json_from_text(response)
            
            if not json_content:
                return response, False
            
            parsed_data = json.loads(json_content)
            
            # Валидация по схеме если она указана
            if response_format.json_schema:
                try:
                    validate(instance=parsed_data, schema=response_format.json_schema)
                    return parsed_data, True
                except ValidationError as e:
                    print(f"JSON schema validation error: {e}")
                    return parsed_data, False
            
            return parsed_data, True
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return response, False
    
    @staticmethod
    def _extract_json_from_text(text: str) -> Optional[str]:
        """Извлекает JSON из текста (на случай если AI добавил дополнительные объяснения)"""
        # Попытка найти JSON блок в markdown
        json_block_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        
        # Попытка найти JSON объект в тексте
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            # Берем самый большой найденный JSON объект
            return max(matches, key=len)
        
        # Если не найден блок, возвращаем весь текст (возможно это чистый JSON)
        text = text.strip()
        if text.startswith('{') and text.endswith('}'):
            return text
            
        return None
    
    @staticmethod
    def validate_schema(schema: Dict[str, Any]) -> bool:
        """Проверяет валидность JSON Schema"""
        try:
            # Простая проверка что это похоже на JSON Schema
            if not isinstance(schema, dict):
                return False
            
            # Проверим что есть базовые поля
            if 'type' not in schema and 'properties' not in schema:
                return False
                
            return True
        except Exception:
            return False


# Глобальный экземпляр сервиса
response_format_service = ResponseFormatService()