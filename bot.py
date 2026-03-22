import asyncio
import random
import time
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

# ================== НАСТРОЙКИ ==================

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

IMAGES_FOLDER = "images"

# ================== ИНИЦИАЛИЗАЦИЯ ==================

bot = Bot(token=TOKEN)
dp = Dispatcher()

memory = {}
active_users = set()
last_message_time = {}

# ================== КНОПКА ==================

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# ================== СЛОВАРИ ==================

dark_phrases = [
    "я вижу тебя даже когда ты не пишешь",
    "сегодня ты опять выберешь не то",
    "тишина вокруг тебя странная",
    "ты ведь чувствуешь это, да?",
    "не все мысли твои",
]

night_phrases = [
    "ночью ты думаешь слишком громко",
    "я слышу твои мысли",
    "ты зря не спишь",
    "в темноте ты честнее",
    "я рядом",
]

taunts = [
    "без меня не вывозишь, да?",
    "опять пишешь мне",
    "не начинай даже",
    "я уже знаю что ты скажешь",
    "давай быстрее"
]

photo_captions = [
    "накаркал",
    "сам гад",
    "можно было и повежливее",
    "ну держи",
    "смотри внимательнее"
]

# ================== ВСПОМОГАТЕЛЬНЫЕ ==================

def distort(text):
    words = text.split()

    if not words:
        return text

    if random.random() < 0.4:
        w = random.choice(words)
        words[words.index(w)] = w + w[-1]

    if random.random() < 0.3:
        words = words[::-1]

    return " ".join(words)

def generate_reply(user_id, user_text):
    base = random.choice([
        "ты сам это начал",
        "не притворяйся",
        "это звучит хуже чем ты думаешь",
        "я бы на твоем месте молчал",
        "ты опять об этом",
    ])

    # иногда вставляет старые сообщения
    if user_id in memory and memory[user_id] and random.random() < 0.4:
        old = random.choice(memory[user_id])
        base += f". {distort(old)}"

    # искажает текущий текст
    if random.random() < 0.5:
        base += f". {distort(user_text)}"

    return base

def get_random_image():
    files = [f for f in os.listdir(IMAGES_FOLDER) if f.endswith((".jpg", ".png", ".jpeg"))]

    if not files:
        return None

    return os.path.join(IMAGES_FOLDER, random.choice(files))

async def safe_send(chat_id, text):
    try:
        await bot.send_message(chat_id, text)
    except:
        pass

# ================== ФОТО ==================

async def send_photo(message: types.Message):
    path = get_random_image()

    if not path:
        await message.answer("нет картинок")
        return

    photo = FSInputFile(path)

    await message.answer_photo(
        photo=photo,
        caption=random.choice(photo_captions)
    )

# ================== СТАРТ ==================

@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "каркуша здесь\n\nжми кнопку",
        reply_markup=keyboard
    )

# ================== КНОПКА ==================

@dp.message(lambda m: m.text == "накаркай, гад 🐦‍⬛️")
async def photo_handler(message: types.Message):
    active_users.add(message.from_user.id)
    await send_photo(message)

# ================== ПСЕВДО "ТЫ ПЕЧАТАЕШЬ" ==================

async def fake_typing(user_id):
    await asyncio.sleep(random.uniform(2, 5))

    if random.random() < 0.3:
        await safe_send(user_id, random.choice(taunts))

# ================== ЧАТ ==================

@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id

    if message.text == "накаркай, гад 🐦‍⬛️":
        return

    active_users.add(user_id)

    # сохраняем
    memory.setdefault(user_id, []).append(message.text)
    if len(memory[user_id]) > 20:
        memory[user_id].pop(0)

    # имитация "видит что печатаешь"
    asyncio.create_task(fake_typing(user_id))

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    reply = generate_reply(user_id, message.text)

    await message.answer(reply)

# ================== НОЧНАЯ КРИПОТА ==================

async def night_watcher():
    while True:
        await asyncio.sleep(300)

        hour = time.localtime().tm_hour

        if 1 <= hour <= 5:
            for user in active_users:
                if random.random() < 0.3:
                    await safe_send(user, random.choice(night_phrases))

# ================== ОБЫЧНЫЕ СООБЩЕНИЯ ==================

async def watcher():
    while True:
        await asyncio.sleep(120)

        for user in active_users:
            now = time.time()
            last = last_message_time.get(user, 0)

            if now - last < 10800:
                continue

            if random.random() < 0.4:
                await safe_send(user, random.choice(dark_phrases))
                last_message_time[user] = now

# ================== ЗАПУСК ==================

async def main():
    print("каркуша запущен")

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(watcher())
    asyncio.create_task(night_watcher())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())