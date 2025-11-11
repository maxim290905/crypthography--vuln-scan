#!/bin/bash

echo "🚀 Запуск Cryptography Vulnerability Scanner..."
echo ""

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose"
    exit 1
fi

# Создание .env файла если его нет
if [ ! -f .env ]; then
    echo "📝 Создание .env файла из примера..."
    cp ENV_EXAMPLE.txt .env
    echo "✅ .env файл создан. Вы можете отредактировать его при необходимости."
fi

# Создание директории storage если её нет
mkdir -p storage/reports storage/scans

echo "🔨 Сборка и запуск контейнеров..."
echo ""

# Запуск docker-compose
if docker compose version &> /dev/null; then
    docker compose up --build
else
    docker-compose up --build
fi


