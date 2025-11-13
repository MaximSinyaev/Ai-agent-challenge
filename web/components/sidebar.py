import streamlit as st

def render_sidebar():
    """Render sidebar with navigation and settings"""
    
    st.header("🎛️ Панель управления")
    # NOTE: Навигация в верхнем блоке (App / Models / Settings / Statistics). Убираем дублирование здесь.
    
    # Connection information
    with st.expander("🔗 Соединение", expanded=False):
        try:
            health = st.session_state.api_client.health_check()
            st.success(f"✅ Подключено к: {health.get('service', 'Unknown')}")
            st.info(f"📝 Версия: {health.get('version', 'Unknown')}")
            if health.get('openrouter_configured'):
                st.success("🌐 OpenRouter настроен")
            else:
                st.warning("⚠️ OpenRouter не настроен")
        except Exception as e:
            st.error(f"❌ Ошибка соединения: {e}")
    
    # Agent selection
    st.subheader("🤖 Текущий агент")
    
    try:
        agents = st.session_state.api_client.get_agents()
        st.session_state.agents_list = agents
        
        if agents:
            agent_options = {agent['id']: f"{agent['name']}" for agent in agents}
            selected_agent = st.selectbox(
                "Выберите агента:",
                options=list(agent_options.keys()),
                format_func=lambda x: agent_options[x],
                index=0 if st.session_state.current_agent not in agent_options else list(agent_options.keys()).index(st.session_state.current_agent)
            )
            st.session_state.current_agent = selected_agent
            
            # Selected agent information
            current_agent_info = next((agent for agent in agents if agent['id'] == selected_agent), None)
            if current_agent_info:
                with st.expander("ℹ️ Информация об агенте", expanded=False):
                    st.write(f"**Имя:** {current_agent_info['name']}")
                    st.write(f"**Описание:** {current_agent_info.get('description', 'Нет описания')}")
                    st.write(f"**Модель:** {current_agent_info.get('model', 'По умолчанию')}")
        else:
            st.warning("⚠️ Агенты не найдены")
            
    except Exception as e:
        st.error(f"❌ Ошибка загрузки агентов: {e}")
    
    # Управление агентами (показываем только если выбрана соответствующая страница)
    if st.session_state.current_page == "agents":
        st.divider()
        render_agent_management()
    
    # Model settings
    st.subheader("🎛️ Параметры модели")
    
    # Temperature
    temperature = st.slider(
        "🌡️ Температура:",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Контролирует творческость ответов. Меньше = предсказуемее, больше = креативнее"
    )
    st.session_state.temperature = temperature
    
    # Maximum tokens
    max_tokens = st.slider(
        "📝 Макс. токены:",
        min_value=50,
        max_value=4000,
        value=st.session_state.max_tokens,
        step=50,
        help="Максимальная длина ответа"
    )
    st.session_state.max_tokens = max_tokens
    
    # Выбор модели (опционально)
    with st.expander("🎯 Кастомная модель", expanded=False):
        try:
            models = st.session_state.api_client.get_models()
            if models:
                model_options = ["По умолчанию"] + [model.get('id', str(model)) for model in models[:20]]  # Ограничиваем количество
                selected_model_idx = st.selectbox(
                    "Модель:",
                    options=range(len(model_options)),
                    format_func=lambda x: model_options[x],
                    index=0
                )
                
                if selected_model_idx == 0:
                    st.session_state.selected_model = None
                else:
                    st.session_state.selected_model = model_options[selected_model_idx]
            else:
                st.info("Модели не загружены")
        except Exception as e:
            st.error(f"Ошибка загрузки моделей: {e}")
    
    # Действия
    st.subheader("⚡ Действия")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Очистить чат", width="content", help="Удалить все сообщения из текущего чата"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🔄 Обновить данные", width="content", help="Обновить список агентов и модулей"):
            # Очищаем кеш
            st.cache_data.clear()
            st.rerun()
    
    # Информация о сессии
    with st.expander("📊 Статистика сессии", expanded=False):
        st.write(f"**Сообщений в чате:** {len(st.session_state.messages)}")
        st.write(f"**Текущая температура:** {st.session_state.temperature}")
        st.write(f"**Макс. токены:** {st.session_state.max_tokens}")
        if st.session_state.selected_model:
            st.write(f"**Выбранная модель:** {st.session_state.selected_model}")
        else:
            st.write("**Модель:** По умолчанию")

def render_agent_management():
    """Рендер компактного управления агентами в sidebar"""
    
    st.subheader("🛠️ Управление агентами")
    
    # Вкладки для управления
    tab1, tab2 = st.tabs(["➕ Создать", "🗑️ Удалить"])
    
    with tab1:
        render_create_agent_compact()
    
    with tab2:
        render_delete_agent_compact()

def render_create_agent_compact():
    """Компактная форма создания агента"""
    
    with st.form("create_agent_compact"):
        st.markdown("**Новый агент**")
        
        name = st.text_input("Имя*:", placeholder="Python Expert")
        description = st.text_area("Описание:", placeholder="Краткое описание", height=60)
        system_prompt = st.text_area("Системный промпт*:", 
                                   placeholder="Ты опытный разработчик...", 
                                   height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider("Температура:", 0.0, 2.0, 0.7, 0.1)
        with col2:
            max_tokens = st.number_input("Токены:", 50, 4000, 1000, 50)
        
        submit = st.form_submit_button("🚀 Создать", width="content")
        
        if submit and name.strip() and system_prompt.strip():
            try:
                config = {
                    "name": name.strip(),
                    "description": description.strip() or None,
                    "system_prompt": system_prompt.strip(),
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                with st.spinner("Создание..."):
                    response = st.session_state.api_client.create_agent(config)
                
                st.success(f"✅ Агент '{name}' создан!")
                st.cache_data.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Ошибка: {e}")
        elif submit:
            st.error("❌ Заполните обязательные поля")

def render_delete_agent_compact():
    """Компактная форма удаления агента"""
    
    try:
        agents = st.session_state.api_client.get_agents()
        deletable_agents = [agent for agent in agents if agent['id'] != 'default']
        
        if deletable_agents:
            agent_options = {agent['id']: f"{agent['name']}" for agent in deletable_agents}
            
            selected_agent_id = st.selectbox(
                "Агент для удаления:",
                options=list(agent_options.keys()),
                format_func=lambda x: f"🗑️ {agent_options[x]}"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                confirm = st.text_input("Введите ID:", placeholder=selected_agent_id)
            
            with col2:
                st.write("")  # Отступ
                if st.button("🗑️ Удалить", 
                           disabled=(confirm != selected_agent_id),
                           width="content"):
                    try:
                        st.session_state.api_client.delete_agent(selected_agent_id)
                        
                        if st.session_state.current_agent == selected_agent_id:
                            st.session_state.current_agent = "default"
                        
                        st.success("✅ Агент удален!")
                        st.cache_data.clear()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Ошибка: {e}")
        else:
            st.info("📭 Нет агентов для удаления")
            
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")