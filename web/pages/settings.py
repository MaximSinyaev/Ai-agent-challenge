import streamlit as st
import json
from typing import Dict, Any

def render_settings_page():
    """Application settings page"""
    
    st.set_page_config(
        page_title="Settings - AI Agent Interface", 
        page_icon="⚙️",
        layout="wide"
    )
    
    st.title("Settings")
    st.markdown("---")
    
    # Инициализация API клиента
    try:
        from web.utils.api_client import APIClient
        from web.utils.config import WebConfig
        
        config = WebConfig()
        api_client = APIClient(config.backend_url)
        
    except Exception as e:
        st.error(f"❌ Ошибка инициализации: {e}")
        st.stop()
    
    # Settings tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Connection", "Interface", "AI Models", "Data"])
    
    # Connection settings
    with tab1:
        st.header("Connection Settings")
        
        # Текущие настройки
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Текущие настройки")
            st.code(f"""
Backend URL: {config.backend_url}
Локальный backend: {config.is_backend_local}
Таймаут кеширования: {config.cache_ttl_agents}с (агенты)
Таймаут кеширования: {config.cache_ttl_models}с (модели)
            """)
        
        with col2:
            st.subheader("🔍 Проверка подключения")
            
            if st.button("🔄 Проверить подключение", use_container_width=True):
                with st.spinner("Проверяем подключение..."):
                    try:
                        health = api_client.health_check()
                        st.success("✅ Подключение успешно!")
                        st.json(health)
                    except Exception as e:
                        st.error(f"❌ Ошибка подключения: {e}")
        
        # Изменение URL backend
        st.markdown("---")
        st.subheader("🔧 Изменить Backend URL")
        
        new_backend_url = st.text_input(
            "Backend URL:",
            value=config.backend_url,
            help="URL backend сервера (например: http://localhost:8000)"
        )
        
        if st.button("💾 Сохранить URL"):
            # В реальном приложении здесь бы мы сохраняли в настройки
            st.success("✅ URL сохранен (перезапустите приложение для применения)")
    
    # Настройки интерфейса
    with tab2:
        st.header("🎛️ Настройки интерфейса")
        
        # Тема (заглушка)
        st.subheader("🎨 Оформление")
        theme = st.selectbox(
            "Тема:",
            ["Auto", "Light", "Dark"],
            help="Тема оформления (управляется Streamlit)"
        )
        
        # Настройки чата
        st.subheader("💬 Настройки чата")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_history = st.number_input(
                "Макс. сообщений в истории:",
                min_value=10,
                max_value=200,
                value=config.max_history_length,
                help="Максимальное количество сообщений для хранения"
            )
        
        with col2:
            auto_scroll = st.checkbox(
                "Автопрокрутка чата",
                value=True,
                help="Автоматически прокручивать к новым сообщениям"
            )
        
        # Экспериментальные функции
        st.subheader("🧪 Экспериментальные функции")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_voice = st.checkbox(
                "Голосовой ввод",
                value=False,
                disabled=True,
                help="Функция в разработке"
            )
        
        with col2:
            enable_images = st.checkbox(
                "Поддержка изображений", 
                value=False,
                disabled=True,
                help="Функция в разработке"
            )
    
    # Настройки AI моделей
    with tab3:
        st.header("🤖 Настройки AI моделей")
        
        # Параметры по умолчанию
        st.subheader("🎯 Параметры по умолчанию")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            default_temperature = st.slider(
                "Температура по умолчанию:",
                min_value=0.0,
                max_value=2.0,
                value=config.default_temperature,
                step=0.1
            )
        
        with col2:
            default_max_tokens = st.number_input(
                "Макс. токены по умолчанию:",
                min_value=50,
                max_value=4000,
                value=config.default_max_tokens
            )
        
        with col3:
            timeout = st.number_input(
                "Таймаут запроса (сек):",
                min_value=5,
                max_value=120,
                value=30
            )
        
        # Доступные модели
        st.subheader("📋 Доступные модели")
        
        try:
            models = api_client.get_models()
            if models:
                st.success(f"✅ Доступно {len(models)} моделей")
                
                # Показываем первые несколько моделей
                for model in models[:5]:
                    with st.expander(f"🤖 {model.get('name', model.get('id'))}", expanded=False):
                        st.json(model)
                
                if len(models) > 5:
                    st.info(f"... и еще {len(models) - 5} моделей. Полный список доступен на странице 'Модели'")
            else:
                st.warning("⚠️ Модели не найдены")
        except Exception as e:
            st.error(f"❌ Ошибка загрузки моделей: {e}")
    
    # Управление данными
    with tab4:
        st.header("📊 Управление данными")
        
        # Статистика
        st.subheader("📈 Статистика")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Подсчет сообщений в текущей сессии
            message_count = len(st.session_state.get('messages', []))
            st.metric("Сообщений в сессии", message_count)
        
        with col2:
            # Подсчет агентов
            try:
                agents = api_client.get_agents()
                agent_count = len(agents) if agents else 0
            except:
                agent_count = 0
            st.metric("Всего агентов", agent_count)
        
        with col3:
            st.metric("Размер кеша", "N/A")
        
        with col4:
            st.metric("Время работы", "N/A")
        
        # Очистка данных
        st.subheader("🗑️ Очистка данных")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Очистить историю чата", type="secondary", use_container_width=True):
                if 'messages' in st.session_state:
                    st.session_state.messages = []
                st.success("✅ История чата очищена")
                st.rerun()
        
        with col2:
            if st.button("🔄 Очистить кеш", type="secondary", use_container_width=True):
                st.cache_data.clear()
                st.success("✅ Кеш очищен")
                st.rerun()
        
        # Экспорт данных
        st.subheader("📥 Экспорт данных")
        
        export_data = {
            "session_messages": st.session_state.get('messages', []),
            "current_agent": st.session_state.get('current_agent', 'default'),
            "settings": {
                "temperature": st.session_state.get('temperature', 0.7),
                "max_tokens": st.session_state.get('max_tokens', 1000)
            }
        }
        
        st.download_button(
            "💾 Скачать данные сессии (JSON)",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name=f"session_export_{int(st.session_state.get('session_start', 0))}.json",
            mime="application/json",
            use_container_width=True
        )

if __name__ == "__main__":
    render_settings_page()