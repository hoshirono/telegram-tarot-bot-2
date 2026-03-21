import asyncio
import random
import os
import time
from io import BytesIO

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.enums import ChatAction

TOKEN = os.getenv("TELEGRAM_TOKEN")
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_memory = {}
user_level = {}
active_users = set()

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="💀 узнать правду")]],
    resize_keyboard=True
)

PHOTO_QUERIES = [
    "creepy dark person",
    "abandoned horror building",
    "shadow figure night",
]

FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1509248961158-e54f6934749c",
    "https://images.unsplash.com/photo-1495567720989-cebdbdd97913",
]

# 📸 async загрузка
async def get_photo_bytes():
    async with aiohttp.ClientSession() as session:

        for _ in range(2):
            try:
                url = "https://api.unsplash.com/photos/random"
                headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}

                params = {"query": random.choice(PHOTO_QUERIES)}

                async with session.get(url, headers=headers, params=params, timeout=5) as r:
                    if r.status == 200:
                        data = await r.json()
                        img_url = data.get("urls", {}).get("regular")

                        if not img_url:
                            continue

                        async with session.get(img_url, timeout=5) as img:
                            if img.status == 200:
                                return BytesIO(await img.read())
            except:
                continue

        # fallback
        try:
            fallback = random.choice(FALLBACK_IMAGES)
            async with session.get(fallback, timeout=5) as img:
                if img.status == 200:
                    return BytesIO(await img.read())
        except:
            return None

    return None

# 😈 текст
def generate_text(name, memory, level):
    last = memory[-1] if memory else "ничего"

    if level < 3:
        return f"{name}, всё будет нормально"

    if level < 6:
        return f"{name}, '{last}' звучит странно"

    if level < 9:
        return f"{name}, ты реально написал '{last}'?"

    return f"{name}, это выглядит жалко"

# 🎴 генерация
async def generate_card(message: types.Message):
    try:
        user_id = message.from_user.id
        name = message.from_user.first_name or "ты"

        memory = user_memory.get(user_id, [])
        level = user_level.get(user_id, 1)

        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(random.uniform(1, 2))

        text = generate_text(name, memory, level)

        img_bytes = await get_photo_bytes()

        if img_bytes:
            photo = BufferedInputFile(img_bytes.read(), filename="photo.jpg")
            await message.answer_photo(photo=photo, caption=f"💀 {text}")
        else:
            await message.answer(f"💀 {text} (без картинки...)")

    except Exception as e:
        print("ERROR:", e)
        await message.answer("💀 что-то пошло не так")

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)
    await message.answer("👁 я здесь", reply_markup=keyboard)

# 🎰 кнопка
@dp.message(lambda msg: msg.text == "💀 узнать правду")
async def spin(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    user_level[user_id] = user_level.get(user_id, 1) + 1

    await generate_card(message)

# 🧠 память
@dp.message()
async def memory_handler(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    user_memory.setdefault(user_id, []).append(message.text)

    if len(user_memory[user_id]) > 50:
        user_memory[user_id].pop(0)

    await message.answer("я это запомнил", reply_markup=keyboard)

# ▶️ запуск
async def main():
    print("бот жив")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())