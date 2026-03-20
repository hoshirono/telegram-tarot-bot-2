import requests
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

meanings = [
    "ты сегодня ничего не сделаешь",
    "удача рядом, но ты её проигнорируешь",
    "всё получится, но не сегодня",
    "ты снова залипнешь в телефоне",
    "сегодня день странных решений",
    "ты избежишь работы любым способом",
    "мотивация придёт... но не к тебе",
    "вселенная пыталась, но ты сильнее",
]

def generate_image(prompt):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    return response.content

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer("🔮 Напиши /card чтобы получить мем-карту дня")

@dp.message_handler(commands=['card'])
async def card(msg: types.Message):
    meaning = random.choice(meanings)

    prompt = f"tarot card, surreal meme, {meaning}, dramatic lighting, detailed, digital art"

    image_bytes = generate_image(prompt)

    with open("card.png", "wb") as f:
        f.write(image_bytes)

    with open("card.png", "rb") as photo:
        await msg.answer_photo(photo, caption=f"🔮 {meaning}")

if __name__ == "__main__":
    executor.start_polling(dp)