import asyncio
import random
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# загрузка переменных
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# проверка токена
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN не найден!")

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

# 🧠 генерация текста (локально, без API)
def generate_text():
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

# 🎨 генерация картинки (через Pollinations)
def generate_image(style, rarity):
    prompt = f"{style}, {rarity}, tarot card, mystical, detailed, high quality"
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

    response = requests.get(url, timeout=15)

    if response.status_code != 200:
        raise Exception("Ошибка генерации картинки")

    file_path = "card.png"

    with open(file_path, "wb") as f:
        f.write(response.content)

    return file_path

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("🔮 Нажми /card чтобы получить карту судьбы")

# 🎴 команда карты
@dp.message(lambda message: message.text == "/card")
async def card(message: types.Message):
    await message.answer("🔮 Твоя карта генерируется...")

    style = random.choice(STYLES)
    rarity_text, rarity_prompt = random.choice(RARITY)

    text = generate_text()

    try:
        image_path = generate_image(style, rarity_prompt)

        photo = types.FSInputFile(image_path)

        caption = f"""
🔮 Твоя карта:

🎨 Стиль: {style}
💎 Уровень: {rarity_text}

🧠 {text}
"""

        await message.answer_photo(photo=photo, caption=caption)

    except Exception as e:
        print("ERROR:", e)
        await message.answer("⚠️ Карта не смогла проявиться... Попробуй ещё раз")

# fallback
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Напиши /card 😎")

# ▶️ запуск
async def main():
    print("🚀 Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())