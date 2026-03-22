import asyncio
import random
import time
import os
import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

# ================== НАСТРОЙКИ ==================

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

IMAGE_FOLDER = "images"

# ================== ПАМЯТЬ ==================

memory = {}
active_users = set()
last_message_time = {}
last_ai_message = {}

# ================== КНОПКА ==================

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# ================== ФОТО ==================

def get_random_image():
    try:
        files = os.listdir(IMAGE_FOLDER)
        if not files:
            return None
        return os.path.join(IMAGE_FOLDER, random.choice(files))
    except:
        return None

# ================== ИИ ==================

async def ai_reply(user_id, text):
    if not OPENROUTER_API_KEY:
        return random.choice([
            "каркуша сегодня молчит",
            "сам подумай",
            "мне лень объяснять",
        ])

    history = memory.get(user_id, [])[-6:]

    messages = [
        {
            "role": "system",
            "content": (
                "Ты — Каркуша, тёмный маг.\n"
                "Саркастичный, циничный, раздражённый.\n"
                "Отвечай ОСМЫСЛЕННО.\n"
                "Веди диалог.\n"
                "Не повторяй пользователя.\n"
                "Не пиши бред.\n"
                "Иногда спорь.\n"
            )
        }
    ]

    for msg in history:
        messages.append({"role": "user", "content": msg})

    messages.append({"role": "user", "content": text})

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/mistral-7b-instruct:free",
                    "messages": messages,
                    "temperature": 0.7
                },
                timeout=20
            ) as r:

                data = await r.json()

                if "choices" not in data:
                    return "каркуша не в духе"

                content = data["choices"][0]["message"]["content"]

                if not content:
                    return "..."

                return content.strip()

    except Exception as e:
        print("AI ERROR:", e)
        return random.choice([
            "не сейчас",
            "я передумал отвечать",
            "сам догадайся",
        ])

# ================== АНТИ-ДУБЛЬ ==================

async def safe_send(message, text):
    if last_ai_message.get(message.chat.id) == text:
        return
    last_ai_message[message.chat.id] = text
    await message.answer(text)

# ================== ФОТО ==================

async def send_photo(message):
    await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

    path = get_random_image()
    if not path:
        await message.answer("картинки кончились")
        return

    caption = random.choice([
        "накаркал",
        "сам виноват",
        "держи",
        "живи теперь с этим",
        "каркуша видел хуже"
    ])

    await message.answer_photo(
        photo=FSInputFile(path),
        caption=caption
    )

# ================== ШЕПОТ ==================

async def delayed_whisper(chat_id):
    await asyncio.sleep(random.uniform(2, 4))

    try:
        await bot.send_message(chat_id, random.choice([
            "я наблюдаю",
            "ты опять сюда пришёл",
            "я всё вижу",
            "интересно...",
        ]))
    except:
        pass

# ================== СТАРТ ==================

@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "каркуша здесь.\n\nговори или жми кнопку.",
        reply_markup=keyboard
    )

# ================== КНОПКА ==================

@dp.message(lambda m: m.text == "накаркай, гад 🐦‍⬛️")
async def button_handler(message: types.Message):
    active_users.add(message.from_user.id)
    await send_photo(message)

# ================== ЧАТ ==================

@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id

    if message.text == "накаркай, гад 🐦‍⬛️":
        return

    active_users.add(user_id)

    # память
    memory.setdefault(user_id, []).append(message.text)
    if len(memory[user_id]) > 20:
        memory[user_id].pop(0)

    # печатает
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    # ответ ИИ
    reply = await ai_reply(user_id, message.text)

    await safe_send(message, reply)

    # редкий "шепот" после ответа
    if random.random() < 0.1:
        asyncio.create_task(delayed_whisper(message.chat.id))

# ================== НАБЛЮДАТЕЛЬ ==================

async def watcher():
    night_texts = [
        "я не сплю",
        "ты тоже не должен",
        "тишина говорит",
        "они рядом"
    ]

    day_texts = [
        "я всё ещё здесь",
        "мне скучно",
        "ты странный",
        "что ты делаешь"
    ]

    while True:
        await asyncio.sleep(60)

        for user_id in list(active_users):
            now = time.time()
            last = last_message_time.get(user_id, 0)

            if now - last < 18000:
                continue

            hour = time.localtime().tm_hour

            text = random.choice(night_texts if 1 <= hour <= 5 else day_texts)

            try:
                await bot.send_message(user_id, f"👁 {text}")
                last_message_time[user_id] = now
            except:
                pass

# ================== ЗАПУСК ==================

async def main():
    print("каркуша запущен")

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(watcher())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())