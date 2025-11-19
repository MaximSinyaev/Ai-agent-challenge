import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict
import time
import sys
from pathlib import Path

# Добавляем путь к родительской директории для импорта модулей
sys.path.append(str(Path(__file__).parent.parent.parent))

# Page configuration
st.set_page_config(page_title="🔧 Модели", page_icon="🔧", layout="wide")

def render_models_page():
    """Available models page"""
    
    st.title("Available Models")
    
    # Показываем текущую выбранную модель
    if hasattr(st.session_state, 'selected_model') and st.session_state.selected_model:
        st.info(f"🎯 Текущая модель: **{st.session_state.selected_model}**")
    else:
        st.info("🎯 Текущая модель: **Default**")
    
    st.markdown("---")
    
    # Загрузка моделей
    with st.spinner("🔄 Загрузка моделей..."):
        try:
            from web.utils.api_client import APIClient
            from web.utils.config import WebConfig
            
            config = WebConfig()
            api_client = APIClient(config.backend_url)
            models = api_client.get_models()
            
            if models:
                st.success(f"Loaded {len(models)} models")
                
                # Filters
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    search_term = st.text_input("Search by name:", placeholder="Enter model name")
                
                with col2:
                    # Get unique providers (from model ID)
                    providers = list(set([model.get('id', '').split('/')[0] for model in models if '/' in model.get('id', '')]))
                    providers = [p for p in providers if p]  # Remove empty
                    selected_provider = st.selectbox("Provider:", ["All"] + sorted(providers))
                
                with col3:
                    sort_by = st.selectbox("Sort by:", ["Name", "ID", "Context Length"])
                
                # Фильтрация моделей
                filtered_models = models.copy()
                
                if search_term:
                    filtered_models = [
                        model for model in filtered_models 
                        if search_term.lower() in model.get('id', '').lower() or 
                           search_term.lower() in model.get('name', '').lower()
                    ]
                
                if selected_provider != "All":
                    filtered_models = [
                        model for model in filtered_models 
                        if model.get('id', '').startswith(f"{selected_provider}/")
                    ]
                
                # Sorting
                if sort_by == "Name":
                    filtered_models.sort(key=lambda x: x.get('name', x.get('id', '')))
                elif sort_by == "ID":
                    filtered_models.sort(key=lambda x: x.get('id', ''))
                elif sort_by == "Context Length":
                    filtered_models.sort(key=lambda x: x.get('context_length', 0), reverse=True)
                
                # Display models
                st.markdown(f"### Found models: {len(filtered_models)}")
                
                for model in filtered_models:
                    with st.expander(f"🤖 {model.get('name', model.get('id', 'Unknown'))}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**ID:** `{model.get('id', 'N/A')}`")
                            st.write(f"**Название:** {model.get('name', 'N/A')}")
                            if model.get('description'):
                                st.write(f"**Описание:** {model.get('description')}")
                        
                        with col2:
                            if model.get('context_length'):
                                st.metric("Размер контекста", f"{model.get('context_length'):,} токенов")
                            
                            # Определяем провайдера
                            model_id = model.get('id', '')
                            if '/' in model_id:
                                provider = model_id.split('/')[0]
                                st.write(f"**Провайдер:** {provider}")
                        
                        # Кнопка для использования модели
                        if st.button(f"🎯 Использовать модель", key=f"use_{model.get('id')}"):
                            st.session_state.selected_model = model.get('id')
                            st.success(f"✅ Выбрана модель: {model.get('name', model.get('id'))}")
                            st.rerun()
                
                # Статистика моделей
                if filtered_models:
                    st.markdown("---")
                    st.subheader("📊 Статистика моделей")
                    
                    # Подготовка данных для графиков
                    provider_counts = {}
                    context_lengths = []
                    
                    for model in filtered_models:
                        # Подсчет по провайдерам
                        model_id = model.get('id', '')
                        if '/' in model_id:
                            provider = model_id.split('/')[0]
                            provider_counts[provider] = provider_counts.get(provider, 0) + 1
                        
                        # Размеры контекста
                        if model.get('context_length'):
                            context_lengths.append(model.get('context_length'))
                    
                    col1, col2 = st.columns(2)
                    
                    # График по провайдерам
                    with col1:
                        if provider_counts:
                            fig_providers = px.pie(
                                values=list(provider_counts.values()),
                                names=list(provider_counts.keys()),
                                title="Распределение моделей по провайдерам"
                            )
                            st.plotly_chart(fig_providers, width="content")
                    
                    # График размеров контекста
                    with col2:
                        if context_lengths:
                            fig_context = px.histogram(
                                x=context_lengths,
                                title="Распределение размеров контекста",
                                labels={"x": "Размер контекста (токены)", "y": "Количество моделей"}
                            )
                            st.plotly_chart(fig_context, width="content")
            
            else:
                st.warning("⚠️ Модели не найдены")
                
        except Exception as e:
            st.error(f"❌ Ошибка загрузки моделей: {e}")
            st.info("💡 Убедитесь, что backend сервер запущен и доступен")

# Запуск страницы
render_models_page()