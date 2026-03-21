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

# 🧠 память (чтобы не повторялось)
used = set()

# 🎮 кнопки
def keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 КРУТИТЬ КРИНЖ")]
        ],
        resize_keyboard=True
    )

# 💀 генерация названия
def generate_name():
    words1 = ["Цифровой", "Проклятый", "Кринжовый", "Гнилой", "Wi-Fi", "Космический", "Депрессивный", "Сломанный"]
    words2 = ["пельмень", "демон", "пророк", "дедлайн", "шаман", "бот", "кредит", "скелет"]
    words3 = ["судьбы", "хаоса", "позора", "интернета", "разложения", "вечности"]

    return f"{random.choice(words1)} {random.choice(words2)} {random.choice(words3)}"

# 🤡 генерация предсказания (максимальный кринж)
def generate_text():
    texts = [
        "Ты опять сделал всё неправильно. И да, все это видели.",
        "Судьба кричит тебе 'остановись', но ты уже купил подписку.",
        "Ты не главный герой. Ты тот самый NPC с багом.",
        "Ты выбрал путь... и это был худший из всех.",
        "Даже рандом был против тебя.",
        "Ты не проиграл. Ты унизился.",
        "Вселенная устала от тебя раньше, чем ты от неё.",
        "Это не дно. Это поддно.",
        "Ты сейчас там, где даже судьба не ожидала тебя увидеть.",
        "Твоя энергия: забытый пароль от жизни."
    ]
    return random.choice(texts)

# 🎴 генерация уникальной карты
def generate_card():
    while True:
        name = generate_name()
        text = generate_text()
        key = name + text

        if key not in used:
            used.add(key)
            return name, text

# 🎨 генерация картинки
def generate_image(name, desc):
    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    prompt = f"""
Tarot card illustration.

Card title: {name}

Scene:
A surreal absurd scene that represents:
{desc}

Style:
- extremely absurd
- cursed meme energy
- grotesque humor
- dramatic composition
- tarot card frame
- exaggerated emotions
- weird symbols
- dark humor
- slightly humiliating

IMPORTANT:
- image MUST reflect meaning
- no random animals
- clear concept
"""

    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "inputs": prompt,
            "options": {"wait_for_model": True}
        },
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.content

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("💀 CRINGE TAROT\n\nЖми кнопку", reply_markup=keyboard())

# 🎰 кнопка
@dp.message(lambda m: m.text == "🎰 КРУТИТЬ КРИНЖ")
async def spin(message: types.Message):
    await message.answer("🎨 Генерирую максимальный кринж...")

    name, text = generate_card()

    try:
        img = generate_image(name, text)
        photo = BufferedInputFile(img, filename="card.png")

        await message.answer_photo(
            photo=photo,
            caption=f"🃏 {name}\n\n🤡 {text}"
        )

    except Exception as e:
        print(e)
        await message.answer("⚠️ даже кринж не смог родиться... попробуй ещё")

# fallback
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Жми кнопку ↓", reply_markup=keyboard())

# ▶️ запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())