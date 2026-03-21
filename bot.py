import asyncio
import random
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# 🎮 КНОПКИ (как ты хотел)
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎰 Крутить")],
        [KeyboardButton(text="⚔️ PvP"), KeyboardButton(text="🧬 Синтез")],
        [KeyboardButton(text="📦 Коллекция"), KeyboardButton(text="📊 Стата")],
        [KeyboardButton(text="🎁 Дейлик")]
    ],
    resize_keyboard=True
)

# 🃏 КАРТЫ
CARDS = [
    "Пельмень Wi-Fi",
    "Скелет-менеджер",
    "Кот-пророк",
    "Бог кредитов",
    "Демон будильника",
    "Жрец вайба",
    "Лорд случайных решений"
]

# 🔮 ПРЕДСКАЗАНИЯ (жестче 😈)
TEXTS = [
    "Ты выбрал худший путь, и это нормально.",
    "Вселенная смотрит на тебя и медленно офигевает.",
    "Ты победишь. Но это будет максимально тупо.",
    "Сегодня ты сломаешь что-то важное. Возможно себя.",
    "Ты уже облажался. Осталось принять это красиво.",
    "Судьба дала тебе шанс. Ты его проигнорируешь.",
    "Ты легенда. Но в плохом смысле."
]

# 🖼 БОЛЬШОЙ ПУЛ КАРТИНОК (разные)
IMAGES = [
    "https://picsum.photos/seed/1/512",
    "https://picsum.photos/seed/2/512",
    "https://picsum.photos/seed/3/512",
    "https://picsum.photos/seed/4/512",
    "https://picsum.photos/seed/5/512",
    "https://picsum.photos/seed/6/512",
    "https://picsum.photos/seed/7/512",
    "https://picsum.photos/seed/8/512",
    "https://picsum.photos/seed/9/512",
    "https://picsum.photos/seed/10/512"
]

# чтобы не повторялись подряд
last_image = None


def get_unique_image():
    global last_image
    img = random.choice(IMAGES)

    while img == last_image:
        img = random.choice(IMAGES)

    last_image = img
    return img


# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "💀 ULTIMATE TAROT ONLINE\n\nВыбирай действие 👇",
        reply_markup=keyboard
    )


# 🎰 крутка
@dp.message(lambda m: m.text == "🎰 Крутить")
async def spin(message: types.Message):
    await message.answer("🎨 Генерирую карту...")

    card = random.choice(CARDS)
    text = random.choice(TEXTS)
    img = get_unique_image()

    await message.answer_photo(
        photo=img,
        caption=f"🃏 {card}\n\n🔮 {text}",
        reply_markup=keyboard
    )


# ⚔️ PvP
@dp.message(lambda m: m.text == "⚔️ PvP")
async def pvp(message: types.Message):
    await message.answer("⚔️ PvP скоро будет 💀", reply_markup=keyboard)


# 🧬 Синтез
@dp.message(lambda m: m.text == "🧬 Синтез")
async def craft(message: types.Message):
    await message.answer("🧬 Синтез карт в разработке 😈", reply_markup=keyboard)


# 📦 Коллекция
@dp.message(lambda m: m.text == "📦 Коллекция")
async def collection(message: types.Message):
    await message.answer("📦 У тебя пока нет коллекции 😭", reply_markup=keyboard)


# 📊 Стата
@dp.message(lambda m: m.text == "📊 Стата")
async def stats(message: types.Message):
    await message.answer("📊 Стата скоро появится", reply_markup=keyboard)


# 🎁 Дейлик
@dp.message(lambda m: m.text == "🎁 Дейлик")
async def daily(message: types.Message):
    coins = random.randint(50, 200)
    await message.answer(f"🎁 Ты получил {coins} монет 💰", reply_markup=keyboard)


# ▶️ запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())