import boto3
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
S3_BUCKET = os.getenv('S3_BUCKET')

print("S3_ACCESS_KEY:", S3_ACCESS_KEY[:5] + '...' if S3_ACCESS_KEY else None)
print("S3_SECRET_KEY:", S3_SECRET_KEY[:5] + '...' if S3_SECRET_KEY else None)
print("S3_ENDPOINT_URL:", S3_ENDPOINT_URL)
print("S3_BUCKET:", S3_BUCKET)

# Создаем клиент S3
s3 = boto3.client('s3',
                  endpoint_url=S3_ENDPOINT_URL,
                  aws_access_key_id=S3_ACCESS_KEY,
                  aws_secret_access_key=S3_SECRET_KEY)

# Пробуем получить список бакетов
try:
    response = s3.list_buckets()
    print("\nДоступные бакеты:")
    for bucket in response['Buckets']:
        print(f"  - {bucket['Name']}")
except Exception as e:
    print(f"\nОшибка при подключении к S3: {e}")

# Проверяем существование целевого бакета
try:
    s3.head_bucket(Bucket=S3_BUCKET)
    print(f"\nБакет '{S3_BUCKET}' существует!")
except Exception as e:
    print(f"\nБакет '{S3_BUCKET}' не найден. Ошибка: {e}")
    
    # Спрашиваем пользователя
    create = input(f"\nСоздать бакет '{S3_BUCKET}'? (y/n): ")
    if create.lower() == 'y':
        try:
            # Пробуем создать бакет
            # Для Timeweb Cloud может потребоваться указать регион
            try:
                s3.create_bucket(Bucket=S3_BUCKET)
                print(f"Бакет '{S3_BUCKET}' создан!")
            except Exception as e:
                # Пробуем с регионом
                print(f"Попытка с регионом...")
                s3.create_bucket(
                    Bucket=S3_BUCKET,
                    CreateBucketConfiguration={
                        'LocationConstraint': 'ru-1'
                    }
                )
                print(f"Бакет '{S3_BUCKET}' создан с регионом 'ru-1'!")
        except Exception as create_error:
            print(f"Не удалось создать бакет: {create_error}")
            print("\nСоздайте бакет вручную через панель Timeweb Cloud:")
            print(f"1. Войдите в панель Timeweb")
            print(f"2. Перейдите в S3 хранилище")
            print(f"3. Создайте бакет с именем: {S3_BUCKET}")