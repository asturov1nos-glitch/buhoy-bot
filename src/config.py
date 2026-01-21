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
        
        # SQLite БД
        self.DB_PATH = '/tmp/cocktails.db'
        
        # Создаем папку для базы если её нет
        db_dir = Path(self.DB_PATH).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # S3 настройки - DEBUG ВЫВОД
        self.S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', '')
        self.S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', '')
        self.S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', '')
        self.S3_BUCKET = os.getenv('S3_BUCKET', '')
        
        # DEBUG: Покажем что получили
        logger.info(f"🔍 DEBUG S3 переменные:")
        logger.info(f"  S3_ENDPOINT_URL: {'✅ Есть' if self.S3_ENDPOINT_URL else '❌ Нет'} -> {self.S3_ENDPOINT_URL[:30] if self.S3_ENDPOINT_URL else ''}")
        logger.info(f"  S3_ACCESS_KEY: {'✅ Есть' if self.S3_ACCESS_KEY else '❌ Нет'} -> {self.S3_ACCESS_KEY[:10] + '...' if self.S3_ACCESS_KEY else ''}")
        logger.info(f"  S3_SECRET_KEY: {'✅ Есть' if self.S3_SECRET_KEY else '❌ Нет'} -> {self.S3_SECRET_KEY[:10] + '...' if self.S3_SECRET_KEY else ''}")
        logger.info(f"  S3_BUCKET: {'✅ Есть' if self.S3_BUCKET else '❌ Нет'} -> {self.S3_BUCKET}")
        
        # Проверяем S3
        self.S3_CONFIGURED = all([
            self.S3_ENDPOINT_URL,
            self.S3_ACCESS_KEY,
            self.S3_SECRET_KEY,
            self.S3_BUCKET
        ])
        
        self.database_url = f"sqlite+aiosqlite:///{self.DB_PATH}"
        
        logger.info(f"✅ Конфигурация: Бот={bool(self.BOT_TOKEN)}, Админы={self.ADMIN_IDS}, БД={self.DB_PATH}")
        
        if self.S3_CONFIGURED:
            logger.info("✅✅✅ S3 НАСТРОЕН! Бэкапы будут работать.")
        else:
            logger.warning("⚠️ S3 не настроен. Добавьте переменные S3_*")
            logger.info("ℹ️ Проверьте в Timeweb Console → App Platform → Переменные окружения")

config = Config()