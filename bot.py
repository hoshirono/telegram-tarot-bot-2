import asyncio
import random
import os
import urllib.parse

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# 🔑 токен
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

# 🃏 карты (сразу с норм визуальным смыслом)
CARDS = [
    "Skeleton office manager in suit",
    "Cat prophet with glowing eyes",
    "God of debts on golden throne",
    "Alarm clock demon with fire aura",
    "Cyber dumpling with wifi signal",
    "Surreal meme wizard floating",
    "Dark tarot jester laughing"
]

# 🔮 предсказания
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
    "dark gothic tarot card, ultra detailed, masterpiece",
    "anime tarot card, glowing, beautiful, detailed",
    "surreal absurd tarot card, weirdcore, dreamlike"
]

# 💎 редкость
RARITY = [
    ("обычная", "simple"),
    ("редкая", "glowing magical aura"),
    ("проклятая 😈", "dark horror cursed energy")
]


# 🎨 генерация картинки через Pollinations (БЕСПЛАТНО)
def generate_image(card_name, text, style, rarity):
    prompt = f"""
    tarot card illustration,
    {card_name},
    {text},
    {style},
    {rarity},
    centered composition,
    mystical, highly detailed, dramatic lighting,
    fantasy art, masterpiece
    """

    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
    return url


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

    image_url = generate_image(card, text, style, rarity_prompt)

    caption = f"""
🃏 {card}

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
            caption + "\n⚠️ (арт не загрузился)",
            reply_markup=keyboard
        )


# ⚔️ PvP
@dp.message(lambda m: m.text == "⚔️ PvP")
async def pvp(message: types.Message):
    await message.answer("⚔️ PvP скоро будет 💀", reply_markup=keyboard)


# 🧬 Синтез
@dp.message(lambda m: m.text == "🧬 Синтез")
async def craft(message: types.Message):
    await message.answer("🧬 Синтез карт в разработке 😈", reply_markup=keyboard)


# 📦 Коллекция
@dp.message(lambda m: m.text == "📦 Коллекция")
async def collection(message: types.Message):
    await message.answer("📦 Коллекция пока пустая 😭", reply_markup=keyboard)


# 📊 Стата
@dp.message(lambda m: m.text == "📊 Стата")
async def stats(message: types.Message):
    await message.answer("📊 Стата скоро появится", reply_markup=keyboard)


# 🎁 Дейлик
@dp.message(lambda m: m.text == "🎁 Дейлик")
async def daily(message: types.Message):
    coins = random.randint(50, 200)
    await message.answer(f"🎁 Ты получил {coins} монет 💰", reply_markup=keyboard)


# ▶️ запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())