import requests
import sys
import time

TOKEN = "7971183338:AAEZm72Md1ZFbpmtG-fmLHdmXzzPsD_GLYI"

def fix_bot():
    print("1. Удаляю webhook...")
    url = f'https://api.telegram.org/bot{TOKEN}/deleteWebhook'
    resp = requests.get(url)
    print(f"   Результат: {resp.json()}")

    print("\n2. Получаю информацию о боте...")
    url = f'https://api.telegram.org/bot{TOKEN}/getMe'
    resp = requests.get(url)
    print(f"   Бот: {resp.json()}")

    print("\n3. Очищаю все ожидающие обновления...")
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1'
    resp = requests.get(url)
    print(f"   Очищено обновлений: {len(resp.json().get('result', []))}")

    print("\n4. Получаю последний offset...")
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
    resp = requests.get(url)
    updates = resp.json().get('result', [])
    if updates:
        last_id = updates[-1]['update_id']
        print(f"   Последний update_id: {last_id}")
        
        # Пропускаем все обновления
        url = f'https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}'
        requests.get(url)
        print(f"   Пропустил все обновления до {last_id+1}")

    print("\n✅ Готово! Теперь можно запускать бота.")

if __name__ == "__main__":
    fix_bot()
