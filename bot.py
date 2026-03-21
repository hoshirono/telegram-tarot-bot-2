import asyncio
import random
import time
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramNetworkError

TOKEN = "8705289370:AAF14RnDpQIi7SxChdQIpGshbD2iB_G9La0"

bot = Bot(token=TOKEN)
dp = Dispatcher()

IMAGE_FOLDER = "images"

active_users = set()
last_message_time = {}
night_sent = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад🐦‍⬛️")]],
    resize_keyboard=True
)

# 🖼 картинки
def get_random_image():
    if not os.path.exists(IMAGE_FOLDER):
        return None

    files = [
        f for f in os.listdir(IMAGE_FOLDER)
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ]

    if not files:
        return None

    path = os.path.join(IMAGE_FOLDER, random.choice(files))

    with open(path, "rb") as f:
        return BufferedInputFile(f.read(), filename="img.jpg")

# 😈 тексты
def night_text():
    return random.choice([
        "не оборачивайся",
        "ты сейчас не один",
        "я уже был здесь",
        "оно смотрит вместе со мной",
        "проверь дверь",
        "ты почти проснулся"
    ])

def random_creepy():
    return random.choice([
        "я наблюдаю",
        "ты странно себя ведёшь",
        "ты опять это сделал",
        "мне не нравится это",
        "интересно, когда ты поймешь"
    ])

# 📸 отправка
async def send_image(message: types.Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    photo = get_random_image()

    if photo:
        await message.answer_photo(photo=photo)
    else:
        await message.answer("картинок нет. как и смысла")

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "жми кнопку",
        reply_markup=keyboard
    )

# 🎰 кнопка
@dp.message(lambda m: m.text == "💀 дай мне визуальный кринж пожалуйста")
async def spin(message: types.Message):
    active_users.add(message.from_user.id)
    await send_image(message)

# 👁 watcher
async def watcher():
    while True:
        await asyncio.sleep(60)

        now = datetime.now()
        hour = now.hour

        for user_id in list(active_users):
            current_time = time.time()
            last = last_message_time.get(user_id, 0)

            # 🌙 ночь
            if 2 <= hour <= 5:
                key = f"{user_id}_{now.date()}"

                if not night_sent.get(key):
                    try:
                        await bot.send_message(user_id, f"👁 {night_text()}")
                        night_sent[key] = True
                    except:
                        pass
                continue

            # 🤡 редко пишет
            if current_time - last < 43200:
                continue

            try:
                await bot.send_message(user_id, f"👁 {random_creepy()}")
                last_message_time[user_id] = current_time
            except:
                pass

# 🔥 СУПЕР-ФИКС ЗАПУСКА
async def main():
    print("бот запущен")

    # 💀 УБИВАЕМ ВСЕ КОНФЛИКТЫ
    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(watcher())

    # 🔁 вечный перезапуск polling при конфликте
    while True:
        try:
            await dp.start_polling(bot)
        except TelegramNetworkError as e:
            print("перезапуск polling...", e)
            await asyncio.sleep(3)
        except Exception as e:
            print("ошибка:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())