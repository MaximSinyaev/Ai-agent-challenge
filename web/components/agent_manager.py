import streamlit as st
from typing import Dict, Any
import json
import time

def render_agent_manager():
    """Рендер интерфейса управления агентами"""
    
    st.header("🔧 Управление агентами")
    
    # Вкладки для разных функций
    tab1, tab2, tab3 = st.tabs(["📋 Список агентов", "➕ Создать агента", "🗑️ Удалить агента"])
    
    # Вкладка со списком агентов
    with tab1:
        render_agents_list()
    
    # Вкладка создания агента
    with tab2:
        render_create_agent()
    
    # Вкладка удаления агента
    with tab3:
        render_delete_agent()

def render_agents_list():
    """Рендер списка агентов"""
    st.subheader("📋 Текущие агенты")
    
    try:
        agents = st.session_state.api_client.get_agents()
        
        if agents:
            for agent in agents:
                with st.expander(f"🤖 {agent['name']} ({agent['id']})", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID:** {agent['id']}")
                        st.write(f"**Имя:** {agent['name']}")
                        st.write(f"**Описание:** {agent.get('description', 'Нет описания')}")
                    
                    with col2:
                        st.write(f"**Модель:** {agent.get('model', 'По умолчанию')}")
                        st.write(f"**Температура:** {agent.get('temperature', 'По умолчанию')}")
                        st.write(f"**Макс. токены:** {agent.get('max_tokens', 'По умолчанию')}")
                    
                    # Системный промпт
                    if agent.get('system_prompt'):
                        st.write("**Системный промпт:**")
                        st.code(agent['system_prompt'], language="text")
                    
                    # Кнопка для выбора агента
                    if st.button(f"🎯 Выбрать агента", key=f"select_{agent['id']}"):
                        st.session_state.current_agent = agent['id']
                        st.success(f"✅ Выбран агент: {agent['name']}")
                        st.rerun()
        else:
            st.info("📭 Агенты не найдены")
            
    except Exception as e:
        st.error(f"❌ Ошибка загрузки агентов: {e}")

def render_create_agent():
    """Рендер формы создания агента"""
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
        
        # Кнопка отправки
        submit_button = st.form_submit_button(
            "🚀 Создать агента",
            use_container_width=True,
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
                    
                    # Отправляем запрос
                    with st.spinner("🔄 Создание агента..."):
                        response = st.session_state.api_client.create_agent(config)
                    
                    st.success(f"✅ Агент '{name}' успешно создан!")
                    st.json(response)
                    
                    # Обновляем кеш агентов
                    st.cache_data.clear()
                    
                except Exception as e:
                    st.error(f"❌ Ошибка создания агента: {e}")

def render_delete_agent():
    """Рендер формы удаления агента"""
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
                        use_container_width=True
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

def render_agent_import_export():
    """Рендер функций импорта/экспорта агентов"""
    st.subheader("📦 Импорт/Экспорт агентов")
    
    col1, col2 = st.columns(2)
    
    # Экспорт
    with col1:
        st.markdown("### 📤 Экспорт")
        try:
            agents = st.session_state.api_client.get_agents()
            if agents:
                export_data = {"agents": agents, "exported_at": time.time()}
                
                st.download_button(
                    "💾 Скачать все агенты (JSON)",
                    data=json.dumps(export_data, indent=2, ensure_ascii=False),
                    file_name=f"agents_export_{int(time.time())}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.info("Нет агентов для экспорта")
        except Exception as e:
            st.error(f"Ошибка экспорта: {e}")
    
    # Импорт
    with col2:
        st.markdown("### 📥 Импорт")
        st.info("🚧 Функция импорта будет добавлена в следующих версиях")
        
        # Заглушка для будущего функционала
        uploaded_file = st.file_uploader(
            "Выберите JSON файл с агентами:",
            type=['json'],
            disabled=True,
            help="Функция временно недоступна"
        )