import asyncio
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import config
from src.database import Database
from src.s3_storage import s3_storage
from src.handlers import user_handlers, admin_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def periodic_backup():
    """Периодический бэкап каждые 15 минут"""
    while True:
        await asyncio.sleep(900)  # 15 минут
        try:
            if s3_storage.is_configured():
                logger.info("🔄 Запуск периодического бэкапа...")
                success = await s3_storage.upload_backup(comment="Периодический бэкап")
                if success:
                    logger.info("✅ Периодический бэкап завершен")
        except Exception as e:
            logger.error(f"❌ Ошибка периодического бэкапа: {e}")

async def startup_tasks():
    """Задачи при старте бота"""
    logger.info("🚀 Выполняю стартовые задачи...")
    
    # 1. Проверяем и создаем файл базы
    db_path = Path(config.DB_PATH)
    if not db_path.exists():
        logger.info(f"📁 Создаю файл базы: {config.DB_PATH}")
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 2. Загружаем из S3 если настроено
    if s3_storage.is_configured():
        logger.info("☁️ Проверяем бэкапы в S3...")
        await s3_storage.download_backup()
    else:
        logger.warning("⚠️ S3 не настроен. Работаем с локальной базой.")
    
    # 3. Создаем таблицы
    logger.info("🗄️ Инициализация базы данных...")
    try:
        await Database.create_tables()
        count = await Database.get_cocktails_count()
        logger.info(f"✅ БД готова. Коктейлей: {count}")
    except Exception as e:
        logger.error(f"❌ Ошибка БД: {e}")
        raise
    
    # 4. Запускаем периодический бэкап
    if s3_storage.is_configured():
        asyncio.create_task(periodic_backup())
        logger.info("✅ Периодический бэкап в S3 запущен (каждые 15 мин)")

async def main():
    logger.info("=" * 50)
    logger.info("🍸 ЗАПУСК COCKTAIL BOT (TIMEWEB + S3 VERSION)")
    logger.info("=" * 50)
    
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен! Завершаю работу.")
        return
    
    try:
        # Стартовые задачи
        await startup_tasks()
        
        # Создаем бота
        bot = Bot(token=config.BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Подключаем обработчики
        dp.include_router(user_handlers.router)
        dp.include_router(admin_handlers.router)
        
        logger.info("✅ Бот запущен в режиме polling")
        logger.info(f"🤖 Админы: {config.ADMIN_IDS}")
        logger.info(f"💾 База: {config.DB_PATH}")
        logger.info(f"☁️ S3: {'✅ Настроен' if s3_storage.is_configured() else '⚠️ Не настроен'}")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")