import logging

logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        logger.warning("S3Storage: Режим заглушки. Реальный S3 не настроен.")
    
    def is_configured(self):
        return False
    
    async def download_backup(self):
        logger.warning("S3 не настроен, пропускаем загрузку")
        return False
    
    async def upload_backup(self, comment=""):
        logger.warning("S3 не настроен, пропускаем загрузку")
        return False
    
    async def get_backup_info(self):
        return None

s3_storage = S3Storage()
