import asyncio
import random
import time
import os
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

IMAGES_FOLDER = "images"

memory = {}
patterns = {}
user_style = {}
relation = {}  # отношение к пользователю
active_users = set()
last_photo_time = {}
last_day_message = {}
last_night_message = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# ================== ОБУЧЕНИЕ ==================

def learn(user_id, text):
    words = re.findall(r'\w+', text.lower())

    memory.setdefault(user_id, []).append(text)
    if len(memory[user_id]) > 30:
        memory[user_id].pop(0)

    user_style.setdefault(user_id, []).extend(words)
    if len(user_style[user_id]) > 200:
        user_style[user_id] = user_style[user_id][-200:]

    for w in words:
        patterns.setdefault(w, []).append(text)
        if len(patterns[w]) > 20:
            patterns[w].pop(0)

    # отношение
    rel = relation.get(user_id, 0)

    if any(w in text.lower() for w in ["спасибо", "норм", "понял"]):
        rel += 1
    if any(w in text.lower() for w in ["иди", "заткнись", "бред"]):
        rel -= 2

    relation[user_id] = max(-10, min(10, rel))

# ================== ЛОГИКА ==================

def analyze(text):
    text = text.lower()

    if "почему" in text:
        return "why"
    if "как" in text:
        return "how"
    if "что" in text:
        return "what"
    if "ты" in text:
        return "attack"
    if "не" in text:
        return "neg"
    return "neutral"

def distort(text):
    words = text.split()

    if random.random() < 0.3 and words:
        i = random.randint(0, len(words)-1)
        words[i] += words[i][-1]

    if random.random() < 0.2:
        words = words[::-1]

    return " ".join(words)

def generate_reply(user_id, text):
    mode = analyze(text)
    rel = relation.get(user_id, 0)

    # базовый смысл
    base_map = {
        "why": "потому что ты сам это запустил",
        "how": "ты уже сделал всё необходимое",
        "what": "ты правда хочешь это знать?",
        "attack": "ты слишком уверен в себе",
        "neg": "отрицание ничего не меняет",
        "neutral": "я наблюдаю"
    }

    base = base_map.get(mode, "я вижу больше чем ты думаешь")

    # настройка отношения
    if rel < -5:
        base += ". ты начинаешь раздражать"
    elif rel > 5:
        base += ". ты стал интереснее"

    # вставка памяти
    if user_id in memory and random.random() < 0.5:
        base += f". {distort(random.choice(memory[user_id]))}"

    # стиль пользователя
    words = user_style.get(user_id, [])
    if words and random.random() < 0.4:
        base += f". {random.choice(words)}..."

    # паттерны
    for w in text.split():
        if w in patterns and random.random() < 0.3:
            base += f". {random.choice(patterns[w])}"
            break

    # газлайтинг
    if random.random() < 0.3:
        base += ". ты сам уже знаешь ответ"

    return distort(base)

# ================== ФОТО ==================

def get_random_image():
    files = [f for f in os.listdir(IMAGES_FOLDER) if f.endswith((".jpg", ".png", ".jpeg"))]
    if not files:
        return None
    return os.path.join(IMAGES_FOLDER, random.choice(files))

async def send_photo(message):
    user_id = message.from_user.id
    now = time.time()

    last = last_photo_time.get(user_id, 0)

    if now - last < 86400:
        await message.answer(random.choice([
            "не так быстро",
            "ждать не умеешь?",
            "я тебе не автомат",
            "сутки не прошли",
            "ты уже получил своё"
        ]))
        return

    path = get_random_image()

    if not path:
        await message.answer("пусто. даже у меня.")
        return

    last_photo_time[user_id] = now

    await message.answer_photo(
        FSInputFile(path),
        caption=random.choice([
            "накаркал",
            "смотри",
            "оно теперь с тобой",
            "ты это выбрал"
        ])
    )

# ================== ЧАТ ==================

@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id

    if message.text == "накаркай, гад 🐦‍⬛️":
        return

    active_users.add(user_id)

    learn(user_id, message.text)

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    reply = generate_reply(user_id, message.text)

    await message.answer(reply)

# ================== СТАРТ ==================

@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "каркуша наблюдает\n\nжми кнопку если хочешь",
        reply_markup=keyboard
    )

# ================== КНОПКА ==================

@dp.message(lambda m: m.text == "накаркай, гад 🐦‍⬛️")
async def button(message: types.Message):
    await send_photo(message)

# ================== НАБЛЮДЕНИЕ ==================

async def watcher():
    while True:
        await asyncio.sleep(300)

        hour = time.localtime().tm_hour

        for user in active_users:
            try:
                if 1 <= hour <= 5:
                    # ночью — 2 сообщения
                    if random.random() < 0.3:
                        await bot.send_message(user, random.choice([
                            "ты не один",
                            "я рядом",
                            "не оборачивайся"
                        ]))
                        await asyncio.sleep(2)
                        await bot.send_message(user, random.choice([
                            "я всё ещё здесь",
                            "ты это чувствуешь",
                            "тишина странная"
                        ]))
                else:
                    # днем — редко 1 сообщение
                    last = last_day_message.get(user, 0)
                    if time.time() - last > 21600:  # 6 часов
                        if random.random() < 0.3:
                            await bot.send_message(user, random.choice([
                                "я думаю о тебе",
                                "что-то изменилось",
                                "я заметил"
                            ]))
                            last_day_message[user] = time.time()

            except:
                pass

# ================== ЗАПУСК ==================

async def main():
    print("каркуша жив")

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(watcher())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())