import logging
import random
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

client = OpenAI(api_key=OPENAI_API_KEY)

# ===== СТИЛИ =====
STYLES = [
    "dark tarot",
    "cute anime tarot",
    "absurd meme tarot"
]

# ===== РЕДКОСТЬ =====
def get_rarity():
    roll = random.randint(1, 100)
    if roll <= 70:
        return "обычная карта"
    elif roll <= 95:
        return "редкая карта"
    else:
        return "проклятая 😈"

# ===== КНОПКИ =====
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    KeyboardButton("❤️ Любовь"),
    KeyboardButton("💰 Деньги"),
    KeyboardButton("🔮 Будущее")
)

# ===== GPT ТЕКСТ =====
def generate_text(theme, rarity):
    prompt = f"""
Ты мистический таролог.

Тема: {theme}
Редкость карты: {rarity}

Сделай короткое, атмосферное предсказание (1-2 предложения).
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ===== СТАРТ =====
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "🔮 Выбери тему гадания:",
        reply_markup=menu
    )

# ===== ОБРАБОТКА КНОПОК =====
@dp.message_handler(lambda message: message.text in ["❤️ Любовь", "💰 Деньги", "🔮 Будущее"])
async def tarot(message: types.Message):
    theme = message.text
    style = random.choice(STYLES)
    rarity = get_rarity()

    await message.answer("🔮 Вытягиваю карту...")

    # === текст от GPT ===
    text_msg = generate_text(theme, rarity)

    # === картинка ===
    prompt = f"{style}, tarot card about {theme}, {rarity}, mystical, detailed"

    image = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    image_url = image.data[0].url

    caption = f"""
🎴 {theme}

🎨 Стиль: {style}
🧠 Редкость: {rarity}

💬 {text_msg}
"""

    await message.answer_photo(photo=image_url, caption=caption)

# ===== ЗАПУСК =====
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)