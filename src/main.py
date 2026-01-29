import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import config
from src.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 ЗАПУСК COCKTAIL BOT")
    logger.info("=" * 60)
    
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    from src.handlers import user_handlers, admin_handlers
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    
    logger.info("Инициализация базы данных...")
    await Database.create_tables()
    logger.info("✅ База данных готова")
    
    logger.info(f"Админы: {config.ADMIN_IDS}")
    logger.info("Бот запущен!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
