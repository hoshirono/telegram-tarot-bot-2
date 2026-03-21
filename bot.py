import asyncio
import random
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# загружаем переменные
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# 🎨 стили
STYLES = [
    "dark tarot",
    "cute anime tarot",
    "absurd meme tarot"
]

# 💎 редкость
RARITY = [
    ("обычная карта", "soft mystical tarot"),
    ("редкая карта", "detailed glowing tarot"),
    ("проклятая 😈", "dark cursed horror tarot")
]

# 🧠 генерация текста (без API)
def generate_text(style, rarity):
    texts = [
        "Судьба шепчет: перемены уже рядом.",
        "Ты стоишь на пороге нового пути.",
        "Тень прошлого влияет на твой выбор.",
        "Удача скрыта там, где ты не ищешь.",
        "Остерегайся иллюзий и ложных надежд.",
        "Скоро откроется истина, которую ты ждал.",
        "Сила внутри тебя сильнее, чем ты думаешь."
    ]
    return random.choice(texts)

# 🎨 генерация картинки (Pollinations)
def generate_image(style, rarity):
    prompt = f"{style}, {rarity}, tarot card, mystical, detailed, high quality"
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

    response = requests.get(url, timeout=20)

    with open("card.png", "wb") as f:
        f.write(response.content)

    return "card.png"

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("🔮 Нажми /card чтобы получить карту судьбы")

# 🎴 карта
@dp.message(lambda message: message.text == "/card")
async def card(message: types.Message):
    await message.answer("🔮 Твоя карта генерируется...")

    style = random.choice(STYLES)
    rarity_text, rarity_prompt = random.choice(RARITY)

    text = generate_text(style, rarity_text)
    image_url = generate_image(style, rarity_prompt)

    caption = f"""
🔮 Твоя карта:

🎨 Стиль: {style}
💎 Уровень: {rarity_text}

🧠 {text}
"""

    await message.answer_photo(photo=image_url, caption=caption)

# fallback
@dp.message()
async def test(message: types.Message):
    await message.answer("Напиши /card 😎")

# запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())def generate_image(style, rarity):
    prompt = f"{style}, {rarity}, tarot card, mystical, detailed, high quality"
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
    return url