import asyncio
import random
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔮 Получить карту")]
    ],
    resize_keyboard=True
)

CARDS = [
    "Пельмень Wi-Fi",
    "Скелет-менеджер",
    "Кот-пророк"
]

TEXTS = [
    "Ты выбрал худший путь, и это нормально.",
    "Вселенная в ахуе от тебя.",
    "Ты победишь. Но случайно."
]

IMAGES = [
    "https://picsum.photos/512",
    "https://placekitten.com/512/512",
    "https://placebear.com/512/512"
]

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Бот жив 👀", reply_markup=keyboard)

@dp.message(lambda m: "Получить карту" in m.text)
async def card(message: types.Message):
    name = random.choice(CARDS)
    text = random.choice(TEXTS)
    img = random.choice(IMAGES)

    await message.answer_photo(
        photo=img,
        caption=f"🃏 {name}\n\n🔮 {text}",
        reply_markup=keyboard
    )

async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())