import asyncio
import random
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🎮 кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎰 Крутить")],
        [KeyboardButton(text="⚔ PvP"), KeyboardButton(text="🧬 Синтез")],
        [KeyboardButton(text="📊 Стата"), KeyboardButton(text="🎁 Дейлик")]
    ],
    resize_keyboard=True
)

# 💀 генерация названия карты (кринж)
def generate_name():
    parts1 = ["Сломанный", "Криповый", "Проклятый", "Wi-Fi", "Цифровой", "Легендарный", "Жирный", "Бесполезный"]
    parts2 = ["хомяк", "кредит", "долг", "сигнал", "батя", "пельмень", "сервер", "бот"]
    parts3 = ["судьбы", "разочарования", "ошибки", "позора", "провала"]

    return f"{random.choice(parts1)} {random.choice(parts2)} {random.choice(parts3)}"

# 🧠 предсказания (жесткие)
PREDICTIONS = [
    "Ты выбрал худший путь, но уже поздно отступать.",
    "Судьба орёт тебе в лицо, но ты всё равно тупишь.",
    "Ты опять сделал не тот выбор. Как обычно.",
    "Вселенная дала тебе шанс, но ты его просрал.",
    "Ты идёшь вперёд… но в сторону дна.",
    "Поздравляю, ты сам себе главный враг.",
    "Даже этот бот в тебя не верит.",
    "Ты не на том пути. И не в той жизни.",
    "Скоро будет хуже. Намного хуже.",
    "Ты уже проиграл, просто ещё не понял.",
    "Это знак. Плохой знак.",
    "Ты думаешь это случайность? Нет, это ты кривой."
]

# 🎨 генерация картинки (новый HF API)
def generate_image(prompt):
    url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "blurry, bad quality, text, watermark",
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("HF ERROR:", response.text)
        return None

    return response.content

# 🎴 генерация карты
async def generate_card(message: types.Message):
    await message.answer("🎨 Генерирую карту...")

    name = generate_name()
    prediction = random.choice(PREDICTIONS)

    prompt = f"""
tarot card illustration, dark fantasy, absurd surreal,
{name},
meaning: {prediction},
highly detailed, mystical, professional art
"""

    img = generate_image(prompt)

    caption = f"""
🃏 {name}

💀 {prediction}
"""

    if img:
        await message.answer_photo(photo=img, caption=caption)
    else:
        await message.answer("⚠ не удалось сгенерировать арт")

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("💀 ULTIMATE TAROT", reply_markup=keyboard)

# 🎰 кнопка крутить
@dp.message(lambda msg: msg.text == "🎰 Крутить")
async def spin(message: types.Message):
    await generate_card(message)

# 🧪 fallback
@dp.message()
async def other(message: types.Message):
    await message.answer("Жми 🎰 Крутить")

# ▶️ запуск
async def main():
    print("Бот жив 💀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())