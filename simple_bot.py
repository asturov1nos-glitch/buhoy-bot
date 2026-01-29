import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ВАШ ТОКЕН (замените на реальный)
TOKEN = "7971183338:AAHcLoNGZkuF9VOfEGirGKwQvR5mz2lySRc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Простой обработчик старта
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"User {message.from_user.id} started bot")
    await message.answer("✅ Бот работает! Напишите что-нибудь.")

# Обработчик всех сообщений
@dp.message()
async def echo(message: types.Message):
    logger.info(f"User {message.from_user.id} said: {message.text}")
    await message.answer(f"Вы написали: {message.text}")

async def main():
    logger.info("🚀 Запуск ПРОСТОГО бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
