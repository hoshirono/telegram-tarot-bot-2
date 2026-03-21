import asyncio
import random
import os

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

# 🧠 текст
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

# 🎨 генерация ссылки (без скачивания!)
def generate_image_url(style, rarity):
    prompt = f"{style}, {rarity}, tarot card, mystical, detailed"
    return f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

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

    text = generate_text()
    image_url = generate_image_url(style, rarity_prompt)

    caption = f"""
🔮 Твоя карта:

🎨 Стиль: {style}
💎 Уровень: {rarity_text}

🧠 {text}
"""

    try:
        # ⏱️ жесткий таймаут 10 сек
        await asyncio.wait_for(
            message.answer_photo(photo=image_url, caption=caption),
            timeout=10
        )

    except asyncio.TimeoutError:
        await message.answer("⚠️ Генерация заняла слишком долго, попробуй ещё раз")

    except Exception as e:
        print("ERROR:", e)

        # fallback картинка
        fallback = "https://picsum.photos/512"

        await message.answer_photo(photo=fallback, caption=caption)

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