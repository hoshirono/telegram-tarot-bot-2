import asyncio
import random
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile

TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🧠 память
user_memory = {}
user_profile = {}
user_level = {}
user_last_trigger = {}

# 💀 кнопка
keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="💀 узнать правду о себе")]],
    resize_keyboard=True
)

# 🎴 названия
CARD_NAMES = [
    "Иллюзия контроля",
    "Сломанный выбор",
    "Петля ошибок",
    "Отрицание реальности",
    "Ложное спокойствие"
]

# 🧠 анализ
def analyze(text):
    text = text.lower()

    if any(w in text for w in ["не знаю", "хз"]):
        return "lost"
    if any(w in text for w in ["думаю", "наверное"]):
        return "doubt"
    if any(w in text for w in ["точно", "уверен"]):
        return "confidence"

    return "neutral"

# 🧠 профиль
def update_profile(user_id, text):
    tone = analyze(text)

    if user_id not in user_profile:
        user_profile[user_id] = {"doubt":0, "confidence":0, "lost":0, "neutral":0}

    user_profile[user_id][tone] += 1

# 😈 генерация текста
def generate_realistic_text(name, memory, profile, level, user_id):
    msg = random.choice(memory) if memory else "ничего"

    dominant = max(profile, key=profile.get)

    # 🎭 случайная "аномалия"
    anomaly = random.random()

    # 😇 начальный этап
    if level <= 2:
        return f"{name}, всё в порядке. Даже если ты написал '{msg}', ты справишься."

    # 😐 средний
    if level <= 5:
        return f"{name}, ты сказал '{msg}'. Ты замечаешь, как часто ты так пишешь?"

    # 😈 продвинутый
    if level <= 8:
        if dominant == "doubt":
            return f"{name}, ты часто сомневаешься. '{msg}' — просто ещё один пример."
        if dominant == "confidence":
            return f"{name}, ты звучишь уверенно. Но результат редко совпадает."
        return f"{name}, '{msg}' — это уже повторяющийся паттерн."

    # 💀 высокий уровень (реализм)
    if anomaly < 0.2:
        # странный ответ (ломает ожидания)
        return f"{name}, я уже видел это раньше. Почти слово в слово."

    if anomaly < 0.4 and user_id in user_last_trigger:
        old = user_last_trigger[user_id]
        return f"{name}, ты говорил '{old}'. Ничего не изменилось."

    if dominant == "doubt":
        result = f"{name}, ты не уверен почти ни в чём. '{msg}' только подтверждает это."
    elif dominant == "confidence":
        result = f"{name}, твоя уверенность не подкреплена. '{msg}' — показательно."
    else:
        result = f"{name}, ты просто наблюдаешь за своей жизнью, не влияя на неё."

    # 💀 усиление
    if level > 10:
        result += " Ты повторяешь себя чаще, чем думаешь."

    return result

# 🎨 генерация картинки
def generate_image(prompt):
    try:
        url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }

        r = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)

        if r.status_code != 200:
            return None

        return r.content
    except:
        return None

# 🎴 карта
async def generate_card(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "ты"

    memory = user_memory.get(user_id, [])
    profile = user_profile.get(user_id, {"neutral":1})
    level = user_level.get(user_id, 1)

    text = generate_realistic_text(name, memory, profile, level, user_id)

    # сохраняем триггер
    if memory:
        user_last_trigger[user_id] = random.choice(memory)

    card = random.choice(CARD_NAMES)

    prompt = f"""
dark tarot card,
{card},
human trapped in repeating patterns,
psychological symbolism,
cinematic, detailed, dramatic lighting
"""

    img = generate_image(prompt)

    caption = f"🃏 {card}\n\n💀 {text}"

    if img:
        photo = BufferedInputFile(img, filename="card.png")
        await message.answer_photo(photo=photo, caption=caption)
    else:
        await message.answer(caption)

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("🙂 я просто слушаю", reply_markup=keyboard)

# 🎰 кнопка
@dp.message(lambda msg: msg.text == "💀 узнать правду о себе")
async def spin(message: types.Message):
    user_id = message.from_user.id
    user_level[user_id] = user_level.get(user_id, 1) + 1

    await generate_card(message)

# 🧠 память
@dp.message()
async def fallback(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append(message.text)

    if len(user_memory[user_id]) > 30:
        user_memory[user_id].pop(0)

    update_profile(user_id, message.text)

    await message.answer("я запомнил это", reply_markup=keyboard)

# ▶️ запуск
async def main():
    print("Пугающе реалистичный ИИ запущен 💀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())