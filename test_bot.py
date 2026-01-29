import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import config
from src.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Проверяем токен
    bot_info = await bot.get_me()
    logger.info(f"Бот: {bot_info.username} (ID: {bot_info.id})")
    
    # Проверяем базу данных
    await Database.create_tables()
    logger.info("База данных готова")
    
    # Запускаем polling с явными параметрами
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    asyncio.run(main())
