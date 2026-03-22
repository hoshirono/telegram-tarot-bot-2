import asyncio
import random
import time
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.enums import ChatAction

TOKEN = "ТВОЙ_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher()

IMAGE_FOLDER = "/app/images"

# память
memory = {}
learned_phrases = {}
last_seen = {}
last_auto = {}
last_typing_fake = {}

active_users = set()

BUTTON_TEXT = "накаркай, гад 🐦‍⬛️"

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BUTTON_TEXT)]],
    resize_keyboard=True
)

# =======================
# 🧠 ПАМЯТЬ
# =======================

def remember_user(user_id, text):
    memory.setdefault(user_id, []).append(text)

    if len(memory[user_id]) > 100:
        memory[user_id].pop(0)

    if len(text) > 6:
        learned_phrases.setdefault(user_id, []).append(text)

        if len(learned_phrases[user_id]) > 50:
            learned_phrases[user_id].pop(0)

# =======================
# 😈 ЛИЧНОСТЬ КАРКУШИ
# =======================

def karkusha_prefix():
    return random.choice([
        "каркуша смотрит на тебя:",
        "каркуша усмехнулся:",
        "каркуша шепчет:",
        "каркуша уже всё понял:"
    ])

# =======================
# 💀 ИСКАЖЕНИЕ
# =======================

def distort(text):
    words = text.split()
    if len(words) > 3:
        words[random.randint(0, len(words)-1)] = "…"
    return " ".join(words)

# =======================
# 😈 АНАЛИЗ ТЕМЫ
# =======================

def generate_smart_reply(user_id, text):
    text_lower = text.lower()

    # темы
    if "жизн" in text_lower:
        base = "ты опять пытаешься понять жизнь, но она уже устала от тебя"
    elif "люб" in text_lower:
        base = "любовь? ты сначала с собой разберись"
    elif "работ" in text_lower:
        base = "работа тебя не спасёт, не надейся"
    elif "устал" in text_lower:
        base = "ты устал? ты даже не начинал нормально"
    else:
        base = random.choice([
            "ты сейчас серьёзно?",
            "это была попытка мысли?",
            "интересно, ты сам в это веришь?",
            "каркуша разочарован"
        ])

    # припоминание
    if user_id in learned_phrases and random.random() < 0.5:
        phrase = random.choice(learned_phrases[user_id])
        phrase = distort(phrase)

        base += f"\n\nты же говорил:\n{phrase}"

    return f"{karkusha_prefix()}\n{base}"

# =======================
# 🖼 КАРТИНКИ
# =======================

def get_random_image():
    if not os.path.exists(IMAGE_FOLDER):
        return None

    files = [f for f in os.listdir(IMAGE_FOLDER)
             if f.endswith((".jpg", ".png", ".jpeg"))]

    if not files:
        return None

    path = os.path.join(IMAGE_FOLDER, random.choice(files))

    with open(path, "rb") as f:
        return BufferedInputFile(f.read(), filename="img.jpg")

async def send_image(message: types.Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    photo = get_random_image()

    caption = random.choice([
        "накаркал",
        "сам гад",
        "можно было и повежливее попросить",
        "держи, страдай",
        "каркуша доволен твоим выбором"
    ])

    if photo:
        await message.answer_photo(photo=photo, caption=caption)
    else:
        await message.answer("каркуша потерял свои образы")

# =======================
# 🚀 СТАРТ
# =======================

@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    await message.answer(
        "я каркуша.\nне жми кнопку без причины.",
        reply_markup=keyboard
    )

# =======================
# 🎰 КНОПКА (ТОЛЬКО ФОТО)
# =======================

@dp.message(lambda m: m.text == BUTTON_TEXT)
async def spin(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    await send_image(message)

# =======================
# 🧠 СООБЩЕНИЯ
# =======================

@dp.message()
async def handle(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    if message.text == BUTTON_TEXT:
        return

    remember_user(user_id, message.text)

    last_seen[user_id] = time.time()

    # иногда отвечает
    if random.random() < 0.7:
        reply = generate_smart_reply(user_id, message.text)
        await message.answer(reply, reply_markup=keyboard)

# =======================
# 👁 СЛЕЖКА / "ТЫ ПЕЧАТАЕШЬ"
# =======================

async def watcher():
    while True:
        await asyncio.sleep(10)

        now = time.time()
        hour = datetime.now().hour

        for user_id in list(active_users):
            last = last_seen.get(user_id, 0)
            last_auto_msg = last_auto.get(user_id, 0)
            last_fake = last_typing_fake.get(user_id, 0)

            # 🔥 "он печатает"
            if now - last < 20 and now - last_fake > 300:
                if random.random() < 0.5:
                    try:
                        text = random.choice([
                            "без меня не вывозишь, да?",
                            "пиши, я всё равно уже знаю",
                            "опять хочешь что-то сказать?",
                            "я уже вижу, что ты печатаешь",
                            "не утруждайся, каркуша быстрее"
                        ])
                        await bot.send_message(user_id, f"👁 {text}")
                        last_typing_fake[user_id] = now
                    except:
                        pass

            # 🌙 ночь
            if 2 <= hour <= 5 and now - last_auto_msg > 21600:
                try:
                    creepy = random.choice([
                        "я здесь",
                        "ты не один",
                        "каркуша рядом",
                        "не закрывай глаза",
                        "оно смотрит"
                    ])
                    await bot.send_message(user_id, f"👁 {creepy}")
                    last_auto[user_id] = now
                except:
                    pass

# =======================
# ▶️ ЗАПУСК
# =======================

async def main():
    print("каркуша запущен")

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