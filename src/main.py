import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # MemoryStorage вместо Redis

from src.config import config
from src.database import Database
from src.handlers import user_handlers, admin_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("=== ЗАПУСК COCKTAIL BOT (TIMEWEB VERSION) ===")
    
    # 1. Инициализация базы данных
    logger.info("Инициализация базы данных...")
    try:
        await Database.create_tables()
        count = await Database.get_cocktails_count()
        logger.info(f"✓ БД готова. Коктейлей: {count}")
    except Exception as e:
        logger.error(f"✗ Ошибка БД: {e}")
        return
    
    # 2. Создаем бота и диспетчер
    bot = Bot(token=config.BOT_TOKEN)
    
    # MemoryStorage вместо RedisStorage - НЕТ REDIS_PASSWORD!
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # 3. Подключаем обработчики
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    
    # 4. Запускаем polling
    logger.info("✓ Бот запущен в режиме polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())