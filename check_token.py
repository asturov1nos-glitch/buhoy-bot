import requests

TOKEN = "7971183338:AAHcLoNGZkuF9VOfEGirGKwQvR5mz2lySRc"
print(f"Проверяем токен: {TOKEN[:16]}...")

url = f'https://api.telegram.org/bot{TOKEN}/getMe'
try:
    response = requests.get(url, timeout=10)
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 200:
        bot_info = response.json()['result']
        print(f"✅ Токен рабочий!")
        print(f"   Имя бота: {bot_info['first_name']}")
        print(f"   Username: @{bot_info['username']}")
        print(f"   ID: {bot_info['id']}")
    else:
        print(f"❌ Ошибка: {response.json()}")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
