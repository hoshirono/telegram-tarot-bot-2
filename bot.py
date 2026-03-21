import logging
import random
import os

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)

# === ТОКЕН ИЗ RAILWAY VARIABLES ===
API_TOKEN = os.getenv("TELEGRAM_TOKEN")

# === БОТ ===
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# === СТИЛИ ===
STYLES = [
    "dark tarot",
    "cute anime tarot",
    "absurd meme tarot"
]

# === УРОВНИ ===
LEVELS = [
    "обычная карта",
    "редкая карта",
    "проклятая 😈"
]

# === КОМАНДА /start ===
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "🔮 Привет! Напиши любое сообщение — я вытащу тебе карту таро."
    )

# === ЛЮБОЕ СООБЩЕНИЕ ===
@dp.message_handler()
async def tarot(message: types.Message):
    style = random.choice(STYLES)
    level = random.choice(LEVELS)

    text = f"""
🔮 Твоя карта:

🎨 Стиль: {style}
🧠 Уровень: {level}
"""

    await message.answer(text)

# === ЗАПУСК ===
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)