import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.filters import CommandStart

# ====== НАСТРОЙКИ ======
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # https://your-app.up.railway.app
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

if not TOKEN or not WEBHOOK_HOST:
    raise ValueError("Нет TELEGRAM_TOKEN или WEBHOOK_HOST")

# ====== ИНИЦИАЛИЗАЦИЯ ======
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ====== ХЕНДЛЕРЫ ======
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("каркуша здесь. не радуйся")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"я услышал: {message.text}")

# ====== WEBHOOK HANDLER ======
async def handle(request):
    try:
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.error(f"Ошибка обработки апдейта: {e}")
    return web.Response()

# ====== ЗАПУСК ======
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

def main():
    app = web.Application()

    app.router.add_post(WEBHOOK_PATH, handle)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()