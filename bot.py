import asyncio
import random
import os
import json
import requests
import time

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# 🔑 переменные
TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_FILE = "data.json"

# ================= БАЗА =================

def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, user_id):
    if user_id not in data:
        data[user_id] = {
            "cards": []
        }
    return data[user_id]

# ================= UI =================

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔮 Получить карту")],
            [KeyboardButton(text="📦 Моя коллекция")]
        ],
        resize_keyboard=True
    )

# ================= ГЕНЕРАЦИЯ =================

def gen_name():
    a = ["Император","Жрица","Рыцарь","Дьявол","Маг","Скелет","Кот","Пельмень"]
    b = ["Хаоса","Кринжа","Судьбы","Wi-Fi","Налогов","Абсурда","Боли"]
    return f"{random.choice(a)} {random.choice(b)}"

def gen_text():
    return random.choice([
        "Ты выбрал худший путь, и это нормально.",
        "Судьба уже смеётся над тобой.",
        "Сегодня ты снова всё испортишь.",
        "Карты говорят: лучше не лезь.",
        "Это знак… плохой знак."
    ])

# 🎨 генерация картинки через HuggingFace
def generate_image(prompt):
    if not HF_TOKEN:
        print("Нет HF_TOKEN")
        return None

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=60
        )

        # если модель "спит"
        if response.status_code == 503:
            print("Модель спит, ждём...")
            time.sleep(10)
            response = requests.post(
                API_URL,
                headers=headers,
                json={"inputs": prompt},
                timeout=60
            )

        if response.status_code != 200:
            print("Ошибка HF:", response.text)
            return None

        file_path = "card.png"
        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path

    except Exception as e:
        print("Ошибка генерации:", e)
        return None

# ================= ХЕНДЛЕРЫ =================

@dp.message(CommandStart())
async def start(message: types.Message):
    data = load_data()
    get_user(data, str(message.from_user.id))
    save_data(data)

    await message.answer(
        "💀 ULTIMATE TAROT ONLINE",
        reply_markup=main_keyboard()
    )

# 🔮 получить карту
@dp.message(lambda m: m.text == "🔮 Получить карту")
async def get_card(message: types.Message):
    await message.answer("🎨 Генерирую карту...")

    data = load_data()
    user = get_user(data, str(message.from_user.id))

    name = gen_name()
    text = gen_text()

    prompt = f"""
tarot card, {name}, dark fantasy, mystical, ultra detailed,
ornate frame, glowing symbols, cinematic lighting, masterpiece
"""

    img_path = generate_image(prompt)

    if img_path:
        photo = types.FSInputFile(img_path)
        await message.answer_photo(
            photo=photo,
            caption=f"🃏 {name}\n🔮 {text}"
        )
    else:
        await message.answer(
            f"🃏 {name}\n🔮 {text}\n\n⚠️ арт не загрузился"
        )

    user["cards"].append(name)
    save_data(data)

# 📦 коллекция
@dp.message(lambda m: m.text == "📦 Моя коллекция")
async def collection(message: types.Message):
    data = load_data()
    user = get_user(data, str(message.from_user.id))

    if not user["cards"]:
        await message.answer("📦 У тебя пока нет карт")
        return

    text = "\n".join(user["cards"][-10:])
    await message.answer(f"📦 Твои карты:\n{text}")

# ================= ЗАПУСК =================

async def main():
    print("🔥 БОТ ЗАПУЩЕН")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())