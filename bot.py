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
        [KeyboardButton(text="🎰 Крутить")]
    ],
    resize_keyboard=True
)

# 💀 генерация названия
def generate_name():
    a = ["Обоссанный", "Кринжовый", "Депрессивный", "Цифровой", "Позорный", "Гнилой", "Wi-Fi", "Бомжовый"]
    b = ["пельмень", "батя", "кредит", "сервер", "хомяк", "мозг", "бот", "ноутбук"]
    c = ["судьбы", "позора", "ошибки", "страдания", "долга", "провала"]

    return f"{random.choice(a)} {random.choice(b)} {random.choice(c)}"

# 💀 предсказания (макс кринж)
PREDICTIONS = [
    "Ты снова всё просрал, но хотя бы стабилен.",
    "Даже случайность работает лучше тебя.",
    "Ты — ошибка, которую даже баг-репорт не спасёт.",
    "Судьба плюнула в тебя и пошла дальше.",
    "Ты идёшь к успеху, но в противоположную сторону.",
    "Твоя жизнь — это туториал, который ты не прошёл.",
    "Ты уже проиграл, просто ещё не осознал масштаб.",
    "Даже этот бот устал от тебя.",
    "Ты выбрал путь, но путь не выбрал тебя.",
    "Поздравляю, ты главный NPC своей жизни.",
    "Ты настолько лишний, что даже рандом тебя игнорит.",
    "Тебя не прокляли — ты просто такой.",
    "Судьба пыталась, но ты сильнее.",
    "Ты — баг, который не фиксится.",
    "Тебя даже карма обходит стороной.",
    "Ты — редкий дроп, но бесполезный.",
    "Ты внизу, и копаешь ещё глубже.",
    "С каждым выбором ты открываешь новое дно.",
    "Ты не провалился — ты провалился красиво.",
    "Ты стал мемом, но никто не смеётся."
]

# 🤡 дополнительный абсурд
EXTRA_SCENES = [
    "man crying in toilet",
    "broken computer screaming",
    "fat angel eating noodles",
    "sad clown with wifi signal",
    "man hugging router",
    "skeleton using laptop",
    "weird creature in office",
    "depressed anime boy in supermarket"
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
    await message.answer("🎨 Генерирую кринж-карту...")

    name = generate_name()
    prediction = random.choice(PREDICTIONS)
    extra = random.choice(EXTRA_SCENES)

    prompt = f"""
absurd surreal tarot card, ultra weird, cursed image,
{name},
visual metaphor: {prediction},

scene: {extra},

grotesque, glitchcore, meme energy,
distorted anatomy, смешанные объекты,
uncomfortable, embarrassing, cursed vibe,

highly detailed, cinematic lighting, masterpiece, 4k
"""

    img = generate_image(prompt)

    caption = f"🃏 {name}\n\n💀 {prediction}"

    if img:
        photo = BufferedInputFile(img, filename="card.png")
        await message.answer_photo(photo=photo, caption=caption)
    else:
        await message.answer("⚠ не удалось сгенерировать арт (мир спас тебя от этого ужаса)")

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("💀 КРИНЖ ТАРО АКТИВИРОВАНО", reply_markup=keyboard)

# 🎰 кнопка
@dp.message(lambda msg: msg.text == "🎰 Крутить")
async def spin(message: types.Message):
    await generate_card(message)

# fallback
@dp.message()
async def other(message: types.Message):
    await message.answer("Жми 🎰 Крутить")

# ▶️ запуск
async def main():
    print("Бот жив и унижает пользователей 💀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())