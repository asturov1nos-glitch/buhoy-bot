import boto3
import logging
import os
from src.config import config

logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        self.is_configured = config.S3_CONFIGURED
        self.local_db_path = config.DB_PATH
        
        if self.is_configured:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=config.S3_ENDPOINT_URL,
                aws_access_key_id=config.S3_ACCESS_KEY,
                aws_secret_access_key=config.S3_SECRET_KEY
            )
            self.bucket_name = config.S3_BUCKET
            logger.info(f"✅ S3 подключен к бакету: {self.bucket_name}")
        else:
            self.s3_client = None
            self.bucket_name = None
            logger.warning("⚠️ S3 не настроен - переменные окружения отсутствуют")

    async def download_backup(self):
        """Скачать базу данных из S3"""
        if not self.is_configured:
            logger.error("S3 не настроен, скачивание невозможно")
            return False
        
        try:
            # Проверяем, есть ли файл в S3
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='cocktails.db'
            )
            
            if 'Contents' not in response:
                logger.info("В S3 нет файла с базой данных")
                return False
            
            # Скачиваем последний backup
            self.s3_client.download_file(
                self.bucket_name,
                'cocktails.db',
                self.local_db_path
            )
            
            logger.info(f"✅ База данных восстановлена из S3: {self.local_db_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка при скачивании из S3: {e}")
            return False

    async def upload_backup(self):
        """Загрузить базу данных в S3"""
        if not self.is_configured:
            logger.error("S3 не настроен, загрузка невозможна")
            return False
        
        if not os.path.exists(self.local_db_path):
            logger.error(f"Файл базы данных не найден: {self.local_db_path}")
            return False
        
        try:
            self.s3_client.upload_file(
                self.local_db_path,
                self.bucket_name,
                'cocktails.db'
            )
            logger.info(f"✅ База данных загружена в S3: {self.bucket_name}/cocktails.db")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке в S3: {e}")
            return False

# Создаем глобальный экземпляр
s3_storage = S3Storage()
