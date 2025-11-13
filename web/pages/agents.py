import streamlit as st
from typing import List, Dict, Any, Optional
import json
import time
import sys
from pathlib import Path

# Добавляем путь к родительской директории для импорта модулей
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from web.models.schemas import ResponseFormatType, ResponseFormat
except ImportError:
    # Если импорт не удался, создаем enum-подобные константы
    class ResponseFormatType:
        PLAIN_TEXT = "plain_text"
        JSON = "json"
        MARKDOWN = "markdown"
        CODE_BLOCK = "code_block"

# Инициализация состояния сессии для страницы
def init_page_session():
    """Инициализация состояния сессии для страницы агентов"""
    if 'api_client' not in st.session_state:
        try:
            from web.utils.api_client import APIClient
            from web.utils.config import WebConfig
            config = WebConfig()
            st.session_state.api_client = APIClient(config.backend_url, api_version="v1")
        except ImportError as e:
            st.error(f"Ошибка импорта: {e}")
            st.stop()
    
    if 'current_agent' not in st.session_state:
        st.session_state.current_agent = "default"

# Основная функция страницы
st.set_page_config(page_title="🤖 Агенты", page_icon="🤖", layout="wide")

init_page_session()

st.header("🤖 Управление агентами")

# Вкладки для разных функций
tab1, tab2, tab3, tab4 = st.tabs(["📋 Список агентов", "➕ Создать агента", "🗑️ Удалить агента", "📦 Импорт/Экспорт"])

# Вкладка со списком агентов
with tab1:
    st.subheader("📋 Все агенты в системе")
    
    try:
        agents = st.session_state.api_client.get_agents()
        
        if agents:
            for i, agent in enumerate(agents):
                with st.expander(f"🤖 {agent['name']} ({agent['id']})", expanded=(i == 0)):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**ID:** {agent['id']}")
                        st.write(f"**Имя:** {agent['name']}")
                        st.write(f"**Описание:** {agent.get('description', 'Нет описания')}")
                        
                        if agent.get('system_prompt'):
                            st.write("**Системный промпт:**")
                            st.code(agent['system_prompt'], language="text")
                    
                    with col2:
                        st.write(f"**Модель:** {agent.get('model', 'По умолчанию')}")
                        st.write(f"**Температура:** {agent.get('temperature', 'По умолчанию')}")
                        st.write(f"**Макс. токены:** {agent.get('max_tokens', 'По умолчанию')}")
                        
                        # Формат ответа
                        if agent.get('response_format'):
                            rf = agent['response_format']
                            st.write(f"**Формат:** {rf.get('type', 'plain_text')}")
                            if rf.get('description'):
                                st.write(f"**Описание формата:** {rf['description']}")
                        
                        # Кнопка выбора агента
                        if st.button(f"🎯 Выбрать", key=f"select_main_{agent['id']}"):
                            st.session_state.current_agent = agent['id']
                            st.success(f"✅ Выбран агент: {agent['name']}")
                            st.rerun()
                            
            # Статистика агентов
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            
            total_agents = len(agents)
            custom_agents = len([a for a in agents if a['id'] != 'default'])
            default_agents = total_agents - custom_agents
            
            with col1:
                st.metric("Всего агентов", total_agents)
            with col2:
                st.metric("Пользовательских", custom_agents)
            with col3:
                st.metric("По умолчанию", default_agents)
                
        else:
            st.info("📭 Агенты не найдены")
            st.markdown("""
            ### � Начните с создания агента
            1. Перейдите на вкладку "➕ Создать агента"
            2. Заполните форму создания
            3. Протестируйте агента в чате
            """)
            
    except Exception as e:
        st.error(f"❌ Ошибка загрузки агентов: {e}")
        st.markdown("### 🔧 Возможные решения")
        st.markdown("""
        - Убедитесь, что backend сервер запущен на порту 8000
        - Проверьте соединение с сервером
        - Попробуйте обновить страницу
        """)

# Вкладка создания агента
with tab2:
    st.subheader("➕ Создание нового агента")
    
    with st.form("create_agent_form"):
        # Основная информация
        st.markdown("### 📝 Основная информация")
        
        name = st.text_input(
            "Имя агента*:",
            placeholder="Например: Python Expert",
            help="Дружественное имя агента"
        )
        
        description = st.text_area(
            "Описание:",
            placeholder="Краткое описание назначения агента",
            help="Опциональное описание функций агента"
        )
        
        # Системный промпт
        st.markdown("### 🎯 Поведение агента")
        
        system_prompt = st.text_area(
            "Системный промпт*:",
            placeholder="Ты опытный Python разработчик. Помогай с кодом, объясняй лучшие практики...",
            height=150,
            help="Инструкции, определяющие поведение и стиль агента"
        )
        
        # Параметры модели
        st.markdown("### ⚙️ Параметры модели")
        
        col1, col2 = st.columns(2)
        
        with col1:
            temperature = st.slider(
                "Температура:",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="Контролирует творческость ответов"
            )
        
        with col2:
            max_tokens = st.number_input(
                "Макс. токены:",
                min_value=50,
                max_value=4000,
                value=1000,
                step=50,
                help="Максимальная длина ответа"
            )
        
        # Формат ответа
        st.markdown("### 📄 Формат ответа")
        
        response_format_type = st.selectbox(
            "Тип формата:",
            options=["plain_text", "json", "markdown", "code_block"],
            format_func=lambda x: {
                "plain_text": "🔤 Обычный текст",
                "json": "📋 JSON структура", 
                "markdown": "📝 Markdown",
                "code_block": "💻 Блок кода"
            }.get(x, x),
            help="Выберите формат ответов агента"
        )
        
        response_format_description = None
        response_format_schema = None
        response_format_examples = None
        
        if response_format_type == "json":
            st.markdown("#### JSON конфигурация")
            
            response_format_description = st.text_input(
                "Описание формата:",
                placeholder="Например: Структурированный ответ для математических задач"
            )
            
            schema_json = st.text_area(
                "JSON Schema (опционально):",
                placeholder='{"type": "object", "properties": {...}}',
                help="Схема для валидации JSON ответов",
                height=100
            )
            
            if schema_json.strip():
                try:
                    response_format_schema = json.loads(schema_json)
                except json.JSONDecodeError as e:
                    st.error(f"❌ Ошибка в JSON Schema: {e}")
            
            examples_text = st.text_area(
                "Примеры ответов (один на строку):",
                placeholder='{"result": "42", "explanation": "Ответ на главный вопрос"}',
                help="Примеры ожидаемых JSON ответов",
                height=100
            )
            
            if examples_text.strip():
                response_format_examples = [line.strip() for line in examples_text.split('\n') if line.strip()]
        
        # Кнопка отправки
        submit_button = st.form_submit_button(
            "� Создать агента",
            width="content",
            type="primary"
        )
        
        if submit_button:
            if not name.strip():
                st.error("❌ Имя агента обязательно")
            elif not system_prompt.strip():
                st.error("❌ Системный промпт обязателен")
            else:
                try:
                    # Создаем конфигурацию агента
                    config = {
                        "name": name.strip(),
                        "description": description.strip() or None,
                        "system_prompt": system_prompt.strip(),
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                    
                    # Добавляем формат ответа если не plain_text
                    if response_format_type != "plain_text":
                        response_format_config = {
                            "type": response_format_type
                        }
                        
                        if response_format_description:
                            response_format_config["description"] = response_format_description
                        
                        if response_format_schema:
                            response_format_config["json_schema"] = response_format_schema
                            
                        if response_format_examples:
                            response_format_config["examples"] = response_format_examples
                        
                        config["response_format"] = response_format_config
                    
                    # Отправляем запрос
                    with st.spinner("🔄 Создание агента..."):
                        response = st.session_state.api_client.create_agent(config)
                    
                    st.success(f"✅ Агент '{name}' успешно создан!")
                    st.json(response)
                    
                    # Обновляем кеш агентов
                    st.cache_data.clear()
                    
                except Exception as e:
                    st.error(f"❌ Ошибка создания агента: {e}")

# Вкладка удаления агента
with tab3:
    st.subheader("🗑️ Удаление агента")
    
    st.warning("⚠️ **Внимание!** Удаление агента необратимо.")
    
    try:
        agents = st.session_state.api_client.get_agents()
        
        if agents:
            # Фильтруем агентов (нельзя удалять default агента)
            deletable_agents = [agent for agent in agents if agent['id'] != 'default']
            
            if deletable_agents:
                agent_options = {agent['id']: f"{agent['name']} ({agent['id']})" for agent in deletable_agents}
                
                selected_agent_id = st.selectbox(
                    "Выберите агента для удаления:",
                    options=list(agent_options.keys()),
                    format_func=lambda x: agent_options[x]
                )
                
                # Показываем информацию о выбранном агенте
                selected_agent = next(agent for agent in deletable_agents if agent['id'] == selected_agent_id)
                
                with st.expander("ℹ️ Информация об агенте", expanded=True):
                    st.write(f"**ID:** {selected_agent['id']}")
                    st.write(f"**Имя:** {selected_agent['name']}")
                    st.write(f"**Описание:** {selected_agent.get('description', 'Нет описания')}")
                
                # Подтверждение удаления
                col1, col2 = st.columns(2)
                
                with col1:
                    confirm_text = st.text_input(
                        f"Для подтверждения введите ID агента ({selected_agent_id}):",
                        placeholder=selected_agent_id
                    )
                
                with col2:
                    st.write("")  # Пустое место для выравнивания
                    delete_button = st.button(
                        "🗑️ Удалить агента",
                        type="primary",
                        disabled=(confirm_text != selected_agent_id),
                        width="content"
                    )
                
                if delete_button and confirm_text == selected_agent_id:
                    try:
                        with st.spinner("🔄 Удаление агента..."):
                            response = st.session_state.api_client.delete_agent(selected_agent_id)
                        
                        st.success(f"✅ Агент '{selected_agent['name']}' успешно удален!")
                        
                        # Если удаляем текущего агента, переключаемся на default
                        if st.session_state.current_agent == selected_agent_id:
                            st.session_state.current_agent = "default"
                            st.info("🔄 Переключился на агента по умолчанию")
                        
                        # Обновляем кеш агентов
                        st.cache_data.clear()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Ошибка удаления агента: {e}")
            else:
                st.info("📭 Нет агентов, доступных для удаления (кроме default)")
        else:
            st.info("📭 Агенты не найдены")
            
    except Exception as e:
        st.error(f"❌ Ошибка загрузки агентов: {e}")

# Вкладка импорта/экспорта
with tab4:
    st.subheader("📦 Импорт/Экспорт агентов")
    
    col1, col2 = st.columns(2)
    
    # Экспорт
    with col1:
        st.markdown("### � Экспорт")
        try:
            agents = st.session_state.api_client.get_agents()
            if agents:
                export_data = {"agents": agents, "exported_at": time.time()}
                
                st.download_button(
                    "💾 Скачать все агенты (JSON)",
                    data=json.dumps(export_data, indent=2, ensure_ascii=False),
                    file_name=f"agents_export_{int(time.time())}.json",
                    mime="application/json",
                    width="content"
                )
            else:
                st.info("Нет агентов для экспорта")
        except Exception as e:
            st.error(f"Ошибка экспорта: {e}")
    
    # Импорт
    with col2:
        st.markdown("### 📥 Импорт")
        st.info("� Функция импорта будет добавлена в следующих версиях")
        
        # Заглушка для будущего функционала
        uploaded_file = st.file_uploader(
            "Выберите JSON файл с агентами:",
            type=['json'],
            disabled=True,
            help="Функция временно недоступна"
        )