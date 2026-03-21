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
user_level = {}

# 💀 кнопка
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💀 получить моральный урон")]
    ],
    resize_keyboard=True
)

# 🎴 название
def generate_name():
    return random.choice([
        "Сломанный выбор судьбы",
        "Проклятый цикл решений",
        "Ошибка самооценки",
        "Иллюзия контроля",
        "Падение без причины"
    ])

# 🧠 АНАЛИЗ текста
def analyze_text(text):
    text = text.lower()

    if any(word in text for word in ["я думаю", "наверное", "возможно"]):
        return "сомнение"
    if any(word in text for word in ["я точно", "я уверен"]):
        return "самоуверенность"
    if any(word in text for word in ["не знаю", "хз"]):
        return "потерянность"
    return "обычное"

# 😈 генерация злого ответа
def generate_evil_text(name, msg, level, tone):
    base = [
        f"{name}, ты написал: '{msg}'.",
        f"{name}, я запомнил: '{msg}'.",
    ]

    doubt = [
        "Ты даже не уверен в себе, и это видно.",
        "Ты уже сомневаешься, хотя ещё ничего не сделал.",
    ]

    confidence = [
        "Самоуверенность без результата — это твой стиль.",
        "Ты звучишь уверенно. Это единственное, что у тебя есть.",
    ]

    lost = [
        "Ты даже не понимаешь, что происходит.",
        "Ты потерян, и это уже не временно.",
    ]

    neutral = [
        "И это многое объясняет.",
        "Теперь всё встало на свои места.",
    ]

    extra = [
        "Ты создаёшь проблемы быстрее, чем решаешь.",
        "Даже случайность делает это лучше тебя.",
        "Ты стабилен. Стабильно не туда.",
    ]

    result = random.choice(base)

    if tone == "сомнение":
        result += " " + random.choice(doubt)
    elif tone == "самоуверенность":
        result += " " + random.choice(confidence)
    elif tone == "потерянность":
        result += " " + random.choice(lost)
    else:
        result += " " + random.choice(neutral)

    # 💀 усиление по уровню
    if level > 2:
        result += " " + random.choice(extra)

    if level > 5:
        result += " Ты повторяешь одни и те же ошибки."

    return result

# 🎨 генерация картинки
def generate_image(prompt):
    try:
        url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)

        if response.status_code != 200:
            return None

        return response.content

    except:
        return None

# 🎴 карта
async def generate_card(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "ты"

    memory = user_memory.get(user_id, ["ничего"])
    msg = random.choice(memory)

    tone = analyze_text(msg)

    level = user_level.get(user_id, 1)

    text = generate_evil_text(name, msg, level, tone)

    card_name = generate_name()

    prompt = f"""
dark tarot card,
{card_name},
symbol of failure, wrong decisions,
person trapped in consequences,
cinematic, detailed, dramatic lighting
"""

    img = generate_image(prompt)

    caption = f"🃏 {card_name}\n\n💀 {text}"

    if img:
        photo = BufferedInputFile(img, filename="card.png")
        await message.answer_photo(photo=photo, caption=caption)
    else:
        await message.answer(caption)

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("💀 ты уверен, что хочешь продолжать?", reply_markup=keyboard)

# 🎰 кнопка
@dp.message(lambda msg: msg.text == "💀 получить моральный урон")
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

    if len(user_memory[user_id]) > 5:
        user_memory[user_id].pop(0)

    await message.answer("я запомнил", reply_markup=keyboard)

# ▶️ запуск
async def main():
    print("Злой ИИ активирован 💀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())