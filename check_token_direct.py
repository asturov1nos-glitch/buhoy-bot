import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
print(f"Токен из .env: {TOKEN}")

if not TOKEN:
    print("❌ Токен не найден в .env")
    exit(1)

# Проверяем через API
url = f'https://api.telegram.org/bot{TOKEN}/getMe'
try:
    response = requests.get(url, timeout=10)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code == 200:
        bot_info = response.json()['result']
        print(f"\n✅ ТОКЕН РАБОЧИЙ!")
        print(f"   Бот: @{bot_info['username']}")
        print(f"   Имя: {bot_info['first_name']}")
        print(f"   ID: {bot_info['id']}")
    else:
        print(f"\n❌ ТОКЕН НЕ РАБОЧИЙ: {response.json()['description']}")
except Exception as e:
    print(f"\n❌ Ошибка подключения: {e}")
