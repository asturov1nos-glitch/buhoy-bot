import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import config
from src.database import Database
from src.s3_storage import s3_storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Запуск COCKTAIL BOT (TIMEWEB + S3 VERSION)")
    logger.info("=" * 60)
    
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # ВАЖНО: Сначала регистрируем админ-обработчики, потом пользовательские
    from src.handlers import admin_handlers, user_handlers
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    
    logger.info("Инициализация базы данных...")
    await Database.create_tables()
    logger.info("✅ База данных инициализирована")
    
    if s3_storage.is_configured():
        logger.info("✅ S3 настроен")
    else:
        logger.warning("⚠️ S3 не настроен. Работаем с локальной базой.")
    
    logger.info(f"Бот запущен в режиме polling")
    logger.info(f"Админы: {config.ADMIN_IDS}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
