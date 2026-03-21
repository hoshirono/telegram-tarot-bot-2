import asyncio
import random
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile

# 🔑 переменные
TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

if not TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN не найден")

if not HF_TOKEN:
    raise Exception("❌ HF_TOKEN не найден")

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

# 💀 генерация названия
def generate_name():
    a = ["Проклятый", "Сломанный", "Кринжовый", "Цифровой", "Бесполезный", "Гнилой", "Wi-Fi", "Легендарный"]
    b = ["хомяк", "кредит", "долг", "батя", "пельмень", "сервер", "бот", "разум"]
    c = ["судьбы", "позора", "ошибки", "провала", "страдания"]

    return f"{random.choice(a)} {random.choice(b)} {random.choice(c)}"

# 🧠 предсказания (жёсткие)
PREDICTIONS = [
    "Ты выбрал худший путь, и уже не свернёшь.",
    "Ты опять всё испортил. Удивительно стабильно.",
    "Судьба дала шанс, но ты его не понял.",
    "Ты идёшь вперёд, но в сторону дна.",
    "Даже этот бот в тебя не верит.",
    "Ты — главный баг в своей жизни.",
    "Поздравляю, ты сам себе проблема.",
    "Станет хуже. Намного хуже.",
    "Ты уже проиграл, просто ещё не понял.",
    "Это не знак. Это приговор."
]

# 🎨 генерация картинки
def generate_image(prompt):
    try:
        url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code != 200:
            print("HF ERROR:", response.text)
            return None

        return response.content

    except Exception as e:
        print("CRASH:", e)
        return None

# 🎴 генерация карты
async def generate_card(message: types.Message):
    await message.answer("🎨 Генерирую карту...")

    name = generate_name()
    prediction = random.choice(PREDICTIONS)

    prompt = f"""
tarot card, dark fantasy, absurd surreal,
{name},
meaning: {prediction},
highly detailed, dramatic lighting, masterpiece
"""

    img = generate_image(prompt)

    caption = f"🃏 {name}\n\n💀 {prediction}"

    if img:
        photo = BufferedInputFile(img, filename="card.png")
        await message.answer_photo(photo=photo, caption=caption)
    else:
        await message.answer("⚠ не удалось сгенерировать арт")

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("💀 ULTIMATE TAROT ONLINE", reply_markup=keyboard)

# 🎰 крутить
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