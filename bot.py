import asyncio
import random
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from openai import OpenAI

# 🔑 ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

# 🎮 кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔮 Получить карту")],
        [KeyboardButton(text="📦 Моя коллекция")]
    ],
    resize_keyboard=True
)

# 🎨 стили
STYLES = [
    "dark gothic tarot card, ultra detailed, masterpiece",
    "cute anime tarot card, glowing, beautiful",
    "absurd meme tarot card, surreal, weirdcore"
]

# 💎 редкость
RARITY = [
    ("обычная", "simple"),
    ("редкая", "rare glowing"),
    ("проклятая 😈", "dark cursed horror")
]

# 🃏 названия карт
CARDS = [
    "Пельмень Wi-Fi",
    "Скелет-менеджер",
    "Кот-пророк",
    "Бог кредитов",
    "Демон будильника",
    "Жрец вайба",
    "Лорд случайных решений"
]

# 🧠 тексты (быстро и без зависаний)
PREDICTIONS = [
    "Ты выбрал худший путь, и это нормально.",
    "Сегодня ты сделаешь странное решение. Оно сработает.",
    "Кто-то думает о тебе. И это подозрительно.",
    "Вселенная в шоке от твоих действий.",
    "Ты победишь… но зачем?",
    "Ошибка станет твоей суперсилой.",
    "Ты уже всё сломал. Осталось насладиться."
]

# 🖼 fallback картинки (если API не дал результат)
FALLBACK_IMAGES = [
    "https://picsum.photos/512",
    "https://placekitten.com/512/512",
    "https://placebear.com/512/512"
]


# 🎨 генерация картинки
async def generate_image(prompt):
    try:
        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        return img.data[0].url
    except Exception as e:
        print("Ошибка генерации картинки:", e)
        return random.choice(FALLBACK_IMAGES)


# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "💀 ULTIMATE TAROT ONLINE\n\nНажми кнопку ниже 👇",
        reply_markup=keyboard
    )


# 🔮 карта
@dp.message(lambda m: m.text == "🔮 Получить карту" or m.text == "/card")
async def card(message: types.Message):
    await message.answer("🎨 Генерирую карту...")

    style = random.choice(STYLES)
    rarity_text, rarity_prompt = random.choice(RARITY)
    card_name = random.choice(CARDS)
    text = random.choice(PREDICTIONS)

    prompt = f"""
    tarot card, {card_name},
    {style},
    {rarity_prompt},
    mystical, detailed, high quality, centered composition
    """

    image_url = await generate_image(prompt)

    caption = f"""
🃏 {card_name}

💎 Редкость: {rarity_text}

🔮 {text}
"""

    try:
        await message.answer_photo(
            photo=image_url,
            caption=caption,
            reply_markup=keyboard
        )
    except:
        await message.answer(
            caption + "\n⚠️ (картинка не загрузилась)",
            reply_markup=keyboard
        )


# 📦 коллекция (заглушка)
@dp.message(lambda m: m.text == "📦 Моя коллекция")
async def collection(message: types.Message):
    await message.answer("📦 Коллекция пока в разработке 😈", reply_markup=keyboard)


# ▶️ запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())