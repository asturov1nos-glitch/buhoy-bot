#!/usr/bin/env python3
"""
Тест обработчиков кнопок
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_handlers():
    from src.config import config
    from src.database import Database
    
    print("=== ТЕСТ КНОПОК ===")
    
    # 1. Проверка базы данных
    print("\n1. Проверка базы данных:")
    try:
        count = await Database.get_cocktails_count()
        print(f"   ✅ В базе: {count} коктейлей")
        
        if count > 0:
            cocktail = await Database.get_random_cocktail()
            print(f"   ✅ Случайный коктейль: {cocktail.name}")
        else:
            print("   ❌ База пуста!")
            
    except Exception as e:
        print(f"   ❌ Ошибка БД: {e}")
    
    # 2. Проверка конфигурации
    print("\n2. Проверка конфигурации:")
    print(f"   ✅ BOT_TOKEN: {'установлен' if config.BOT_TOKEN else 'НЕТ!'}")
    print(f"   ✅ ADMIN_IDS: {config.ADMIN_IDS}")
    
    # 3. Проверка обработчиков
    print("\n3. Проверка импортов обработчиков:")
    try:
        from src.handlers import user_router
        print("   ✅ Обработчики импортируются")
        
        # Проверяем есть ли обработчики для кнопок
        handlers_count = len(user_router.message.handlers)
        print(f"   ✅ Зарегистрировано обработчиков: {handlers_count}")
        
    except Exception as e:
        print(f"   ❌ Ошибка импорта: {e}")
    
    print("\n=== РЕКОМЕНДАЦИИ ===")
    if not config.BOT_TOKEN:
        print("1. Установите BOT_TOKEN в .env файле")
    else:
        print("1. Бот должен отвечать на команды")
        print("2. Проверьте /start в Telegram")
        print("3. Если кнопки не работают, проверьте текст кнопок")

if __name__ == "__main__":
    asyncio.run(test_handlers())
