import os
import logging
from typing import List, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # Загружаем .env файл если существует
        try:
            from dotenv import load_dotenv
            load_dotenv()
            logger.info(".env файл загружен")
        except Exception as e:
            logger.warning(f"Не удалось загрузить .env файл: {e}")
        
        # Бот
        self.BOT_TOKEN = self._get_env("BOT_TOKEN", "")
        
        # Админы
        admin_ids = self._get_env("ADMIN_IDS", "")
        self.ADMIN_IDS = []
        if admin_ids:
            try:
                self.ADMIN_IDS = [int(id.strip()) for id in admin_ids.split(',') if id.strip()]
            except ValueError as e:
                logger.error(f"Ошибка парсинга ADMIN_IDS: {e}")
        
        # Database
        self.DB_HOST = self._get_env("DB_HOST", "localhost")
        self.DB_PORT = self._get_env("DB_PORT", "5432")
        self.DB_NAME = self._get_env("DB_NAME", "cocktail_bot")
        self.DB_USER = self._get_env("DB_USER", "postgres")
        self.DB_PASSWORD = self._get_env("DB_PASSWORD", "postgres")
        
        # Redis
        self.REDIS_HOST = self._get_env("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(self._get_env("REDIS_PORT", "6379"))
        self.REDIS_PASSWORD = self._get_env("REDIS_PASSWORD", None)
        
        # Webhook
        self.WEBHOOK_URL = self._get_env("WEBHOOK_URL", "")
        self.WEBHOOK_PATH = self._get_env("WEBHOOK_PATH", "/webhook")
        self.PORT = int(self._get_env("PORT", "8080"))
        
        logger.info(f"Конфигурация загружена. Бот: {bool(self.BOT_TOKEN)}, Админов: {len(self.ADMIN_IDS)}")
    
    def _get_env(self, key: str, default: str = None) -> str:
        """Безопасное получение переменной окружения"""
        value = os.getenv(key)
        
        if value is None:
            return default
        
        # Удаляем лишние пробелы и кавычки
        value = value.strip().strip('"').strip("'")
        
        return value if value else default
    
    @property
    def database_url(self) -> str:
        """URL для подключения к PostgreSQL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self) -> str:
        """URL для подключения к Redis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    @property
    def use_webhook(self) -> bool:
        """Использовать webhook режим?"""
        return bool(self.WEBHOOK_URL)

# Создаем глобальный конфиг
config = Config()
