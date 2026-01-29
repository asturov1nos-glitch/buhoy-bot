import requests

BOT_TOKEN = "7971183338:AAEZm72Md1ZFbpmtG-fmLHdmXzzPsD_GLYI"

# 1. Удаляем webhook
url = f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook'
response = requests.get(url)
print("1. Удаление webhook:", response.json())

# 2. Получаем информацию о боте
url = f'https://api.telegram.org/bot{BOT_TOKEN}/getMe'
response = requests.get(url)
print("2. Информация о боте:", response.json())

# 3. Получаем обновления (чтобы очистить очередь)
url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1'
response = requests.get(url)
print("3. Очистка очереди обновлений:", response.json())
