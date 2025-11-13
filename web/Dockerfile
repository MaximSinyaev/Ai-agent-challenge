FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы веб-приложения
COPY web/ ./web/

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r web/requirements.txt

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash streamlit_user
USER streamlit_user

# Открываем порт
EXPOSE 8501

# Переходим в директорию с приложением
WORKDIR /app/web

# Запускаем Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]