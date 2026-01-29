import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        load_dotenv()
        logger.info(".env файл загружен")
        
        self.BOT_TOKEN = os.getenv('BOT_TOKEN', '')
        if not self.BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не найден в .env")
        
        # Администраторы
        admin_ids_str = os.getenv('ADMIN_IDS', '')
        self.ADMIN_IDS = []
        
        if admin_ids_str:
            try:
                admin_ids_str = admin_ids_str.strip()
                if admin_ids_str.startswith('[') and admin_ids_str.endswith(']'):
                    import ast
                    admin_ids_list = ast.literal_eval(admin_ids_str)
                    self.ADMIN_IDS = [int(id) for id in admin_ids_list]
                elif ',' in admin_ids_str:
                    self.ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
                else:
                    self.ADMIN_IDS = [int(admin_ids_str)]
            except Exception as e:
                logger.error(f"Ошибка парсинга ADMIN_IDS: {e}")
                self.ADMIN_IDS = []
        
        # База данных
        self.database_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:////tmp/cocktails.db')
        if self.database_url.startswith('sqlite+aiosqlite:///'):
            self.DB_PATH = self.database_url.replace('sqlite+aiosqlite:///', '')
        else:
            self.DB_PATH = '/tmp/cocktails.db'
        
        # S3
        self.S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', '')
        self.S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', '')
        self.S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', '')
        self.S3_BUCKET = os.getenv('S3_BUCKET', '')
        
        self.S3_CONFIGURED = all([
            self.S3_ENDPOINT_URL,
            self.S3_ACCESS_KEY,
            self.S3_SECRET_KEY,
            self.S3_BUCKET
        ])
        
        logger.info("🔍 DEBUG S3 переменные:")
        logger.info(f"  S3_ENDPOINT_URL: {'✅ Есть' if self.S3_ENDPOINT_URL else '❌ Нет'} -> {self.S3_ENDPOINT_URL[:30] if self.S3_ENDPOINT_URL else ''}")
        logger.info(f"  S3_ACCESS_KEY: {'✅ Есть' if self.S3_ACCESS_KEY else '❌ Нет'} -> {self.S3_ACCESS_KEY[:10] + '...' if self.S3_ACCESS_KEY else ''}")
        logger.info(f"  S3_SECRET_KEY: {'✅ Есть' if self.S3_SECRET_KEY else '❌ Нет'} -> {self.S3_SECRET_KEY[:10] + '...' if self.S3_SECRET_KEY else ''}")
        logger.info(f"  S3_BUCKET: {'✅ Есть' if self.S3_BUCKET else '❌ Нет'} -> {self.S3_BUCKET}")
        
        if self.S3_CONFIGURED:
            logger.info("✅✅✅ S3 НАСТРОЕН! Бэкапы будут работать.")
        else:
            logger.warning("⚠️ S3 не настроен. Добавьте переменные S3_*")
        
        logger.info(f"✅ Конфигурация: Бот={'True' if self.BOT_TOKEN else 'False'}, Админы={self.ADMIN_IDS}, БД={self.database_url}")

config = Config()
