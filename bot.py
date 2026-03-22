import os
import asyncio
import random
from aiohttp import web

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

# ======================
# 🔑 ENV
# ======================

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # https://your-app.up.railway.app
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

if not TOKEN or not WEBHOOK_HOST:
    raise ValueError("Нет TELEGRAM_TOKEN или WEBHOOK_HOST")

# ======================
# 🤖 BOT
# ======================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ======================
# 📁 КАРТИНКИ
# ======================

IMAGE_FOLDER = "images"

def get_random_image():
    files = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith((".jpg", ".png"))]
    if not files:
        return None
    return os.path.join(IMAGE_FOLDER, random.choice(files))

# ======================
# ⌨️ КНОПКА
# ======================

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# ======================
# 🧠 ПРОСТОЙ “ИИ”
# ======================

memory = {}

def smart_reply(user_id, text):
    text_low = text.lower()

    # оскорбления
    if any(w in text_low for w in ["идиот", "дебил", "нахуй", "пошел"]):
        return random.choice([
            "ты даже ругаться нормально не умеешь",
            "слабо. попробуй еще раз",
            "это максимум твоего интеллекта?",
            "мне даже обидно не стало"
        ])

    # как дела
    if "как ты" in text_low or "как дела" in text_low:
        return random.choice([
            "я наблюдаю",
            "лучше, чем ты думаешь",
            "всё идет по плану. не твоему",
            "ты бы не понял"
        ])

    # память
    if user_id in memory and random.random() < 0.3:
        old = random.choice(memory[user_id])
        return f"{old}... ты ведь так и не понял, да?"

    # обычный ответ
    return random.choice([
        "продолжай",
        "это не имеет значения",
        "ты упускаешь главное",
        "я уже это видел",
        "дальше"
    ])

# ======================
# 🚀 HANDLERS
# ======================

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # кнопка
    if text == "накаркай, гад 🐦‍⬛️":
        await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

        path = get_random_image()
        if not path:
            await message.answer("картинки закончились. как и ты")
            return

        await message.answer_photo(
            FSInputFile(path),
            caption=random.choice([
                "накаркал",
                "сам виноват",
                "не ной",
                "так и должно было быть"
            ])
        )
        return

    # память
    memory.setdefault(user_id, []).append(text)
    if len(memory[user_id]) > 20:
        memory[user_id].pop(0)

    # печатает
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(0.5, 1.5))

    # ответ
    reply = smart_reply(user_id, text)
    await message.answer(reply)

# ======================
# 🌐 WEBHOOK SERVER
# ======================

async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()

async def on_startup(app):
    print("бот запускается...")
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()