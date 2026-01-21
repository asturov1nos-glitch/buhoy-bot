# src/config.py - ВЕРСИЯ ДЛЯ TIMEWEB APP PLATFORM
import os
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # 1. Загружаем переменные окружения
        self.BOT_TOKEN = os.getenv('BOT_TOKEN', '')
        
        # 2. Админы
        admin_ids = os.getenv('ADMIN_IDS', '860643367')
        self.ADMIN_IDS = []
        try:
            if admin_ids:
                self.ADMIN_IDS = [int(id.strip()) for id in admin_ids.split(',')]
        except ValueError:
            logger.warning(f"Ошибка парсинга ADMIN_IDS: {admin_ids}")
        
        # 3. SQLite БД в Volume (ВАЖНО: /data - том App Platform)
        self.DB_PATH = os.getenv('DB_PATH', '/data/cocktails.db')
        
        # 4. Формируем URL для SQLite
        # Используем aiosqlite для асинхронной работы
        self.database_url = f"sqlite+aiosqlite:///{self.DB_PATH}"
        
        # 5. Для совместимости со старым кодом (если где-то используется)
        self.DB_HOST = 'localhost'
        self.DB_PORT = '5432'
        self.DB_NAME = 'cocktail_bot'
        self.DB_USER = 'postgres'
        self.DB_PASSWORD = 'postgres'
        
        # 6. Redis не используем (заменили на MemoryStorage)
        self.REDIS_HOST = 'localhost'
        self.REDIS_PORT = 6379
        
        # 7. Порт (для Timeweb App Platform)
        self.PORT = int(os.getenv('PORT', '8080'))
        
        logger.info(f"✅ Конфигурация: Бот={bool(self.BOT_TOKEN)}, Админы={self.ADMIN_IDS}")
        logger.info(f"✅ База данных: {self.DB_PATH}")
        logger.info(f"✅ Database URL: {self.database_url}")

# Глобальный экземпляр
config = Config()