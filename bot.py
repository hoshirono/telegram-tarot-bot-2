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

# 🧠 текст (локально)
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

# 🎨 генерация картинки с fallback
def generate_image(style, rarity):
    prompt = f"{style}, {rarity}, tarot card, mystical, detailed"
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            file_path = "card.png"
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path

    except Exception as e:
        print("Image error:", e)

    # fallback картинки (если API умер)
    fallback_images = [
        "https://picsum.photos/512",
        "https://placekitten.com/512/512",
        "https://dummyimage.com/512x512/000/fff&text=Tarot"
    ]

    return random.choice(fallback_images)

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
    image_path = generate_image(style, rarity_prompt)

    caption = f"""
🔮 Твоя карта:

🎨 Стиль: {style}
💎 Уровень: {rarity_text}

🧠 {text}
"""

    try:
        # если ссылка
        if isinstance(image_path, str) and image_path.startswith("http"):
            await message.answer_photo(photo=image_path, caption=caption)
        else:
            photo = types.FSInputFile(image_path)
            await message.answer_photo(photo=photo, caption=caption)

    except Exception as e:
        print("Send error:", e)
        await message.answer("⚠️ Ошибка отправки карты, попробуй ещё раз")

# fallback
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Напиши /card 😎")

# запуск
async def main():
    print("🚀 Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())