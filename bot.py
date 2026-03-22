import asyncio
import os
import random
import signal
import sys
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

IMAGE_FOLDER = "images"

memory = {}
last_photo_time = {}
active_users = set()
last_activity = {}

night_sent = {}
day_sent = {}

shutdown_event = asyncio.Event()

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# 💀 МЯГКОЕ ЗАВЕРШЕНИЕ
def shutdown_handler():
    print("💀 Получен сигнал остановки")
    shutdown_event.set()

signal.signal(signal.SIGTERM, lambda *_: shutdown_handler())
signal.signal(signal.SIGINT, lambda *_: shutdown_handler())

# 🧠 простой интеллект
def generate_reply(user_id, text):
    text = text.lower()

    if "как ты" in text:
        return random.choice([
            "наблюдаю",
            "живу дольше тебя",
            "я не меняюсь"
        ])

    if "почему" in text:
        return random.choice([
            "потому что ты так решил",
            "слишком поздно спрашивать",
            "ты уже сделал выбор"
        ])

    if any(x in text for x in ["идиот", "нахуй", "дебил"]):
        return random.choice([
            "слабовато",
            "это всё?",
            "ожидал лучше"
        ])

    if user_id in memory and random.random() < 0.3:
        return random.choice(memory[user_id])

    return random.choice([
        "продолжай",
        "я слушаю",
        "интересно",
        "ты повторяешься"
    ])

# 🖼 фото
def get_image():
    files = os.listdir(IMAGE_FOLDER)
    if not files:
        return None
    return os.path.join(IMAGE_FOLDER, random.choice(files))

async def send_photo(message: types.Message):
    user_id = message.from_user.id
    now = time.time()

    if user_id in last_photo_time:
        diff = now - last_photo_time[user_id]
        if diff < 86400:
            left = int((86400 - diff) / 3600)
            await message.answer(f"ждать {left}ч")
            return

    path = get_image()
    if not path:
        await message.answer("нет картинок")
        return

    await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    await asyncio.sleep(1)

    await message.answer_photo(
        FSInputFile(path),
        caption=random.choice(["накаркал", "смотри"])
    )

    last_photo_time[user_id] = now

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)
    await message.answer("каркуша здесь", reply_markup=keyboard)

# 🎰 кнопка
@dp.message(lambda m: m.text == "накаркай, гад 🐦‍⬛️")
async def btn(message: types.Message):
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
    await asyncio.sleep(1)

    reply = generate_reply(user_id, message.text)
    await message.answer(reply)

# 👁 поведение
async def watcher():
    while not shutdown_event.is_set():
        await asyncio.sleep(60)

        now = time.time()
        hour = datetime.now().hour

        for user_id in list(active_users):
            last = last_activity.get(user_id, 0)

            if 1 <= hour <= 5 and not night_sent.get(user_id):
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

            if 10 <= hour <= 22 and not day_sent.get(user_id):
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

    await asyncio.sleep(3)

    watcher_task = asyncio.create_task(watcher())

    polling_task = asyncio.create_task(dp.start_polling(bot))

    # 💀 ЖДЁМ СИГНАЛА ОСТАНОВКИ
    await shutdown_event.wait()

    print("💀 останавливаемся...")

    polling_task.cancel()
    watcher_task.cancel()

    await bot.session.close()

    print("бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())