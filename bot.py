import asyncio
import random
import time
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction
import aiohttp

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
            "мне лень думать",
            "сам догадайся",
            "я сегодня молчу",
        ])

    history = memory.get(user_id, [])[-6:]

    messages = [
        {
            "role": "system",
            "content": (
                "Ты — Каркуша, тёмный маг.\n"
                "Саркастичный, циничный, раздражительный.\n"
                "Веди осмысленный диалог.\n"
                "Не повторяй пользователя.\n"
                "Не говори 'ты писал'.\n"
                "Иногда спорь.\n"
                "Иногда отвечай коротко.\n"
                "Не неси бред.\n"
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
                    "model": "mistralai/mistral-7b-instruct",
                    "messages": messages,
                    "temperature": 0.7
                }
            ) as r:
                data = await r.json()

                if "choices" not in data:
                    return "каркуша не в духе"

                return data["choices"][0]["message"]["content"]

    except:
        return "я тебя не слышу"

# ================== АНТИ ДУБЛЬ ==================

async def safe_send(message, text):
    if last_ai_message.get(message.chat.id) == text:
        return
    last_ai_message[message.chat.id] = text
    await message.answer(text)

# ================== ОТПРАВКА ФОТО ==================

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
        "не ной теперь",
        "живи с этим",
        "могло быть хуже"
    ])

    await message.answer_photo(
        photo=FSInputFile(path),
        caption=caption
    )

# ================== СТАРТ ==================

@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "каркуша смотрит на тебя.\n\nжми кнопку или говори.",
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

    # "он видит что ты пишешь"
    if random.random() < 0.25:
        await message.answer(random.choice([
            "опять печатаешь...",
            "я уже знаю, что ты скажешь",
            "давай быстрее",
            "не тупи",
        ]))

    # печатает
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    reply = await ai_reply(user_id, message.text)
    await safe_send(message, reply)

# ================== НАБЛЮДАТЕЛЬ ==================

async def watcher():
    night_texts = [
        "я не сплю",
        "ты тоже не должен",
        "тишина слишком громкая",
        "я вижу тебя",
        "они рядом"
    ]

    day_texts = [
        "я всё ещё здесь",
        "ты странный",
        "мне скучно",
        "что ты опять сделал"
    ]

    while True:
        await asyncio.sleep(60)

        for user_id in list(active_users):
            now = time.time()
            last = last_message_time.get(user_id, 0)

            if now - last < 18000:
                continue

            hour = time.localtime().tm_hour

            if 1 <= hour <= 5:
                text = random.choice(night_texts)
            else:
                text = random.choice(day_texts)

            try:
                await bot.send_message(user_id, f"👁 {text}")
                last_message_time[user_id] = now
            except:
                pass

# ================== ЗАПУСК ==================

async def main():
    print("каркуша проснулся")

    # 💀 фикс конфликта
    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(watcher())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())