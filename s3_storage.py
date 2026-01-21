import asyncio
import boto3
import aiofiles
import logging
from pathlib import Path
from datetime import datetime
from botocore.exceptions import ClientError
import json
import os

logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        # Конфигурация S3 из переменных окружения
        self.endpoint_url = os.getenv('S3_ENDPOINT_URL', '')
        self.access_key = os.getenv('S3_ACCESS_KEY', '')
        self.secret_key = os.getenv('S3_SECRET_KEY', '')
        self.bucket_name = os.getenv('S3_BUCKET', 'cocktail-bot-backups')
        
        self.s3_client = None
        self.backup_filename = 'cocktails.db'
        self.local_db_path = '/tmp/cocktails.db'  # SQLite файл
        
    def is_configured(self):
        """Проверяем, настроен ли S3"""
        return all([self.endpoint_url, self.access_key, self.secret_key, self.bucket_name])
    
    def _get_s3_client(self):
        """Создаем клиент S3"""
        if not self.is_configured():
            return None
            
        if self.s3_client is None:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
        return self.s3_client
    
    async def download_backup(self):
        """Скачиваем последний бэкап из S3"""
        if not self.is_configured():
            logger.warning("S3 не настроен, пропускаем загрузку")
            return False
            
        try:
            client = self._get_s3_client()
            
            # Проверяем, существует ли файл в S3
            try:
                client.head_object(Bucket=self.bucket_name, Key=self.backup_filename)
            except ClientError:
                logger.info("Бэкап в S3 не найден, начинаем с чистой базы")
                return False
            
            # Скачиваем файл
            logger.info("Загружаем базу из S3...")
            client.download_file(
                self.bucket_name, 
                self.backup_filename, 
                self.local_db_path
            )
            
            # Проверяем размер файла
            size = Path(self.local_db_path).stat().st_size
            logger.info(f"✓ База загружена из S3 ({size} байт)")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки из S3: {e}")
            return False
    
    async def upload_backup(self, comment=""):
        """Загружаем бэкап в S3"""
        if not self.is_configured():
            logger.warning("S3 не настроен, пропускаем загрузку")
            return False
            
        if not Path(self.local_db_path).exists():
            logger.warning("Локальный файл базы не найден")
            return False
            
        try:
            client = self._get_s3_client()
            
            # Загружаем файл
            logger.info("Загружаем базу в S3...")
            client.upload_file(
                self.local_db_path,
                self.bucket_name,
                self.backup_filename,
                ExtraArgs={
                    'Metadata': {
                        'upload-time': datetime.now().isoformat(),
                        'comment': comment
                    }
                }
            )
            
            size = Path(self.local_db_path).stat().st_size
            logger.info(f"✓ База загружена в S3 ({size} байт)")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки в S3: {e}")
            return False
    
    async def get_backup_info(self):
        """Получаем информацию о последнем бэкапе"""
        if not self.is_configured():
            return None
            
        try:
            client = self._get_s3_client()
            response = client.head_object(
                Bucket=self.bucket_name,
                Key=self.backup_filename
            )
            
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'metadata': response.get('Metadata', {})
            }
        except ClientError:
            return None
        except Exception as e:
            logger.error(f"Ошибка получения информации о бэкапе: {e}")
            return None

# Глобальный экземпляр
s3_storage = S3Storage()