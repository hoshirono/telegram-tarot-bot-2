import asyncio
import random
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

night_sent = {}
day_sent = {}

user_locks = {}

IMAGE_FOLDER = "images"

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# ====== ВРЕМЯ ======
import math

def format_time_left(seconds):
    seconds = max(0, math.ceil(seconds))  # округление ВВЕРХ

    h = seconds // 3600
    m = (seconds % 3600) // 60

    return f"{h}ч {m}м"
# ====== КАРТИНКА ======
def get_random_image():
    files = os.listdir(IMAGE_FOLDER)
    if not files:
        return None
    return os.path.join(IMAGE_FOLDER, random.choice(files))

# ====== ОТПРАВКА ФОТО (С ЛОКОМ) ======

import time
import math

COOLDOWN = 43200  # 12 часов

def format_time_left(seconds):
    seconds = max(0, math.ceil(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}ч {m}м"


async def send_photo(message):
    user = message.from_user.id
    now = time.time()

    # 🔥 ЖЕСТКИЙ анти-спам флаг (моментальный)
    if user in user_locks:
        if now - user_locks[user] < 2:
            return

    user_locks[user] = now

    last = last_photo_time.get(user, 0)
    diff = now - last

    # ❌ если не прошло 12 часов
    if diff < COOLDOWN:
        remain = COOLDOWN - diff

        await message.answer(random.choice([
                    f"я уже сказал. {format_time_left(remain)}",
                    f"ты долбишь кнопку зря. {format_time_left(remain)}",
                    f"терпения нет совсем? {format_time_left(remain)}",
                    f"не выйдет. {format_time_left(remain)}"
        ]), reply_markup=keyboard)
        return

    # 🔥 КРИТИЧЕСКИЙ ФИКС:
    # СРАЗУ блокируем следующую попытку
    last_photo_time[user] = now

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
            "сам виноват",
            "смотри"
        ]),
        reply_markup=keyboard
    )
# ====== СТАРТ ======
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "каркуша здесь",
        reply_markup=keyboard
    )

# ====== КНОПКА ======
@dp.message(lambda m: m.text == "накаркай, гад 🐦‍⬛️")
async def handle_button(message: types.Message):
    active_users.add(message.from_user.id)
    await send_photo(message)

# ====== ПРОСТОЙ ДИАЛОГ ======
def generate_reply(text):
    t = text.lower()

    if "как" in t:
        return random.choice([
            "живу",
            "наблюдаю",
            "тебя переживу"
        ])

    if any(w in t for w in ["нахуй", "иди", "дебил"]):
        return random.choice([
            "слабовато",
            "и это всё?",
            "ещё"
        ])

    return random.choice([
        "я вижу",
        "продолжай",
        "ничего нового",
        "ты предсказуем"
    ])

@dp.message()
async def handle(message: types.Message):
    if message.text == "накаркай, гад 🐦‍⬛️":
        return

    active_users.add(message.from_user.id)

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(0.5, 1.2))

    reply = generate_reply(message.text)
    await message.answer(reply, reply_markup=keyboard)

# ====== WATCHER ======
async def watcher():
    while True:
        await asyncio.sleep(60)

        now = datetime.now()
        hour = now.hour

        for user in list(active_users):
            try:
                # ===== НОЧЬ =====
                if 1 <= hour <= 5:
                    if not night_sent.get(user, False):
                        await bot.send_message(user, random.choice([
                            "не спишь?",
                            "я рядом",
                            "я вижу тебя"
                        ]))

                        await asyncio.sleep(60)

                        await bot.send_message(user, random.choice([
                            "ответь",
                            "не игнорируй",
                            "ты ведь здесь"
                        ]))

                        night_sent[user] = True
                else:
                    night_sent[user] = False

                # ===== ДЕНЬ (1 раз) =====
                if 10 <= hour <= 22:
                    if not day_sent.get(user, False):
                        if random.random() < 0.02:
                            await bot.send_message(user, random.choice([
                                "не расслабляйся",
                                "я помню",
                                "ты снова здесь"
                            ]))
                            day_sent[user] = True
                else:
                    day_sent[user] = False

                # ===== НАПОМИНАНИЕ =====
                last = last_photo_time.get(user)
                reminded = last_reminded.get(user)

                if last:
                    diff = (now - last).total_seconds()

                    if diff >= 43200:
                        if not reminded or (now - reminded).total_seconds() > 43200:
                            await bot.send_message(user, random.choice([
                                "время пришло",
                                "можешь снова",
                                "я ждал"
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