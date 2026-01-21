import os

class Config:
    def __init__(self):
        self.BOT_TOKEN = os.getenv('BOT_TOKEN', '')
        admin_ids = os.getenv('ADMIN_IDS', '860643367')
        self.ADMIN_IDS = [int(id.strip()) for id in admin_ids.split(',')] if admin_ids else []
        self.DB_PATH = '/data/cocktails.db'
        self.database_url = f'sqlite+aiosqlite:///{self.DB_PATH}'
        self.DB_HOST = self.DB_USER = self.DB_PASSWORD = 'local'
        self.DB_PORT = '5432'
        self.DB_NAME = 'cocktail_bot'
        self.REDIS_HOST = 'localhost'
        self.REDIS_PORT = 6379
        print(f"✅ Конфиг: Бот={bool(self.BOT_TOKEN)}, Админы={self.ADMIN_IDS}, БД={self.DB_PATH}")

config = Config()
