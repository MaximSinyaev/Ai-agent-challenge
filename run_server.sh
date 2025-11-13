#!/bin/bash

# Скрипт для запуска AI Agent Backend

export APPLICATION_ENV=LOCAL

echo "Запуск AI Agent Backend..."
echo "Environment: $APPLICATION_ENV"
echo "URL: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo ""

# Активируем виртуальное окружение если оно есть
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Виртуальное окружение активировано"
fi

# Запускаем сервер
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000