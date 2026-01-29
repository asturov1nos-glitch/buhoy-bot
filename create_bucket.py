import boto3

# Используем ключи из логов
S3_ACCESS_KEY = "GKQ5I0RISV1VKZDCF46M"
S3_SECRET_KEY = "MksAYd1gM8ANzWOnWx3J8xee1k6EcDn5Kl2x8mgJ"
S3_ENDPOINT_URL = "https://s3.timeweb.cloud"
S3_BUCKET = "cocktail-bot-backups"

print("Пробую подключиться к S3...")
print(f"Access Key: {S3_ACCESS_KEY[:10]}...")
print(f"Secret Key: {S3_SECRET_KEY[:10]}...")

try:
    s3 = boto3.client('s3',
                      endpoint_url=S3_ENDPOINT_URL,
                      aws_access_key_id=S3_ACCESS_KEY,
                      aws_secret_access_key=S3_SECRET_KEY)
    
    print("✅ Подключение к S3 успешно!")
    
    # Проверяем существование бакета
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
        print(f"✅ Бакет '{S3_BUCKET}' уже существует!")
    except Exception as e:
        print(f"ℹ️  Бакет не найден: {e}")
        print(f"🔄 Создаю бакет '{S3_BUCKET}'...")
        
        try:
            # Пробуем создать бакет
            s3.create_bucket(Bucket=S3_BUCKET)
            print(f"✅ Бакет '{S3_BUCKET}' успешно создан!")
        except Exception as create_error:
            print(f"❌ Ошибка создания: {create_error}")
            
            # Пробуем с регионом
            print("🔄 Пробую создать с регионом 'ru-1'...")
            try:
                s3.create_bucket(
                    Bucket=S3_BUCKET,
                    CreateBucketConfiguration={
                        'LocationConstraint': 'ru-1'
                    }
                )
                print(f"✅ Бакет '{S3_BUCKET}' создан с регионом 'ru-1'!")
            except Exception as region_error:
                print(f"❌ Ошибка с регионом: {region_error}")
                
except Exception as e:
    print(f"❌ Ошибка подключения к S3: {e}")
    print("\n🔧 Возможные причины:")
    print("1. Неправильные ключи доступа")
    print("2. Проблемы с сетью")
    print("3. Endpoint URL неверный")
