import asyncio
import random
import os
import time
from io import BytesIO

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ChatAction

TOKEN = os.getenv("TELEGRAM_TOKEN")
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 👁 память
user_memory = {}
user_level = {}
user_last_seen = {}
active_users = set()

# 💀 кнопка
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="💀 узнать правду")]],
    resize_keyboard=True
)

PHOTO_QUERIES = [
    "creepy dark person",
    "abandoned horror building",
    "lonely night street",
    "shadow figure",
]

FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1509248961158-e54f6934749c",
    "https://images.unsplash.com/photo-1495567720989-cebdbdd97913",
]

# 📸 async загрузка картинки
async def get_photo_bytes():
    async with aiohttp.ClientSession() as session:

        # пробуем API
        for _ in range(2):
            try:
                url = "https://api.unsplash.com/photos/random"

                headers = {
                    "Authorization": f"Client-ID {UNSPLASH_KEY}"
                }

                params = {
                    "query": random.choice(PHOTO_QUERIES),
                    "orientation": "square"
                }

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

# 👁 слежка
def observer(user_id):
    now = time.time()

    if user_id not in user_last_seen:
        user_last_seen[user_id] = now
        return None

    diff = now - user_last_seen[user_id]
    user_last_seen[user_id] = now

    if diff < 10:
        return "ты слишком быстро вернулся"
    if diff > 300:
        return "я ждал тебя"

    return None

# 😈 текст
def generate_text(name, memory, level):
    last = memory[-1] if memory else "ничего"

    if level <= 2:
        return f"{name}, всё будет нормально"

    if level <= 5:
        return f"{name}, '{last}' звучит сомнительно"

    if level <= 8:
        return f"{name}, ты реально написал '{last}'?"

    return random.choice([
        f"{name}, это выглядит жалко",
        f"{name}, ты сам веришь в это?",
        f"{name}, становится только хуже",
        f"{name}, ты даже не понимаешь",
    ])

# 🎴 генерация
async def generate_card(message: types.Message):
    try:
        user_id = message.from_user.id
        name = message.from_user.first_name or "ты"

        memory = user_memory.get(user_id, [])
        level = user_level.get(user_id, 1)

        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(random.uniform(1.0, 2.0))

        text = generate_text(name, memory, level)
        obs = observer(user_id)

        if obs:
            text = f"{obs}. {text}"

        img_bytes = await get_photo_bytes()

        if img_bytes:
            img_bytes.name = "photo.jpg"
            await message.answer_photo(photo=img_bytes, caption=f"💀 {text}")
        else:
            await message.answer(f"💀 {text}")

    except Exception as e:
        print("ERROR:", e)
        await message.answer("💀 что-то пошло не так...")

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

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

# 👁 инициатива (без краша)
async def watcher():
    while True:
        try:
            await asyncio.sleep(random.randint(60, 120))

            if not active_users:
                continue

            user_id = random.choice(list(active_users))

            text = random.choice([
                "ты опять здесь?",
                "я думаю о тебе",
                "ты не закончил",
                "я помню"
            ])

            await bot.send_message(user_id, f"👁 {text}")

        except Exception as e:
            print("WATCHER ERROR:", e)

# ▶️ запуск
async def main():
    print("👁 бот жив")
    asyncio.create_task(watcher())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())