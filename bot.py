import asyncio
import random
import time
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

# ====== ТОКЕН ======
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("⚠️ TELEGRAM_TOKEN не найден")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ====== ДАННЫЕ ======
active_users = set()
memory = {}

last_photo_time = {}
last_reminded = {}

night_sent = {}
day_sent = {}

IMAGE_FOLDER = "images"

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# ====== КАРТИНКА ======
def get_random_image():
    files = os.listdir(IMAGE_FOLDER)
    if not files:
        return None
    return os.path.join(IMAGE_FOLDER, random.choice(files))

# ====== ДИАЛОГ ======
def generate_reply(user_id, text):
    t = text.lower()

    insults = ["нахуй", "иди", "тупой", "дебил"]
    if any(w in t for w in insults):
        return random.choice([
            "слабовато",
            "ещё",
            "ты злишься скучно",
            "и это всё?"
        ])

    if "как" in t and "ты" in t:
        return random.choice([
            "я существую",
            "лучше чем ты",
            "нормально. наблюдаю"
        ])

    if t in ["да", "нет"]:
        return random.choice([
            "ожидаемо",
            "и всё?",
        ])

    base = random.choice([
        "ты снова здесь",
        "ничего не меняется",
        "я вижу",
        "продолжай"
    ])

    if user_id in memory and memory[user_id]:
        if random.random() < 0.3:
            base += f". {random.choice(memory[user_id])}"

    return base

# ====== ОТПРАВКА ФОТО ======
async def send_photo(message):
    user = message.from_user.id
    now = time.time()

    last = last_photo_time.get(user, 0)

    if now - last < 86400:
        remain = int((86400 - (now - last)) // 3600)
        await message.answer(random.choice([
            f"я сказал — позже. {remain}ч",
            f"ещё рано. подожди {remain}ч",
            f"ты не понял с первого раза? {remain}ч"
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
            "сам виноват",
            "получай",
            "смотри"
        ]),
        reply_markup=keyboard
    )

    last_photo_time[user] = now

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

# ====== ДИАЛОГ ======
@dp.message()
async def handle(message: types.Message):
    user = message.from_user.id
    active_users.add(user)

    if message.text == "накаркай, гад 🐦‍⬛️":
        return

    memory.setdefault(user, []).append(message.text)
    if len(memory[user]) > 20:
        memory[user].pop(0)

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(0.5, 1.5))

    reply = generate_reply(user, message.text)

    await message.answer(reply, reply_markup=keyboard)

# ====== WATCHER ======
async def watcher():
    while True:
        await asyncio.sleep(60)

        now = time.time()
        hour = time.localtime().tm_hour

        for user in list(active_users):
            try:
                # ===== НОЧЬ (1 раз, 2 сообщения) =====
                if 1 <= hour <= 5:
                    if not night_sent.get(user, False):
                        await bot.send_message(user, random.choice([
                            "не спишь?",
                            "я здесь",
                            "я вижу тебя"
                        ]))

                        await asyncio.sleep(2)

                        await bot.send_message(user, random.choice([
                            "не игнорируй",
                            "ответь",
                            "ты ведь зашел не просто так"
                        ]))

                        night_sent[user] = True

                # сброс после ночи
                else:
                    night_sent[user] = False

                # ===== ДЕНЬ (1 раз) =====
                if 10 <= hour <= 22:
                    if not day_sent.get(user, False):
                        if random.random() < 0.05:
                            await bot.send_message(user, random.choice([
                                "ты снова здесь",
                                "я помню",
                                "не расслабляйся"
                            ]))
                            day_sent[user] = True

                else:
                    day_sent[user] = False

                # ===== НАПОМИНАНИЕ 24ч =====
                last_photo = last_photo_time.get(user, 0)
                last_note = last_reminded.get(user, 0)

                if last_photo != 0:
                    if now - last_photo >= 86400 and now - last_note >= 86400:
                        await bot.send_message(user, random.choice([
                            "время пришло",
                            "можешь снова попробовать",
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