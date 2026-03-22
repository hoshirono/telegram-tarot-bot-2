import asyncio
import random
import time
import os
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

IMAGES_FOLDER = "images"

memory = {}
user_style = {}
relation = {}
active_users = set()
last_photo_time = {}
last_seen = {}
obsession_level = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# ================== ОБУЧЕНИЕ ==================

def learn(user_id, text):
    words = re.findall(r'\w+', text.lower())

    memory.setdefault(user_id, []).append(text)
    if len(memory[user_id]) > 30:
        memory[user_id].pop(0)

    user_style.setdefault(user_id, []).extend(words)
    if len(user_style[user_id]) > 200:
        user_style[user_id] = user_style[user_id][-200:]

    rel = relation.get(user_id, 0)

    if any(w in text.lower() for w in ["спасибо", "норм"]):
        rel += 1
    if any(w in text.lower() for w in ["иди", "заткнись", "бред"]):
        rel -= 2

    relation[user_id] = max(-10, min(10, rel))

    # рост одержимости
    obsession_level[user_id] = obsession_level.get(user_id, 0) + 1

# ================== ГЕНЕРАЦИЯ ==================

def distort(text):
    words = text.split()

    if words and random.random() < 0.3:
        i = random.randint(0, len(words)-1)
        words[i] += words[i][-1]

    if random.random() < 0.2:
        words = words[::-1]

    return " ".join(words)

def generate_reply(user_id, text):
    base = random.choice([
        "я вижу это",
        "ты снова здесь",
        "ничего не меняется",
        "я ждал",
        "ты не удивляешь"
    ])

    if user_id in memory and random.random() < 0.5:
        base += f". {random.choice(memory[user_id])}"

    if random.random() < 0.4:
        base += f". {text}"

    if random.random() < 0.3:
        base += ". ты сам это понимаешь"

    return distort(base)

# ================== ФОТО ==================

def get_image():
    files = [f for f in os.listdir(IMAGES_FOLDER) if f.endswith((".jpg",".png",".jpeg"))]
    if not files:
        return None
    return os.path.join(IMAGES_FOLDER, random.choice(files))

async def send_photo(message):
    user_id = message.from_user.id
    now = time.time()

    last = last_photo_time.get(user_id, 0)

    if now - last < 86400:
        await message.answer("ещё рано. подожди.")
        return

    path = get_image()

    if not path:
        await message.answer("нет файлов")
        return

    last_photo_time[user_id] = now

    await message.answer_photo(
        FSInputFile(path),
        caption=random.choice(["накаркал","смотри"])
    )

# ================== ОСНОВНОЙ ОБРАБОТЧИК ==================

@dp.message()
async def handle(message: types.Message):
    try:
        user_id = message.from_user.id
        text = message.text

        active_users.add(user_id)
        last_seen[user_id] = time.time()

        # КНОПКА
        if text == "накаркай, гад 🐦‍⬛️":
            await send_photo(message)
            return

        # ОБУЧЕНИЕ
        learn(user_id, text)

        # ПЕЧАТАЕТ
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(random.uniform(1,2))

        reply = generate_reply(user_id, text)

        await message.answer(reply)

    except Exception as e:
        print("ERROR:", e)

# ================== ОДЕРЖИМОСТЬ ==================

async def watcher():
    while True:
        await asyncio.sleep(180)

        for user in active_users:
            try:
                last = last_seen.get(user, 0)
                obs = obsession_level.get(user, 0)

                # если пользователь активен → усиливаем давление
                if time.time() - last < 120:
                    if random.random() < min(0.5, obs / 50):
                        await bot.send_message(user, random.choice([
                            "ты опять здесь",
                            "я чувствую тебя",
                            "не уходи",
                            "мы не закончили"
                        ]))

                # если пропал → зовём обратно
                elif time.time() - last > 600:
                    if random.random() < 0.3:
                        await bot.send_message(user, random.choice([
                            "куда ты делся",
                            "я жду",
                            "ты не закончил",
                        ]))

                # НОЧЬ
                hour = time.localtime().tm_hour
                if 1 <= hour <= 5:
                    if random.random() < 0.3:
                        await bot.send_message(user, random.choice([
                            "не спишь?",
                            "я рядом",
                            "ты слышишь это?"
                        ]))
                        await asyncio.sleep(2)
                        await bot.send_message(user, random.choice([
                            "не игнорируй",
                            "я всё ещё здесь"
                        ]))

            except:
                pass

# ================== СТАРТ ==================

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "каркуша уже наблюдает",
        reply_markup=keyboard
    )

# ================== ЗАПУСК ==================

async def main():
    print("каркуша одержим")

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(watcher())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())