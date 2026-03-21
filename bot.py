import asyncio
import random
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from openai import OpenAI

# 🔑 ключи из Railway
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🤖 клиенты
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

# 🎨 стили
STYLES = [
    "dark tarot",
    "cute anime tarot",
    "absurd meme tarot"
]

# 💎 редкость
RARITY = [
    ("обычная карта", "common"),
    ("редкая карта", "rare"),
    ("проклятая 😈", "cursed")
]

# 🧠 генерация текста
def generate_text(style, rarity):
    prompt = f"""
Ты мистический таролог.

Создай короткое предсказание для таро карты.
Стиль: {style}
Редкость: {rarity}

Сделай текст атмосферным, загадочным и коротким (1-2 предложения).
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# 🎨 генерация картинки
def generate_image(style, rarity):
    prompt = f"{style}, tarot card, {rarity}, mystical, detailed, high quality"

    img = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    return img.data[0].url


# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("🔮 Нажми /card чтобы получить карту судьбы")


# 🎴 команда карты
@dp.message(lambda message: message.text == "/card")
async def card(message: types.Message):
    await message.answer("🔮 Твоя карта генерируется...")

    style = random.choice(STYLES)
    rarity_text, rarity_key = random.choice(RARITY)

    # генерим
    text = generate_text(style, rarity_text)
    image_url = generate_image(style, rarity_key)

    caption = f"""
🔮 Твоя карта:

🎨 Стиль: {style}
💎 Уровень: {rarity_text}

🧠 {text}
"""

    await message.answer_photo(photo=image_url, caption=caption)


# 🧪 тест
@dp.message()
async def test(message: types.Message):
    await message.answer("Напиши /card 😎")


# ▶️ запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())