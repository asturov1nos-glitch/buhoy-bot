import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import config
from src.database import Database
from src.s3_storage import s3_storage
from src.handlers import user_handlers, admin_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def periodic_backup():
    """Периодический бэкап каждые 5 минут"""
    while True:
        await asyncio.sleep(300)  # 5 минут
        try:
            await s3_storage.upload_backup(comment="Периодический бэкап")
        except Exception as e:
            logger.error(f"Ошибка периодического бэкапа: {e}")

async def main():
    logger.info("=== ЗАПУСК COCKTAIL BOT (S3 BACKUP VERSION) ===")
    
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен!")
        return
    
    # 1. Пробуем загрузить базу из S3
    logger.info("Проверяем бэкапы в S3...")
    await s3_storage.download_backup()
    
    # 2. Инициализация базы данных
    logger.info("Инициализация базы данных...")
    try:
        await Database.create_tables()
        count = await Database.get_cocktails_count()
        logger.info(f"✓ БД готова. Коктейлей: {count}")
        
        # 3. Запускаем периодический бэкап
        asyncio.create_task(periodic_backup())
        logger.info("✓ Периодический бэкап в S3 запущен (каждые 5 мин)")
        
    except Exception as e:
        logger.error(f"✗ Ошибка БД: {e}")
        return
    
    # 4. Создаем бота и диспетчер
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # 5. Подключаем обработчики
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    
    logger.info("✓ Бот запущен в режиме polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())