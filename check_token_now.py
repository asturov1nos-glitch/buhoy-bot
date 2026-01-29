import requests

# Токены которые пробовали
tokens = [
    "7971183338:AAHcLoNGZkuF9VOfEGirGKwQvR5mz2lySRc",
    "7971183338:AAEZm72Md1ZFbpmtG-fmLHdmXzzPsD_GLYI",
    "8229177032:AAGIb3v4jygLqrViV7xjep8Z80f8NNW0Bnw"
]

for token in tokens:
    print(f"\nПроверяю токен: {token[:16]}...")
    url = f'https://api.telegram.org/bot{token}/getMe'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"✅ РАБОЧИЙ ТОКЕН!")
            print(f"   Бот: @{bot_info['username']}")
            print(f"   Имя: {bot_info['first_name']}")
            print(f"   ID: {bot_info['id']}")
            print(f"\n⚠️  Используйте этот токен в .env")
            break
        else:
            print(f"❌ Не работает: {response.json()['description']}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
