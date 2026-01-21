import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 не установлен")

class S3Storage:
    def __init__(self):
        self.enabled = False
        
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 недоступен. Установите: pip install boto3")
            return
        
        from src.config import config
        
        self.config = config
        self.endpoint_url = config.S3_ENDPOINT_URL
        self.access_key = config.S3_ACCESS_KEY
        self.secret_key = config.S3_SECRET_KEY
        self.bucket_name = config.S3_BUCKET
        self.local_db_path = config.DB_PATH
        
        self.s3_client = None
        
        if config.S3_CONFIGURED:
            try:
                # Тестируем подключение
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=self.endpoint_url,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    config=boto3.session.Config(signature_version='s3v4')
                )
                
                # Проверяем бакет
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                self.enabled = True
                logger.info(f"✅ S3 подключен к бакету: {self.bucket_name}")
            except Exception as e:
                logger.error(f"❌ Ошибка подключения к S3: {e}")
                logger.info("⚠️ Проверьте: 1) Ключи доступа 2) Бакет существует 3) Сеть доступна")
        else:
            logger.warning("S3 не настроен (отсутствуют переменные окружения)")
    
    def is_configured(self) -> bool:
        """Проверяем, настроен ли S3"""
        return self.enabled
    
    async def download_backup(self) -> bool:
        """Скачиваем последний бэкап из S3"""
        if not self.enabled:
            logger.warning("S3 отключен, пропускаем загрузку")
            return False
        
        try:
            # Проверяем, существует ли файл в S3
            try:
                self.s3_client.head_object(
                    Bucket=self.bucket_name, 
                    Key='cocktails.db'
                )
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    logger.info("Бэкап в S3 не найден. Начинаем с чистой базы.")
                else:
                    logger.error(f"Ошибка проверки бэкапа: {e}")
                return False
            
            # Скачиваем файл
            logger.info("Загружаем базу из S3...")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.s3_client.download_file,
                self.bucket_name,
                'cocktails.db',
                self.local_db_path
            )
            
            # Проверяем
            if Path(self.local_db_path).exists():
                size = Path(self.local_db_path).stat().st_size
                logger.info(f"✅ База загружена из S3 ({size} байт)")
                return True
            else:
                logger.error("❌ Файл не был загружен")
                return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки из S3: {e}")
            return False
    
    async def upload_backup(self, comment: str = "") -> bool:
        """Загружаем бэкап в S3"""
        if not self.enabled:
            logger.warning("S3 отключен, пропускаем загрузку")
            return False
        
        if not Path(self.local_db_path).exists():
            logger.warning("Локальный файл базы не найден")
            return False
        
        try:
            # Загружаем файл
            logger.info("Загружаем базу в S3...")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.s3_client.upload_file,
                self.local_db_path,
                self.bucket_name,
                'cocktails.db',
                {
                    'Metadata': {
                        'upload-time': datetime.now().isoformat(),
                        'comment': comment,
                        'app': 'cocktail-bot',
                        'version': '1.0'
                    }
                }
            )
            
            # Проверяем загрузку
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key='cocktails.db'
            )
            
            size = response['ContentLength']
            logger.info(f"✅ База загружена в S3 ({size} байт)")
            
            # Создаем мета-файл с информацией
            await self._create_meta_file(comment)
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки в S3: {e}")
            return False
    
    async def _create_meta_file(self, comment: str = ""):
        """Создаем JSON файл с информацией о бэкапе"""
        try:
            meta_data = {
                'backup_time': datetime.now().isoformat(),
                'comment': comment,
                'database_size': Path(self.local_db_path).stat().st_size,
                'app_version': '1.0'
            }
            
            import json
            meta_json = json.dumps(meta_data, indent=2)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key='backup_meta.json',
                Body=meta_json,
                ContentType='application/json'
            )
            
        except Exception as e:
            logger.warning(f"Не удалось создать meta файл: {e}")
    
    async def get_backup_info(self) -> Optional[Dict[str, Any]]:
        """Получаем информацию о последнем бэкапе"""
        if not self.enabled:
            return None
        
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key='cocktails.db'
            )
            
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'metadata': response.get('Metadata', {}),
                'exists': True
            }
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return {'exists': False}
            logger.error(f"Ошибка получения информации о бэкапе: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return None
    
    async def list_backups(self):
        """Список всех бэкапов (если будет версионирование)"""
        if not self.enabled:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='cocktails.db'
            )
            
            backups = []
            for obj in response.get('Contents', []):
                backups.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified']
                })
            
            return backups
        except Exception as e:
            logger.error(f"Ошибка получения списка бэкапов: {e}")
            return []

# Глобальный экземпляр
s3_storage = S3Storage()