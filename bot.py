import asyncio
import random
import os
import urllib.parse
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# 🎮 кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎰 Крутить")],
        [KeyboardButton(text="⚔️ PvP"), KeyboardButton(text="🧬 Синтез")],
        [KeyboardButton(text="📦 Коллекция"), KeyboardButton(text="📊 Стата")],
        [KeyboardButton(text="🎁 Дейлик")]
    ],
    resize_keyboard=True
)

# 🃏 карты
CARDS = [
    "Skeleton office manager in suit",
    "Cat prophet with glowing eyes",
    "God of debts on golden throne",
    "Alarm clock demon with fire aura",
    "Cyber dumpling with wifi signal",
    "Surreal meme wizard floating",
    "Dark tarot jester laughing"
]

# 🔮 тексты
TEXTS = [
    "Ты выбрал худший путь, и это нормально.",
    "Вселенная наблюдает за тобой с недоумением.",
    "Ты победишь. Но максимально странным способом.",
    "Сегодня ты сделаешь ошибку. И это тебя спасёт.",
    "Ты уже зашёл слишком далеко. Продолжай.",
    "Судьба дала тебе шанс, но ты его не заметил.",
    "Ты станешь легендой. Но не так как хотел."
]

# 🎨 стили
STYLES = [
    "dark gothic tarot card",
    "anime tarot card",
    "surreal weird tarot card"
]

# 💎 редкость
RARITY = [
    ("обычная", "simple"),
    ("редкая", "glowing magical aura"),
    ("проклятая 😈", "dark horror cursed energy")
]


# 🎨 генерация URL
def generate_image_url(card, text, style, rarity):
    prompt = f"""
    tarot card, {card}, {text}, {style}, {rarity},
    centered composition, detailed, fantasy, masterpiece
    """
    return "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)


# 📥 скачивание картинки
def download_image(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.content
    except:
        return None


# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "💀 ULTIMATE TAROT ONLINE\n\nВыбирай действие 👇",
        reply_markup=keyboard
    )


# 🎰 крутка
@dp.message(lambda m: m.text == "🎰 Крутить")
async def spin(message: types.Message):
    await message.answer("🎨 Генерирую карту...")

    card = random.choice(CARDS)
    text = random.choice(TEXTS)
    style = random.choice(STYLES)
    rarity_text, rarity_prompt = random.choice(RARITY)

    url = generate_image_url(card, text, style, rarity_prompt)

    # ⬇️ скачиваем
    image_bytes = download_image(url)

    caption = f"""
🃏 {card}

💎 Редкость: {rarity_text}

🔮 {text}
"""

    if image_bytes:
        await message.answer_photo(
            photo=types.BufferedInputFile(image_bytes, filename="card.png"),
            caption=caption,
            reply_markup=keyboard
        )
    else:
        await message.answer(
            caption + "\n⚠️ арт не загрузился",
            reply_markup=keyboard
        )


# остальные кнопки
@dp.message(lambda m: m.text == "⚔️ PvP")
async def pvp(message: types.Message):
    await message.answer("⚔️ PvP скоро будет", reply_markup=keyboard)

@dp.message(lambda m: m.text == "🧬 Синтез")
async def craft(message: types.Message):
    await message.answer("🧬 Синтез в разработке", reply_markup=keyboard)

@dp.message(lambda m: m.text == "📦 Коллекция")
async def collection(message: types.Message):
    await message.answer("📦 Коллекция пока пустая", reply_markup=keyboard)

@dp.message(lambda m: m.text == "📊 Стата")
async def stats(message: types.Message):
    await message.answer("📊 Скоро будет", reply_markup=keyboard)

@dp.message(lambda m: m.text == "🎁 Дейлик")
async def daily(message: types.Message):
    coins = random.randint(50, 200)
    await message.answer(f"🎁 +{coins} монет", reply_markup=keyboard)


# ▶️ запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())