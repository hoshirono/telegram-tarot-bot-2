import asyncio
import random
import time
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.enums import ChatAction

# 🔑 ВСТАВЬ ТОКЕН
TOKEN = "8705289370:AAF14RnDpQIi7SxChdQIpGshbD2iB_G9La0"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📁 ПАПКА С КАРТИНКАМИ
IMAGE_FOLDER = "/app/images"  # локально: "images"

# 🧠 память
memory = {}
learned_phrases = {}
last_seen = {}
last_auto = {}

active_users = set()

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="💀 ну давай че там покажи дичь")]],
    resize_keyboard=True
)

# =======================
# 🧠 ПАМЯТЬ
# =======================

def remember_user(user_id, text):
    memory.setdefault(user_id, []).append(text)

    if len(memory[user_id]) > 100:
        memory[user_id].pop(0)

    if len(text) > 8:
        learned_phrases.setdefault(user_id, []).append(text)

        if len(learned_phrases[user_id]) > 50:
            learned_phrases[user_id].pop(0)


# =======================
# 😈 СТИЛЬ ПОЛЬЗОВАТЕЛЯ
# =======================

def mimic_style(user_id, text):
    if user_id not in memory:
        return text

    samples = memory[user_id]

    # если пишет без заглавных — бот тоже
    if all(s.lower() == s for s in samples[-5:]):
        text = text.lower()

    # если мат — добавляем мат
    if any("хуй" in s or "бля" in s for s in samples):
        text += random.choice([
            " да, именно так",
            " ну ты понял",
            " классика блять",
            " ахуенно конечно"
        ])

    return text


# =======================
# 💀 ИСКАЖЕНИЕ ФРАЗ
# =======================

def distort_phrase(text):
    words = text.split()

    if len(words) > 3:
        words[random.randint(0, len(words)-1)] = "…"

    if random.random() < 0.3:
        words.append("или нет")

    return " ".join(words)


# =======================
# 😈 ГЕНЕРАЦИЯ СООБЩЕНИЯ
# =======================

def generate_mock(user_id):
    if user_id in learned_phrases and learned_phrases[user_id]:
        phrase = random.choice(learned_phrases[user_id])
        distorted = distort_phrase(phrase)

        base = random.choice([
            "ты же писал:",
            "я помню это:",
            "ты сказал:",
            "это было:"
        ])

        endings = random.choice([
            "и ты норм?",
            "и после этого ты живешь дальше?",
            "это многое объясняет",
            "мне стало хуже после этого"
        ])

        text = f"{base}\n\n{distorted}\n\n{endings}"
        return mimic_style(user_id, text)

    return "ты пока недостаточно наговорил"


# =======================
# 🖼 КАРТИНКИ
# =======================

def get_random_image():
    if not os.path.exists(IMAGE_FOLDER):
        print("нет папки:", IMAGE_FOLDER)
        return None

    files = [
        f for f in os.listdir(IMAGE_FOLDER)
        if f.endswith((".jpg", ".png", ".jpeg"))
    ]

    if not files:
        print("нет файлов")
        return None

    path = os.path.join(IMAGE_FOLDER, random.choice(files))

    with open(path, "rb") as f:
        return BufferedInputFile(f.read(), filename="img.jpg")


async def send_image(message: types.Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    photo = get_random_image()

    if photo:
        await message.answer_photo(photo=photo)
    else:
        await message.answer("картинки где-то сдохли")


# =======================
# 🚀 СТАРТ
# =======================

@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    await message.answer(
        "жми кнопку и не жалуйся потом",
        reply_markup=keyboard
    )


# =======================
# 🎰 КНОПКА
# =======================

@dp.message(lambda m: m.text == "накаркай, гад 🐦‍⬛️")
async def spin(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    await send_image(message)


# =======================
# 🧠 СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
# =======================

@dp.message()
async def handle(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    remember_user(user_id, message.text)

    now = time.time()
    last_seen[user_id] = now

    # шанс мгновенного ответа
    if random.random() < 0.5:
        await message.answer(generate_mock(user_id), reply_markup=keyboard)


# =======================
# 👁 СЛЕЖКА
# =======================

async def watcher():
    while True:
        await asyncio.sleep(30)

        now = time.time()
        hour = datetime.now().hour

        for user_id in list(active_users):
            last = last_seen.get(user_id, 0)
            last_auto_msg = last_auto.get(user_id, 0)

            # 📡 реакция после активности (очень важно)
            if now - last < 60 and now - last_auto_msg > 300:
                try:
                    text = generate_mock(user_id)
                    await bot.send_message(user_id, f"👁 {text}")
                    last_auto[user_id] = now
                except:
                    pass
                continue

            # 🌙 ночная крипота
            if 2 <= hour <= 5 and now - last_auto_msg > 21600:
                try:
                    creepy = random.choice([
                        "ты не один",
                        "я вижу тебя",
                        "оно тоже здесь",
                        "не смотри назад",
                        "ты проснулся?"
                    ])
                    await bot.send_message(user_id, f"👁 {creepy}")
                    last_auto[user_id] = now
                except:
                    pass


# =======================
# ▶️ ЗАПУСК
# =======================

async def main():
    print("бот запущен")

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(watcher())

    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            print("перезапуск:", e)
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())