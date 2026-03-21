import asyncio
import random
import os
import base64

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from openai import OpenAI

# 🔑 ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

# 🎴 уникальность
used_cards = set()

# 🎨 стили
STYLES = [
    "dark gothic tarot",
    "anime tarot masterpiece",
    "surreal absurd tarot art",
    "cyberpunk mystical tarot",
]

# 💎 редкость
RARITY = [
    ("обычная", "common"),
    ("редкая", "rare"),
    ("легендарная", "legendary"),
    ("проклятая 😈", "cursed")
]

# 🧠 генерация карты (название + смысл)
def generate_card_data():
    prompt = """
Придумай ОДНУ уникальную карту таро.

Формат строго:
Название: ...
Описание: ...

Правила:
- название должно быть абсурдным, но звучать как карта таро
- описание короткое (1 строка)
- не повторяй классические карты
- можно мемы, абсурд, темный юмор
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = res.choices[0].message.content

    try:
        name = text.split("Название:")[1].split("Описание:")[0].strip()
        desc = text.split("Описание:")[1].strip()
    except:
        name = "Сломанная реальность"
        desc = "Что-то пошло не так, но уже поздно."

    return name, desc


# 🎨 генерация картинки (ИСПРАВЛЕНО)
def generate_image_bytes(name, desc, style, rarity):
    prompt = f"""
Tarot card illustration.

Card name: {name}
Meaning: {desc}

Style: {style}
Rarity: {rarity}

Requirements:
- BEAUTIFUL detailed tarot card
- centered composition
- fantasy illustration
- high quality
- no random objects
- MUST match the meaning and name
- no chaos, coherent scene
"""

    img = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    # 🔥 ВАЖНО: берем base64
    image_base64 = img.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    return image_bytes


# 🎮 кнопки
def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Крутить")],
            [KeyboardButton(text="📦 Коллекция"), KeyboardButton(text="📊 Стата")],
            [KeyboardButton(text="🎁 Дейлик")]
        ],
        resize_keyboard=True
    )


# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "💀 ULTIMATE TAROT ONLINE\n\nНажми «Крутить»",
        reply_markup=main_keyboard()
    )


# 🎴 генерация карты
@dp.message(lambda m: m.text == "🎰 Крутить")
async def spin(message: types.Message):
    await message.answer("🎨 Генерирую карту...")

    style = random.choice(STYLES)
    rarity_text, rarity_key = random.choice(RARITY)

    # уникальная карта
    for _ in range(10):
        name, desc = generate_card_data()
        if name not in used_cards:
            used_cards.add(name)
            break

    try:
        img_bytes = generate_image_bytes(name, desc, style, rarity_key)

        photo = BufferedInputFile(img_bytes, filename="card.png")

        caption = f"""
🃏 {name}

💎 Редкость: {rarity_text}

🔮 {desc}
"""

        await message.answer_photo(photo=photo, caption=caption)

    except Exception as e:
        print("ERROR:", e)
        await message.answer("⚠️ арт не загрузился, попробуй ещё раз")


# 🧪 fallback
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Нажми 🎰 Крутить")


# ▶️ запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())