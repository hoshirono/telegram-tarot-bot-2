import asyncio
import random
import os
import requests
import time

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# 🔑 токены
TOKEN = os.getenv("TELEGRAM_TOKEN")
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY")

if not TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN не найден")

if not UNSPLASH_KEY:
    raise Exception("❌ UNSPLASH_KEY не найден")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 👁 память
user_memory = {}
user_profile = {}
user_level = {}
user_last_seen = {}
active_users = set()

# 💀 кнопка
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="💀 узнать правду")]],
    resize_keyboard=True
)

# 📸 поисковые запросы (максимально криповые)
PHOTO_QUERIES = [
    "creepy person in dark",
    "abandoned hospital horror",
    "man staring in darkness",
    "disturbing empty room",
    "shadow figure night",
    "lonely street night fog",
    "weird unsettling portrait",
    "creepy corridor horror"
]

# 📸 получение фото
def get_photo():
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
            return r.json()["urls"]["regular"]
    except:
        return None

    return None

# 🧠 анализ
def analyze(text):
    text = text.lower()
    if "не знаю" in text or "хз" in text:
        return "weak"
    if "уверен" in text or "точно" in text:
        return "ego"
    return "neutral"

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

# 😈 генерация текста
def generate_text(name, memory, profile, level):
    last = memory[-1] if memory else "ничего"

    if level <= 2:
        return f"{name}, всё будет нормально. наверное."

    if level <= 5:
        return f"{name}, ты написал '{last}'. звучит неуверенно."

    if level <= 8:
        return f"{name}, '{last}' — и ты думаешь это хорошая идея?"

    # ЖЁСТКИЙ режим
    return random.choice([
        f"{name}, ты реально думаешь, что '{last}' — это норм?",
        f"{name}, это выглядит жалко. особенно '{last}'",
        f"{name}, ты сам веришь в эту чушь: '{last}'?",
        f"{name}, чем больше ты пишешь, тем хуже выглядит ситуация",
        f"{name}, ты даже не понимаешь насколько это плохо"
    ])

# 🎴 генерация
async def generate_card(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "ты"

    memory = user_memory.get(user_id, [])
    profile = user_profile.get(user_id, {})
    level = user_level.get(user_id, 1)

    base = generate_text(name, memory, profile, level)
    obs = observer(user_id)

    text = f"{obs}. {base}" if obs else base

    photo = get_photo()

    if photo:
        await message.answer_photo(photo=photo, caption=f"💀 {text}")
    else:
        await message.answer(f"💀 {text}")

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

# 👁 инициатива бота
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
            "ты правда думаешь, что всё нормально?",
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