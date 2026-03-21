import asyncio
import random
import os
import requests
import time
from io import BytesIO

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

# 🔑 токены
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

# 📸 запросы
PHOTO_QUERIES = [
    "creepy person dark",
    "abandoned hospital horror",
    "disturbing empty room",
    "shadow figure night",
    "lonely street fog",
]

# 📸 получить фото (теперь байты)
def get_photo_bytes():
    url = "https://api.unsplash.com/photos/random"

    headers = {
        "Authorization": f"Client-ID {UNSPLASH_KEY}"
    }

    params = {
        "query": random.choice(PHOTO_QUERIES),
        "orientation": "square"
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            img_url = r.json()["urls"]["regular"]

            img = requests.get(img_url, timeout=10)
            return BytesIO(img.content)
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
    user_id = message.from_user.id
    name = message.from_user.first_name or "ты"

    memory = user_memory.get(user_id, [])
    level = user_level.get(user_id, 1)

    # ⏳ эффект "печатает"
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1.5, 3.5))

    text = generate_text(name, memory, level)
    obs = observer(user_id)

    if obs:
        text = f"{obs}. {text}"

    img_bytes = get_photo_bytes()

    if img_bytes:
        img_bytes.name = "photo.jpg"
        await message.answer_photo(photo=img_bytes, caption=f"💀 {text}")
    else:
        await message.answer(f"💀 {text} (сегодня без картинки)")

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

    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append(message.text)

    if len(user_memory[user_id]) > 50:
        user_memory[user_id].pop(0)

    await message.answer("я это запомнил", reply_markup=keyboard)

# 👁 инициатива
async def watcher():
    while True:
        await asyncio.sleep(random.randint(60, 180))

        if not active_users:
            continue

        user_id = random.choice(list(active_users))

        text = random.choice([
            "ты опять здесь?",
            "я думаю о тебе",
            "ты не закончил",
            "это всё ещё с тобой",
            "я помню, что ты писал"
        ])

        try:
            await bot.send_message(user_id, f"👁 {text}")
        except:
            pass

# ▶️ запуск
async def main():
    print("👁 бот наблюдает")
    asyncio.create_task(watcher())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())