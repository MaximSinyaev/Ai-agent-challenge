import streamlit as st
from typing import Dict, Any
import time
import sys
from pathlib import Path

# Добавляем путь к родительской директории для импорта модулей
sys.path.append(str(Path(__file__).parent.parent.parent))

# Page configuration
st.set_page_config(page_title="📊 Статистика", page_icon="📊", layout="wide")

# Инициализация состояния сессии для страницы
def init_page_session():
    """Инициализация состояния сессии для страницы статистики"""
    if 'api_client' not in st.session_state:
        try:
            from web.utils.api_client import APIClient
            from web.utils.config import WebConfig
            config = WebConfig()
            st.session_state.api_client = APIClient(config.backend_url, api_version="v1")
        except ImportError as e:
            st.error(f"Ошибка импорта: {e}")
            st.stop()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'current_agent' not in st.session_state:
        st.session_state.current_agent = "default"
    
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    
    if 'max_tokens' not in st.session_state:
        st.session_state.max_tokens = 1000
    
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None

init_page_session()

def render_stats_page():
    """Render statistics page"""
    st.header("📊 Usage Statistics")
    
    # Main statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💬 Messages", len(st.session_state.messages))
    
    with col2:
        try:
            agents_count = len(st.session_state.api_client.get_agents())
            st.metric("🤖 Agents", agents_count)
        except:
            st.metric("🤖 Agents", "—")
    
    with col3:
        st.metric("🌡️ Temperature", f"{st.session_state.temperature}")
    
    with col4:
        st.metric("📝 Max tokens", st.session_state.max_tokens)
    
    st.divider()
    
    # Информация о сессии
    st.subheader("🔧 Настройки сессии")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Текущий агент:** {st.session_state.current_agent}")
        if st.session_state.selected_model:
            st.write(f"**Выбранная модель:** {st.session_state.selected_model}")
        else:
            st.write(f"**Модель:** По умолчанию")
        
        # Информация о времени сессии
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = time.time()
        
        session_duration = time.time() - st.session_state.session_start_time
        hours = int(session_duration // 3600)
        minutes = int((session_duration % 3600) // 60)
        st.write(f"**Время сессии:** {hours:02d}:{minutes:02d}")
    
    with col2:
        try:
            health = st.session_state.api_client.health_check()
            st.write(f"**Статус backend:** ✅ Подключен")
            st.write(f"**Версия:** {health.get('version', 'Unknown')}")
            if health.get('openrouter_configured'):
                st.write(f"**OpenRouter:** ✅ Настроен")
            else:
                st.write(f"**OpenRouter:** ⚠️ Не настроен")
        except Exception as e:
            st.write(f"**Статус backend:** ❌ Ошибка")
            st.write(f"**Ошибка:** {str(e)[:50]}...")
    
    # История сообщений
    if st.session_state.messages:
        st.divider()
        st.subheader("📈 Аналитика чата")
        
        # Подсчет типов сообщений
        user_messages = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
        assistant_messages = len([msg for msg in st.session_state.messages if msg["role"] == "assistant"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👤 Сообщения пользователя", user_messages)
        with col2:
            st.metric("🤖 Ответы агента", assistant_messages)
        with col3:
            if user_messages > 0:
                response_rate = (assistant_messages / user_messages) * 100
                st.metric("📊 Процент ответов", f"{response_rate:.1f}%")
            else:
                st.metric("📊 Процент ответов", "0%")
        
        # Анализ длины сообщений
        if st.session_state.messages:
            user_msg_lengths = [len(msg['content']) for msg in st.session_state.messages if msg['role'] == 'user']
            assistant_msg_lengths = [len(msg['content']) for msg in st.session_state.messages if msg['role'] == 'assistant']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📏 Средняя длина сообщений")
                if user_msg_lengths:
                    avg_user_length = sum(user_msg_lengths) / len(user_msg_lengths)
                    st.write(f"👤 Пользователь: {avg_user_length:.0f} символов")
                if assistant_msg_lengths:
                    avg_assistant_length = sum(assistant_msg_lengths) / len(assistant_msg_lengths)
                    st.write(f"🤖 Агент: {avg_assistant_length:.0f} символов")
            
            with col2:
                st.markdown("#### 📊 Общая статистика")
                total_chars_user = sum(user_msg_lengths) if user_msg_lengths else 0
                total_chars_assistant = sum(assistant_msg_lengths) if assistant_msg_lengths else 0
                st.write(f"📝 Всего символов: {total_chars_user + total_chars_assistant}")
                st.write(f"📄 Всего сообщений: {len(st.session_state.messages)}")
        
        # Последние сообщения
        with st.expander("📝 Последние сообщения", expanded=False):
            for i, msg in enumerate(st.session_state.messages[-5:], 1):  # Показываем последние 5 сообщений
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                content_preview = msg['content'][:100] + ('...' if len(msg['content']) > 100 else '')
                st.write(f"**{i}.** {role_icon} **{msg['role'].title()}:** {content_preview}")
    
    else:
        st.divider()
        st.info("💬 Пока нет сообщений в чате")
        
        st.markdown("### 🚀 Начните общение")
        st.markdown("""
        Чтобы увидеть статистику:
        1. Перейдите на вкладку "💬 Чат"
        2. Выберите агента в боковой панели  
        3. Напишите сообщение
        4. Вернитесь сюда для просмотра статистики
        """)
    
    # Дополнительные возможности
    st.divider()
    st.subheader("🛠️ Дополнительные функции")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Экспорт истории чата", width="content"):
            if st.session_state.messages:
                chat_data = {
                    "messages": st.session_state.messages,
                    "agent": st.session_state.current_agent,
                    "temperature": st.session_state.temperature,
                    "max_tokens": st.session_state.max_tokens,
                    "exported_at": time.time()
                }
                
                import json
                json_str = json.dumps(chat_data, ensure_ascii=False, indent=2)
                
                st.download_button(
                    label="💾 Скачать JSON",
                    data=json_str,
                    file_name=f"chat_history_{int(time.time())}.json",
                    mime="application/json",
                    width="content"
                )
            else:
                st.warning("История чата пуста")
    
    with col2:
        if st.button("🧹 Сбросить статистику", width="content"):
            if st.button("⚠️ Подтвердить сброс", width="content"):
                st.session_state.messages = []
                if 'session_start_time' in st.session_state:
                    del st.session_state.session_start_time
                st.success("✅ Статистика сброшена")
                st.rerun()
            
# Запуск страницы
render_stats_page()