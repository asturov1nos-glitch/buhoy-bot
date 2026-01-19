#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации бота
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.config import config
    
    print("=" * 50)
    print("ПРОВЕРКА КОНФИГУРАЦИИ COCKTAIL BOT")
    print("=" * 50)
    
    # Проверяем переменные
    print(f"BOT_TOKEN: {'✓ Установлен' if config.BOT_TOKEN else '✗ НЕ УСТАНОВЛЕН'}")
    print(f"ADMIN_IDS: {config.ADMIN_IDS if config.ADMIN_IDS else '[] (нет админов)'}")
    print(f"DB: {config.DB_USER}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    print(f"Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
    print(f"PORT: {config.PORT}")
    print(f"WEBHOOK: {'✓ Включен' if config.WEBHOOK_URL else '✗ Выключен'}")
    
    print("\n" + "=" * 50)
    
    # Рекомендации
    if not config.BOT_TOKEN or config.BOT_TOKEN == "test_bot_token_123456:AAHb1234567890":
        print("\n⚠️  ВНИМАНИЕ: Используется тестовый BOT_TOKEN!")
        print("   Получите настоящий токен у @BotFather в Telegram")
        print("   Команда: /newbot")
    
    if not config.ADMIN_IDS:
        print("\n⚠️  ВНИМАНИЕ: Нет администраторов!")
        print("   Добавьте ваш Telegram ID в ADMIN_IDS")
        print("   Узнать ID: @userinfobot в Telegram")
    
    print("\n✅ Конфигурация проверена!")
    
except Exception as e:
    print(f"❌ Ошибка при проверке конфигурации: {e}")
    import traceback
    traceback.print_exc()
