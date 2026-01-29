import subprocess
import time
import os
import signal
import sys

def main():
    print("🔴 Останавливаем все процессы бота...")
    os.system("pkill -f 'python.*main'")
    os.system("pkill -f 'python.*bot'")
    time.sleep(3)
    
    print("🟡 Очищаем webhook...")
    token = "7971183338:AAEZm72Md1ZFbpmtG-fmLHdmXzzPsD_GLYI"
    import requests
    requests.get(f"https://api.telegram.org/bot{token}/deleteWebhook")
    
    print("🟢 Запускаем бота...")
    # Запускаем бота как дочерний процесс
    process = subprocess.Popen(
        ["python", "-m", "src.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Выводим логи
    try:
        for line in iter(process.stdout.readline, ''):
            print(line.strip())
    except KeyboardInterrupt:
        print("\n🛑 Останавливаем бота...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()
