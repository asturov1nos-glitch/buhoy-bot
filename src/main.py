import asyncio
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import config
from src.database import Database
from src.s3_storage import s3_storage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Запуск COCKTAIL BOT (TIMEWEB + S3 VERSION)")
    logger.info("=" * 60)
    
    # Создание бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация хендлеров
    from src.handlers import user_handlers, admin_handlers
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    try:
        # Используем метод create_tables из Database
        await Database.create_tables()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
        # Если есть файл базы данных, попробуем продолжить
        import os
        if os.path.exists(config.database_url.replace('sqlite+aiosqlite:///', '')):
            logger.warning("⚠️ Файл базы данных существует, продолжаем...")
        else:
            logger.error("❌ Файл базы данных не существует, создаем новый...")
            # Попробуем создать файл вручную
            try:
                db_path = config.database_url.replace('sqlite+aiosqlite:///', '')
                Path(db_path).touch()
                logger.info(f"✅ Создан файл базы данных: {db_path}")
            except Exception as e2:
                logger.error(f"❌ Не удалось создать файл базы данных: {e2}")
    
    # Проверка S3
    if s3_storage.is_configured():
        logger.info("✅ S3 настроен")
    else:
        logger.warning("⚠️ S3 не настроен. Работаем с локальной базой.")
    
    logger.info(f"Бот запущен в режиме polling")
    logger.info(f"Админы: {config.ADMIN_IDS}")
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
