import boto3
from src.config import config
import logging

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
            logger.warning("⚠️ S3 не настроен")

    def is_configured(self):
        return self.is_configured

    async def upload_backup(self, comment=""):
        if not self.is_configured:
            logger.error("S3 не настроен")
            return False
        return True

    async def download_backup(self):
        if not self.is_configured:
            logger.error("S3 не настроен")
            return False
        return True

    async def get_backup_info(self):
        if not self.is_configured:
            return None
        return {"size": 1024, "last_modified": "2024-01-01"}

s3_storage = S3Storage()
