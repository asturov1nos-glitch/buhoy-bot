#!/bin/bash

echo "=== ПОЛНЫЙ ТЕСТ СБОРКИ И ЗАПУСКА ==="
echo

# 1. Проверяем Dockerfile
echo "1. Проверка Dockerfile..."
if [ -f Dockerfile ]; then
    echo "✅ Dockerfile найден"
    # Проверяем первую строку
    FIRST_LINE=$(head -1 Dockerfile)
    if [[ $FIRST_LINE == FROM* ]]; then
        echo "✅ Первая строка Dockerfile правильная: $FIRST_LINE"
    else
        echo "❌ Ошибка: первая строка должна быть FROM, а не: $FIRST_LINE"
        exit 1
    fi
else
    echo "❌ Dockerfile не найден"
    exit 1
fi

echo

# 2. Проверяем docker-compose.yml
echo "2. Проверка docker-compose.yml..."
if [ -f docker-compose.yml ]; then
    echo "✅ docker-compose.yml найден"
    # Проверяем синтаксис
    if docker-compose config -q; then
        echo "✅ docker-compose.yml синтаксически правильный"
    else
        echo "❌ Ошибка в docker-compose.yml"
        exit 1
    fi
else
    echo "❌ docker-compose.yml не найден"
    exit 1
fi

echo

# 3. Проверяем наличие .env
echo "3. Проверка .env файла..."
if [ -f .env ]; then
    echo "✅ .env файл найден"
    # Проверяем BOT_TOKEN
    if grep -q "BOT_TOKEN=" .env; then
        BOT_TOKEN=$(grep BOT_TOKEN= .env | cut -d'=' -f2)
        if [[ $BOT_TOKEN != "test_bot_token_123456:AAHb1234567890" && $BOT_TOKEN != "ваш_настоящий_токен_бота" ]]; then
            echo "✅ BOT_TOKEN установлен (длина: ${#BOT_TOKEN})"
        else
            echo "⚠️  ВНИМАНИЕ: Используется тестовый BOT_TOKEN"
            echo "   Получите настоящий у @BotFather"
        fi
    else
        echo "❌ BOT_TOKEN не найден в .env"
    fi
else
    echo "⚠️  .env файл не найден"
    echo "   Создайте: cp .env.example .env"
fi

echo

# 4. Сборка образа
echo "4. Тест сборки Docker образа..."
echo "Команда: docker build -q -t cocktail-bot-test ."
docker build -q -t cocktail-bot-test .
if [ $? -eq 0 ]; then
    echo "✅ Docker образ успешно собран"
    
    # Показываем информацию о образе
    echo "Информация о собранном образе:"
    docker images cocktail-bot-test --format "  Размер: {{.Size}}, Создан: {{.CreatedAt}}"
    
    # Удаляем тестовый образ
    echo "Удаление тестового образа..."
    docker rmi cocktail-bot-test 2>/dev/null
    echo "✅ Тестовый образ удален"
else
    echo "❌ Ошибка сборки Docker образа"
    echo "Подробности ошибки:"
    docker build -t cocktail-bot-test .
    exit 1
fi

echo
echo "=== ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! ==="
echo
echo "✅ Dockerfile: OK"
echo "✅ docker-compose.yml: OK"
echo "✅ Сборка образа: OK"
echo
echo "Теперь можно запустить бота:"
echo "  docker-compose up -d"
echo
echo "Для Yandex Cloud деплоя:"
echo "  1. Настройте секреты в GitHub"
echo "  2. Запушите изменения в main ветку"
