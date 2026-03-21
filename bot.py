import asyncio
import random
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile

# 🔑 ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# 🎴 уникальность
used_cards = set()

# 💎 редкость
RARITY = [
    "обычная",
    "редкая",
    "легендарная",
    "проклятая"
]

# 🎨 стили
STYLES = [
    "dark gothic tarot",
    "anime tarot",
    "surreal tarot",
    "cyberpunk tarot"
]

# 🧠 генерация карты (без OpenAI)
CARD_POOL = [
    ("Бог кредитов", "Ты снова в долгах, но уже красиво."),
    ("Wi-Fi шаман", "Связь нестабильна, как твоя судьба."),
    ("Пельмень судьбы", "Ты варишься в событиях."),
    ("Скелет на подработке", "Ты живешь, но зачем-то работаешь."),
    ("Глаз системы", "За тобой наблюдают."),
    ("Цифровой демон", "Ошибка стала частью тебя."),
    ("Король багов", "Ты управляешь хаосом."),
    ("Сломанный пророк", "Ты знал, но сделал хуже."),
]

def generate_card():
    while True:
        card = random.choice(CARD_POOL)
        if card[0] not in used_cards:
            used_cards.add(card[0])
            return card

# 🎨 генерация картинки через HuggingFace
def generate_image(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": prompt}
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.content


# 🎮 кнопки
def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Крутить")],
            [KeyboardButton(text="📦 Коллекция"), KeyboardButton(text="📊 Стата")],
        ],
        resize_keyboard=True
    )


# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "💀 FREE TAROT\n\nЖми «Крутить»",
        reply_markup=main_keyboard()
    )


# 🎴 генерация
@dp.message(lambda m: m.text == "🎰 Крутить")
async def spin(message: types.Message):
    await message.answer("🎨 Генерирую карту...")

    name, desc = generate_card()
    style = random.choice(STYLES)
    rarity = random.choice(RARITY)

    prompt = f"""
tarot card illustration, {name},
{desc},
style: {style},
beautiful, detailed, centered composition
"""

    try:
        img_bytes = generate_image(prompt)
        photo = BufferedInputFile(img_bytes, filename="card.png")

        caption = f"""
🃏 {name}

💎 {rarity}

🔮 {desc}
"""

        await message.answer_photo(photo=photo, caption=caption)

    except Exception as e:
        print("ERROR:", e)
        await message.answer("⚠️ не удалось сгенерировать арт")


# 🧪 fallback
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Жми 🎰 Крутить")


# ▶️ запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())