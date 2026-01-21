import os
import logging
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # Загружаем .env если есть
        try:
            from dotenv import load_dotenv
            load_dotenv()
            logger.info(".env файл загружен")
        except:
            pass
        
        # Бот
        self.BOT_TOKEN = os.getenv('BOT_TOKEN', '')
        if not self.BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не установлен!")
        
        # Админы
        admin_ids = os.getenv('ADMIN_IDS', '')
        self.ADMIN_IDS = []
        if admin_ids:
            try:
                self.ADMIN_IDS = [int(id.strip()) for id in admin_ids.split(',')]
            except ValueError as e:
                logger.error(f"Ошибка парсинга ADMIN_IDS: {e}")
        
        # SQLite БД - путь зависит от окружения
        if os.getenv('TIMEWEB_ENV'):
            # В Timeweb - используем /tmp с S3 бэкапами
            self.DB_PATH = os.getenv('DB_PATH', '/tmp/cocktails.db')
        else:
            # Локально - используем текущую директорию
            self.DB_PATH = os.getenv('DB_PATH', './cocktails.db')
        
        # Создаем папку для базы если её нет
        db_dir = Path(self.DB_PATH).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        self.database_url = f"sqlite+aiosqlite:///{self.DB_PATH}"
        
        # S3 настройки
        self.S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', '')
        self.S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', '')
        self.S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', '')
        self.S3_BUCKET = os.getenv('S3_BUCKET', 'cocktail-bot-backups')
        
        # Проверяем S3 конфигурацию
        self.S3_CONFIGURED = all([
            self.S3_ENDPOINT_URL,
            self.S3_ACCESS_KEY,
            self.S3_SECRET_KEY,
            self.S3_BUCKET
        ])
        
        if self.S3_CONFIGURED:
            logger.info("✅ S3 настроен для бэкапов")
        else:
            logger.warning("⚠️ S3 не настроен. Бэкапы будут отключены.")
            logger.info("ℹ️ Для настройки S3 добавь переменные: S3_ENDPOINT_URL, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET")
        
        # Порт
        self.PORT = int(os.getenv('PORT', '8080'))
        
        logger.info(f"✅ Конфигурация: Бот={bool(self.BOT_TOKEN)}, Админы={self.ADMIN_IDS}")
        logger.info(f"✅ Database: {self.DB_PATH}")
        logger.info(f"✅ S3: {'Настроен ✅' if self.S3_CONFIGURED else 'Не настроен ⚠️'}")

# Глобальный конфиг
config = Config()