import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# НАСТРОЙКА ЛОГГЕРА ПЕРВОЙ СТРОКОЙ!
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 ЗАПУСК COCKTAIL BOT")
    
    # Импортируем config ПОСЛЕ настройки логгера
    from src.config import config
    config.log_config()
    
    if not config.BOT_TOKEN:
        logger.error("Токен не загружен. Завершение.")
        return
    
    # 1. Пытаемся восстановить базу из S3 если она пустая
    try:
        from src.s3_storage_real import s3_storage
        logger.info("Проверяем наличие базы данных...")
        
        # Если файл базы не существует или пустой, пытаемся восстановить из S3
        if not os.path.exists(config.DB_PATH) or os.path.getsize(config.DB_PATH) == 0:
            logger.info("База данных отсутствует или пустая, пытаемся восстановить из S3...")
            if await s3_storage.download_backup():
                logger.info("✅ База успешно восстановлена из S3")
            else:
                logger.info("Не удалось восстановить базу из S3, будет создана новая")
        else:
            logger.info(f"✅ База данных уже существует: {config.DB_PATH}")
    except Exception as e:
        logger.warning(f"Не удалось проверить/восстановить базу из S3: {e}")
    
    # 2. Инициализируем базу данных
    try:
        from src.database import Database
        await Database.create_tables()
        logger.info("✅ База данных инициализирована")
        
        # Проверяем, есть ли коктейли
        count = await Database.get_cocktails_count()
        logger.info(f"📊 Коктейлей в базе: {count}")
        
        # Если база пустая, добавляем тестовый коктейль
        if count == 0:
            from src.database import Database as DB
            test_cocktail = {
                'name': 'Маргарита Классическая',
                'description': 'Классический мексиканский коктейль с текилой и лаймом',
                'ingredients': {'Текила серебряная': '50 мл', 'Лаймовый сок': '25 мл', 'Апельсиновый ликер': '20 мл'},
                'recipe': 'Наполнить шейкер льдом. Добавить все ингредиенты. Взбить 10-15 секунд. Процедить в бокал, украсить долькой лайма.',
                'tags': ['классика', 'текила', 'кислый', 'мексика'],
                'strength': 25,
                'difficulty': 'легко'
            }
            await DB.add_cocktail(**test_cocktail)
            logger.info(f"✅ Добавлен тестовый коктейль: {test_cocktail['name']}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
    
    # 3. Создаем бота и диспетчер
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # 4. Регистрируем роутеры
    from src.handlers import user_handlers, admin_handlers
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    
    logger.info("✅ Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
