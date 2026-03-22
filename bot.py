import asyncio
import os
import random
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📁 папка с картинками
IMAGE_FOLDER = "images"

# 🧠 память
memory = {}
last_photo_time = {}
active_users = set()
last_activity = {}

# 👁 контроль сообщений
night_sent = {}
day_sent = {}

# 🎮 кнопка
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# 🧠 простой “ИИ”
def generate_reply(user_id, text):
    text_lower = text.lower()

    insults = ["идиот", "тупой", "дебил", "нахуй", "пошел"]
    if any(word in text_lower for word in insults):
        return random.choice([
            "слабовато. я ожидал большего.",
            "оскорбления — это максимум, да?",
            "ты даже злиться нормально не умеешь",
            "жалко смотришься"
        ])

    if "как ты" in text_lower or "как дела" in text_lower:
        return random.choice([
            "я не меняюсь. в отличие от тебя.",
            "наблюдаю. этого достаточно.",
            "всё стабильно плохо. у тебя.",
            "я в порядке. ты — под вопросом."
        ])

    if "почему" in text_lower:
        return random.choice([
            "потому что ты так решил.",
            "ты правда ждёшь ответа?",
            "поздно задавать вопросы.",
            "ты уже сделал выбор."
        ])

    # 🧠 память вставка
    if user_id in memory and random.random() < 0.3:
        past = random.choice(memory[user_id])
        return f"{past}. ты так и не понял, да?"

    return random.choice([
        "ты повторяешься",
        "я уже это видел",
        "ничего нового",
        "продолжай. мне даже интересно",
        "ты всё ещё здесь"
    ])

# 🖼 фото
def get_random_image():
    files = os.listdir(IMAGE_FOLDER)
    if not files:
        return None
    return os.path.join(IMAGE_FOLDER, random.choice(files))

# 🎴 отправка фото
async def send_photo(message: types.Message):
    user_id = message.from_user.id
    now = time.time()

    if user_id in last_photo_time:
        diff = now - last_photo_time[user_id]
        if diff < 86400:
            remaining = int((86400 - diff) / 3600)
            await message.answer(
                random.choice([
                    f"я сказал — позже. осталось {remaining}ч",
                    f"не жадничай. ещё {remaining}ч",
                    f"терпи. {remaining}ч осталось"
                ])
            )
            return

    path = get_random_image()
    if not path:
        await message.answer("картинок нет")
        return

    await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    await asyncio.sleep(1)

    await message.answer_photo(
        photo=FSInputFile(path),
        caption=random.choice([
            "накаркал",
            "сам напросился",
            "смотри",
            "доволен?"
        ])
    )

    last_photo_time[user_id] = now

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "каркуша здесь.\nжми кнопку или пиши.",
        reply_markup=keyboard
    )

# 🎰 кнопка
@dp.message(lambda m: m.text == "накаркай, гад 🐦‍⬛️")
async def handle_button(message: types.Message):
    active_users.add(message.from_user.id)
    await send_photo(message)

# 💬 диалог
@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id

    active_users.add(user_id)
    last_activity[user_id] = time.time()

    memory.setdefault(user_id, []).append(message.text)
    if len(memory[user_id]) > 50:
        memory[user_id].pop(0)

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(0.5, 1.5))

    reply = generate_reply(user_id, message.text)

    await message.answer(reply)

# 👁 поведение
async def watcher():
    while True:
        await asyncio.sleep(60)
        now = time.time()
        hour = datetime.now().hour

        for user_id in list(active_users):
            last = last_activity.get(user_id, 0)

            # 🌙 ночь — 2 сообщения
            if 1 <= hour <= 5:
                if night_sent.get(user_id):
                    continue

                if now - last < 600:
                    try:
                        await bot.send_message(user_id, "я не сплю")
                        await asyncio.sleep(2)
                        await bot.send_message(user_id, "и ты тоже")
                        night_sent[user_id] = True
                    except:
                        pass

            else:
                night_sent[user_id] = False

            # ☀️ день — 1 сообщение
            if 10 <= hour <= 22:
                if day_sent.get(user_id):
                    continue

                if now - last < 300:
                    try:
                        await bot.send_message(user_id, "я вижу тебя")
                        day_sent[user_id] = True
                    except:
                        pass
            else:
                day_sent[user_id] = False

# ▶️ запуск
async def main():
    print("бот запускается...")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

    await asyncio.sleep(2)

    asyncio.create_task(watcher())

    print("бот запущен")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())