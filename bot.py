import asyncio
import os
import sys

from aiogram import Bot, Dispatcher

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

LOCK_FILE = "bot.lock"


# 💀 защита от второго запуска
def acquire_lock():
    if os.path.exists(LOCK_FILE):
        print("❌ Бот уже запущен (найден lock-файл)")
        sys.exit()

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


# 💀 освобождение при остановке
def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


# 🚀 основной запуск
async def main():
    print("бот запускается...")

    # 💥 УБИРАЕМ WEBHOOK (очень важно)
    await bot.delete_webhook(drop_pending_updates=True)

    print("бот запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        acquire_lock()   # 👈 блокируем второй запуск
        asyncio.run(main())
    finally:
        release_lock()   # 👈 освобождаем при остановке