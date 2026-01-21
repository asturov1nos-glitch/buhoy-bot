FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY src/ ./src/

# Создаем папки
RUN mkdir -p /tmp /app/data

# Указываем порт
EXPOSE 8080

# Запускаем бота
CMD ["python", "-m", "src.main"]