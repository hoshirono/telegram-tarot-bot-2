import asyncio
import random
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

used_cards = set()

CARD_POOL = [
    ("Бог кредитов", "Ты снова в долгах, но уже красиво."),
    ("Wi-Fi шаман", "Связь нестабильна, как твоя судьба."),
    ("Пельмень судьбы", "Ты варишься в событиях."),
    ("Скелет на подработке", "Ты живешь, но зачем-то работаешь."),
    ("Глаз системы", "За тобой наблюдают."),
    ("Цифровой демон", "Ошибка стала частью тебя."),
]

def generate_card():
    while True:
        card = random.choice(CARD_POOL)
        if card[0] not in used_cards:
            used_cards.add(card[0])
            return card

def generate_image(prompt):
    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

    if response.status_code != 200:
        raise Exception(response.text)

    return response.content


def keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Крутить")],
            [KeyboardButton(text="📦 Коллекция"), KeyboardButton(text="📊 Стата")]
        ],
        resize_keyboard=True
    )


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("💀 FREE TAROT", reply_markup=keyboard())


@dp.message(lambda m: m.text == "🎰 Крутить")
async def spin(message: types.Message):
    await message.answer("🎨 Генерирую карту...")

    name, desc = generate_card()

    prompt = f"""
tarot card, {name},
{desc},
beautiful tarot illustration,
centered composition,
detailed, fantasy art
"""

    try:
        img = generate_image(prompt)
        photo = BufferedInputFile(img, filename="card.png")

        await message.answer_photo(
            photo=photo,
            caption=f"🃏 {name}\n\n🔮 {desc}"
        )

    except Exception as e:
        print(e)
        await message.answer("⚠️ не удалось сгенерировать арт")


@dp.message()
async def fallback(message: types.Message):
    await message.answer("Жми 🎰 Крутить")


async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())