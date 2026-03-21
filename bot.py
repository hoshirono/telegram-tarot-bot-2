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

# 💀 ОДНА КНОПКА (кринж)
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💀 получить моральный урон")]
    ],
    resize_keyboard=True
)

# 💀 генерация названия
def generate_name():
    a = ["Обоссанный", "Кринжовый", "Депрессивный", "Позорный", "Wi-Fi", "Бомжовый"]
    b = ["пельмень", "батя", "кредит", "сервер", "мозг", "ноутбук"]
    c = ["судьбы", "позора", "ошибки", "страдания", "провала"]

    return f"{random.choice(a)} {random.choice(b)} {random.choice(c)}"

# 💀 предсказания
PREDICTIONS = [
    "Ты снова всё просрал, но хотя бы стабилен.",
    "Даже случайность работает лучше тебя.",
    "Ты — ошибка, которую даже баг-репорт не спасёт.",
    "Судьба плюнула в тебя и пошла дальше.",
    "Ты идёшь к успеху, но в противоположную сторону.",
    "Ты уже проиграл, просто ещё не понял.",
    "Ты главный NPC своей жизни.",
    "Ты — баг, который не фиксится.",
    "С каждым выбором ты открываешь новое дно.",
    "Ты стал мемом, но никто не смеётся."
]

# 🤡 сцены
EXTRA_SCENES = [
    "man crying in toilet",
    "broken computer screaming",
    "fat angel eating noodles",
    "sad clown with wifi signal",
    "man hugging router",
    "skeleton using laptop"
]

# 🎨 генерация картинки
def generate_image(prompt):
    try:
        url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {"inputs": prompt}

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
    await message.answer("🎨 сейчас тебе станет хуже...")

    name = generate_name()
    prediction = random.choice(PREDICTIONS)
    extra = random.choice(EXTRA_SCENES)

    prompt = f"""
absurd surreal tarot card, cursed image,
{name},
meaning: {prediction},
scene: {extra},
grotesque, glitchcore, weird anatomy,
highly detailed, dramatic lighting
"""

    img = generate_image(prompt)

    caption = f"🃏 {name}\n\n💀 {prediction}"

    if img:
        photo = BufferedInputFile(img, filename="card.png")
        await message.answer_photo(photo=photo, caption=caption)
    else:
        await message.answer("⚠ даже нейросеть отказалась это показывать")

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "💀 добро пожаловать\nты зря сюда зашел",
        reply_markup=keyboard
    )

# 💀 кнопка
@dp.message(lambda msg: msg.text == "💀 получить моральный урон")
async def spin(message: types.Message):
    await generate_card(message)

# 🔥 ВАЖНО: ловим ПЕРВОЕ сообщение
@dp.message()
async def fallback(message: types.Message):
    await message.answer(
        "нажми кнопку и пожалей об этом",
        reply_markup=keyboard
    )

# ▶️ запуск
async def main():
    print("Бот готов ломать психику 💀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())