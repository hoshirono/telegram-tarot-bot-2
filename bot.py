import asyncio
import random
import time
import os
from pathlib import Path

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

# ========================
# 🔑 ENV
# ========================
TOKEN = os.getenv("8705289370:AAF14RnDpQIi7SxChdQIpGshbD2iB_G9La0")
AI_KEY = os.getenv("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")

if not TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ========================
# 📁 ПАПКА С ФОТКАМИ
# ========================
IMAGE_FOLDER = Path("images")

# ========================
# 💀 ДАННЫЕ
# ========================
memory = {}
active_users = set()
last_message_time = {}
user_style = {}

# ========================
# 🔘 КНОПКА
# ========================
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# ========================
# 🧠 AI
# ========================
async def ask_ai(prompt):
    if not AI_KEY:
        return None

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {AI_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {"role": "system", "content": "Ты Каркуша — темный маг, циничный, саркастичный, немного злой"},
                    {"role": "user", "content": prompt}
                ]
            }

            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=20
            ) as r:
                data = await r.json()
                return data["choices"][0]["message"]["content"]
    except:
        return None

# ========================
# 🧠 СТИЛЬ ПОЛЬЗОВАТЕЛЯ
# ========================
def adapt_style(text):
    if len(text) < 5:
        return text

    if random.random() < 0.3:
        text = text.lower()

    if random.random() < 0.3:
        text = text.replace(" ", "...")

    if random.random() < 0.2:
        text = text + "."

    return text

# ========================
# 💬 ЛОКАЛЬНЫЙ ОТВЕТ
# ========================
def generate_local_reply(user_id, text):
    base = random.choice([
        "ты серьёзно?",
        "и это всё?",
        "слабовато",
        "я ожидал хуже",
        "хотя бы честно",
        "мда"
    ])

    if user_id in memory and memory[user_id]:
        old = random.choice(memory[user_id])
        base += f"\n\nты же писал: '{old}'"

    return adapt_style(base)

# ========================
# 🖼 ФОТО
# ========================
def get_random_image():
    files = list(IMAGE_FOLDER.glob("*"))
    return random.choice(files) if files else None

# ========================
# 🎴 ОТПРАВКА ФОТО
# ========================
async def send_photo(message: types.Message):
    await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

    file_path = get_random_image()
    if not file_path:
        await message.answer("картинки закончились. как и ты.")
        return

    captions = [
        "накаркал",
        "сам просил",
        "ну держи",
        "это ты заслужил",
        "смотри и не плачь",
        "красиво получилось, да?"
    ]

    photo = FSInputFile(file_path)
    await message.answer_photo(
        photo=photo,
        caption=random.choice(captions)
    )

# ========================
# 🚀 СТАРТ
# ========================
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "каркуша уже здесь",
        reply_markup=keyboard
    )

# ========================
# 🎰 КНОПКА (ТОЛЬКО ФОТО)
# ========================
@dp.message(lambda m: m.text == "накаркай, гад 🐦‍⬛️")
async def photo_button(message: types.Message):
    active_users.add(message.from_user.id)
    await send_photo(message)

# ========================
# 💬 СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
# ========================
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text or ""

    active_users.add(user_id)

    # сохраняем память
    memory.setdefault(user_id, []).append(text)
    if len(memory[user_id]) > 50:
        memory[user_id].pop(0)

    # иногда пишем ДО ответа (эффект "читает мысли")
    if random.random() < 0.2:
        await message.answer("не пиши... я уже знаю")

    # ИИ или локалка
    reply = None
    if random.random() < 0.4:
        reply = await ask_ai(text)

    if not reply:
        reply = generate_local_reply(user_id, text)

    await message.answer(reply, reply_markup=keyboard)

# ========================
# 👁 САМОСТОЯТЕЛЬНЫЕ СООБЩЕНИЯ
# ========================
async def watcher():
    while True:
        await asyncio.sleep(60)

        for user_id in list(active_users):
            now = time.time()
            last = last_message_time.get(user_id, 0)

            if now - last < random.randint(1800, 7200):
                continue

            hour = time.localtime().tm_hour

            if 1 <= hour <= 5:
                text = random.choice([
                    "ты не спишь...",
                    "я вижу тебя",
                    "зря ты открыл чат",
                    "оно рядом"
                ])
            else:
                text = random.choice([
                    "ты снова здесь",
                    "без меня не вывозишь?",
                    "я ждал",
                    "опять ты"
                ])

            try:
                await bot.send_message(user_id, f"👁 {text}")
                last_message_time[user_id] = now
            except:
                pass

# ========================
# ▶️ ЗАПУСК
# ========================
async def main():
    print("бот запущен")

    # 💀 УБИРАЕМ КОНФЛИКТ
    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(watcher())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())