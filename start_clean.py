import os
import subprocess
import time
import requests

# 1. Убиваем все Python процессы
print("🛑 Останавливаем все процессы Python...")
os.system("pkill -9 -f python")

# 2. Ожидаем
time.sleep(3)

# 3. Очищаем webhook
print("🔄 Очищаем webhook...")
TOKEN = "7971183338:AAEZm72Md1ZFbpmtG-fmLHdmXzzPsD_GLYI"
requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")

# 4. Запускаем бота
print("🚀 Запускаем бота...")
os.system("python -m src.main")
