#!/usr/bin/env python3
"""
Скрипт для ручного наполнения базы данных
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import Database

async def init_manually():
    print("=== РУЧНОЕ НАПОЛНЕНИЕ БАЗЫ ДАННЫХ ===")
    
    # Создаем таблицы
    print("Создаем таблицы...")
    await Database.create_tables()
    
    # Проверяем количество коктейлей
    count = await Database.get_cocktails_count()
    print(f"В базе уже есть {count} коктейлей")
    
    if count > 0:
        response = input("База уже содержит коктейли. Продолжить? (y/N): ")
        if response.lower() != 'y':
            print("Отменено")
            return
    
    # Примеры коктейлей
    cocktails = [
        {
            "name": "Мохито",
            "description": "Освежающий кубинский коктейль с мятой и лаймом",
            "ingredients": {
                "белый ром": "50 мл",
                "свежая мята": "6-8 листиков",
                "лайм": "половинка",
                "сахарный сироп": "20 мл",
                "содовая": "100 мл",
                "лед": "дробленый"
            },
            "recipe": "1. В высокий бокал положите мяту и лайм\n2. Добавьте сахарный сироп и аккуратно подавите\n3. Наполните бокал дробленым льдом\n4. Добавьте ром и содовую\n5. Аккуратно перемешайте",
            "tags": ["освежающий", "летний", "мятный", "цитрусовый"],
            "strength": 15,
            "difficulty": "легко"
        },
        {
            "name": "Маргарита",
            "description": "Классический коктейль с текилой и лаймом",
            "ingredients": {
                "текила": "50 мл",
                "трипл сек": "20 мл",
                "лаймовый сок": "20 мл",
                "сахарный сироп": "10 мл",
                "лед": "кубики",
                "соль": "для ободка"
            },
            "recipe": "1. Обмакните край бокала в сок лайма и соль\n2. В шейкер со льдом добавьте все ингредиенты\n3. Взбейте и процедите в бокал\n4. Украсьте долькой лайма",
            "tags": ["классика", "текила", "цитрусовый", "соленый"],
            "strength": 25,
            "difficulty": "средне"
        }
    ]
    
    print(f"Добавляю {len(cocktails)} коктейлей...")
    
    for cocktail_data in cocktails:
        try:
            cocktail = await Database.add_cocktail(**cocktail_data)
            print(f"✓ {cocktail.name}")
        except Exception as e:
            print(f"✗ {cocktail_data['name']}: {e}")
    
    count = await Database.get_cocktails_count()
    print(f"\n✅ Готово! В базе {count} коктейлей")

if __name__ == "__main__":
    asyncio.run(init_manually())
