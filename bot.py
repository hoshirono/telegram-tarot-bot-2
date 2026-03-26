import asyncio
import random
import time
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

# ====== ТОКЕН ======
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ====== ДАННЫЕ ======
active_users = set()

last_photo_time = {}
last_reminded = {}

day_sent = {}
night_sent = {}

IMAGE_FOLDER = "images"

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# ====== КАРТИНКИ ======
def get_random_image():
    try:
        files = os.listdir(IMAGE_FOLDER)
        files = [f for f in files if not f.startswith(".")]
        if not files:
            return None
        return os.path.join(IMAGE_FOLDER, random.choice(files))
    except:
        return None


# ====== ФОРМАТ ВРЕМЕНИ ======
def format_time_left(seconds):
    minutes = int(seconds // 60)
    hours = minutes // 60
    minutes = minutes % 60

    return f"{hours}ч {minutes}м"


# ====== ОТПРАВКА ФОТО ======
async def send_photo(message):
    user = message.from_user.id
    now = datetime.now()

    last = last_photo_time.get(user)

    if last:
        diff = (now - last).total_seconds()

        if diff < 43200:  # 12 часов
            remain = 43200 - diff

            await message.answer(random.choice([
                f"я сказал — позже. {format_time_left(remain)}",
                f"ещё рано. осталось {format_time_left(remain)}",
                f"ты проверяешь границы? {format_time_left(remain)}",
                f"не дождался. {format_time_left(remain)}"
            ]), reply_markup=keyboard)
            return

    path = get_random_image()

    if not path:
        await message.answer("картинок нет", reply_markup=keyboard)
        return

    await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    await asyncio.sleep(1)

    photo = FSInputFile(path)

    await message.answer_photo(
        photo,
        caption=random.choice([
            "накаркал",
            "держи",
            "сам напросился",
            "смотри теперь"
        ]),
        reply_markup=keyboard
    )

    last_photo_time[user] = now


# ====== СТАРТ ======
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer("каркуша здесь", reply_markup=keyboard)


# ====== КНОПКА ======
@dp.message(lambda m: m.text == "накаркай, гад 🐦‍⬛️")
async def handle_button(message: types.Message):
    active_users.add(message.from_user.id)
    await send_photo(message)


# ====== WATCHER ======
async def watcher():
    while True:
        await asyncio.sleep(60)

        now = datetime.now()
        hour = now.hour

        for user in list(active_users):
            try:
                # ===== НОЧЬ (1 раз, 2 сообщения с интервалом 60 сек) =====
                if 1 <= hour <= 5:
                    if not night_sent.get(user, False):

                        await bot.send_message(user, random.choice([
                            "не спишь?",
                            "я рядом",
                            "ты опять здесь"
                        ]))

                        await asyncio.sleep(60)

                        await bot.send_message(user, random.choice([
                            "не игнорируй",
                            "я жду",
                            "ответь"
                        ]))

                        night_sent[user] = True

                else:
                    night_sent[user] = False

                # ===== ДЕНЬ (1 раз) =====
                if 10 <= hour <= 22:
                    if not day_sent.get(user, False):

                        await bot.send_message(user, random.choice([
                            "не расслабляйся",
                            "я наблюдаю",
                            "ты снова здесь"
                        ]))

                        day_sent[user] = True

                else:
                    day_sent[user] = False

                # ===== НАПОМИНАНИЕ 12 ЧАСОВ =====
                last = last_photo_time.get(user)
                last_note = last_reminded.get(user)

                if last:
                    diff = (now - last).total_seconds()

                    if diff >= 43200:
                        if not last_note or (now - last_note).total_seconds() > 43200:

                            await bot.send_message(user, random.choice([
                                "время пришло",
                                "можешь снова попытаться",
                                "я ждал этого"
                            ]))

                            last_reminded[user] = now

            except:
                pass


# ====== ЗАПУСК ======
async def main():
    print("бот запущен")

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(watcher())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())