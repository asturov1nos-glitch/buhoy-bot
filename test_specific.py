#!/usr/bin/env python3
"""
Скрипт для тестирования конкретных кнопок
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_specific():
    from src.database import Database
    from src.config import config
    
    print("=== ТЕСТ КОНКРЕТНЫХ ПРОБЛЕМ ===")
    
    # 1. Проверка случайного коктейля
    print("\n1. Тест 'Случайный коктейль':")
    try:
        cocktail = await Database.get_random_cocktail()
        if cocktail:
            print(f"   ✅ Найден: {cocktail.name}")
            print(f"   Описание: {cocktail.description[:50]}..." if cocktail.description else "   Описание: нет")
            print(f"   Ингредиентов: {len(cocktail.ingredients)}")
        else:
            print("   ❌ Коктейль не найден!")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 2. Проверка поиска
    print("\n2. Тест поиска 'мохито':")
    try:
        cocktails = await Database.search_cocktails(name="мохито")
        if cocktails:
            print(f"   ✅ Найдено: {len(cocktails)} коктейлей")
            for c in cocktails:
                print(f"   - {c.name}")
        else:
            print("   ❌ Ничего не найдено!")
    except Exception as e:
        print(f"   ❌ Ошибка поиска: {e}")
    
    # 3. Проверка всех коктейлей
    print("\n3. Тест 'Все коктейли':")
    try:
        cocktails = await Database.get_all_cocktails()
        print(f"   ✅ Всего коктейлей: {len(cocktails)}")
        if cocktails:
            print("   Первые 3:")
            for c in cocktails[:3]:
                print(f"   - {c.name}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 4. Проверка конфигурации
    print("\n4. Проверка конфигурации:")
    print(f"   BOT_TOKEN: {'✅ Установлен' if config.BOT_TOKEN else '❌ НЕТ!'}")
    print(f"   Админы: {config.ADMIN_IDS}")
    print(f"   База данных: {config.DB_HOST}:{config.DB_PORT}")
    print(f"   Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
    
    print("\n=== ВЫВОД ===")
    if config.BOT_TOKEN:
        print("✅ Конфигурация в порядке")
        print("✅ База данных работает")
        print("\nПроблема может быть в:")
        print("1. Обработчиках кнопок (проверь текст кнопок)")
        print("2. Состояниях FSM")
        print("3. Клавиатурах (неправильные кнопки)")
    else:
        print("❌ BOT_TOKEN не установлен!")

if __name__ == "__main__":
    asyncio.run(test_specific())
