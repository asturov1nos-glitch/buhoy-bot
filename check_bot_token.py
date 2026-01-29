import requests

# Токен из .env
TOKEN = "7971183338:AAHcLoNGZkuF9VOfEGirGKwQvR5mz2lySRc"

print("Проверяем токен...")
url = f'https://api.telegram.org/bot{TOKEN}/getMe'
try:
    response = requests.get(url, timeout=10)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code == 200:
        bot_info = response.json()['result']
        print(f"\n✅ Токен рабочий!")
        print(f"   Имя бота: {bot_info['first_name']}")
        print(f"   Username: @{bot_info['username']}")
        print(f"   ID: {bot_info['id']}")
    else:
        print(f"\n❌ Токен не работает: {response.json()['description']}")
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    print("Возможные причины:")
    print("1. Неправильный токен")
    print("2. Проблемы с интернетом")
    print("3. Токен был отозван")
