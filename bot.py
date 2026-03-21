import asyncio
import random
import os
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

# память
memory = {}
level = {}
active_users = set()

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔮 узнать свою жалкую судьбу")]],
    resize_keyboard=True
)

# 🎴 карты
CARD_NAMES = [
    "Король просранных шансов",
    "Шут без перспектив",
    "Император неловкости",
    "Повешенный на своих решениях",
    "Дурак, но с опытом",
]

PREDICTIONS = [
    "ты снова сделаешь не тот выбор, но будешь оправдываться",
    "ты всё понимаешь, но всё равно делаешь хуже",
    "ничего не изменится, потому что это ты",
    "ты упустишь шанс и сделаешь вид, что так и надо",
    "ты снова свернёшь не туда, как обычно",
]

RARITY = ["обычная", "редкая", "позорная", "легендарно бесполезная"]

PHOTO_QUERIES = [
    "dark lonely person",
    "creepy shadow",
    "abandoned place horror",
]

# 📸 генерация картинки
async def get_image():
    async with aiohttp.ClientSession() as session:
        try:
            url = "https://api.unsplash.com/photos/random"
            headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
            params = {"query": random.choice(PHOTO_QUERIES)}

            async with session.get(url, headers=headers, params=params, timeout=5) as r:
                data = await r.json()
                img_url = data["urls"]["regular"]

            async with session.get(img_url, timeout=5) as img:
                return BytesIO(await img.read())

        except:
            return None

# 😈 генерация предсказания
def generate_prediction(user_id, name):
    user_memory = memory.get(user_id, [])
    lvl = level.get(user_id, 1)

    card = random.choice(CARD_NAMES)
    pred = random.choice(PREDICTIONS)
    rarity = random.choice(RARITY)

    # добавляем персональное унижение
    if user_memory:
        last = user_memory[-1]
        pred += f"\n\nи да, '{last}' — это было особенно тупо"

    # усиление токсичности
    if lvl > 5:
        pred += "\nты реально не учишься"
    if lvl > 8:
        pred += "\nэто даже не смешно уже"

    return card, rarity, pred

# 🎴 выдача карты
async def send_card(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "ты"

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    card, rarity, pred = generate_prediction(user_id, name)

    text = f"🃏 {card}\n💎 Редкость: {rarity}\n\n🔮 {pred}"

    img = await get_image()

    if img:
        photo = BufferedInputFile(img.read(), filename="card.jpg")
        await message.answer_photo(photo=photo, caption=text)
    else:
        await message.answer(text)

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    await message.answer(
        "я буду предсказывать твою судьбу\nи тебе это не понравится",
        reply_markup=keyboard
    )

# 🎰 кнопка
@dp.message(lambda m: m.text == "🔮 узнать свою жалкую судьбу")
async def spin(message: types.Message):
    user_id = message.from_user.id

    level[user_id] = level.get(user_id, 1) + 1
    active_users.add(user_id)

    await send_card(message)

# 🧠 память
@dp.message()
async def remember(message: types.Message):
    user_id = message.from_user.id

    memory.setdefault(user_id, []).append(message.text)

    if len(memory[user_id]) > 30:
        memory[user_id].pop(0)

    await message.answer("запомнил. зря ты это написал.", reply_markup=keyboard)

# 👁 инициатива
async def watcher():
    while True:
        await asyncio.sleep(random.randint(60, 120))

        if not active_users:
            continue

        user_id = random.choice(list(active_users))

        text = random.choice([
            "я всё ещё думаю о твоём последнем решении",
            "ты ведь понимаешь, что всё пошло не туда?",
            "интересно, ты уже пожалел?",
        ])

        try:
            await bot.send_message(user_id, f"👁 {text}")
        except:
            pass

# ▶️ запуск
async def main():
    print("бот запущен")
    asyncio.create_task(watcher())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())