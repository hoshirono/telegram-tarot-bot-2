import asyncio
import random
import logging
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ChatAction
from dotenv import load_dotenv

# ===================== ENV =====================

load_dotenv()

TOKEN = os.getenv("TOKEN")
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY")

if not TOKEN:
    raise ValueError("❌ TOKEN не найден в .env")

# ===================== ЛОГИ =====================

logging.basicConfig(level=logging.INFO)

# ===================== БОТ =====================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===================== КНОПКА =====================

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💀 Дай мне судьбу")]
    ],
    resize_keyboard=True
)

# ===================== ПАМЯТЬ =====================

used_predictions = set()
user_memory = {}

# ===================== ПРЕДСКАЗАНИЯ =====================

def generate_prediction():
    subjects = ["Сегодня", "Твоя жизнь", "Судьба", "Эта неделя", "Вселенная"]
    verbs = ["скатится в", "превратится в", "станет", "развалится в"]
    trash = [
        "бессмысленную хуету",
        "цирк долбоебизма",
        "затянувшийся провал",
        "полный пиздец",
        "клоунаду без зрителей",
        "дно с подвалом",
        "жалкую попытку быть нормальным"
    ]
    endings = [
        "и ты это допустил",
        "и это полностью твоя вина",
        "но ты снова сделаешь вид, что всё ок",
        "и ты даже не поймёшь где сломался",
        "но ты уже привык к такому"
    ]
    sarcasm = [
        "Красавчик.",
        "Стабильность.",
        "Прогресс налицо.",
        "Это уже талант.",
        "Продолжай в том же духе (нет)."
    ]

    for _ in range(100):
        text = f"{random.choice(subjects)} {random.choice(verbs)} {random.choice(trash)}, {random.choice(endings)}. {random.choice(sarcasm)}"
        if text not in used_predictions:
            used_predictions.add(text)
            return text

    return "Даже судьба устала тебя генерировать."

# ===================== КАРТИНКИ =====================

def get_image():
    if not UNSPLASH_KEY:
        return None

    try:
        url = "https://api.unsplash.com/photos/random"
        headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}

        queries = [
            "creepy", "weird", "liminal", "dark", "surreal",
            "awkward", "strange person", "disturbing"
        ]

        params = {"query": random.choice(queries)}

        r = requests.get(url, headers=headers, params=params, timeout=10)

        if r.status_code == 200:
            return r.json()["urls"]["regular"]

    except Exception as e:
        print("Ошибка картинки:", e)

    return None

# ===================== СТАРТ =====================

@dp.message(lambda msg: msg.text == "/start")
async def start(msg: types.Message):
    await msg.answer(
        "Я уже здесь.\nНажми кнопку и получи своё.",
        reply_markup=keyboard
    )

# ===================== КНОПКА =====================

@dp.message(lambda msg: "судьбу" in msg.text.lower())
async def tarot(msg: types.Message):
    await bot.send_chat_action(msg.chat.id, ChatAction.TYPING)
    await asyncio.sleep(1.5)

    prediction = generate_prediction()

    insult = ""
    if msg.from_user.id in user_memory:
        insult = f"\n\nТы же писал: \"{user_memory[msg.from_user.id]}\". Это многое объясняет."

    text = f"🔮 {prediction}{insult}"

    image_url = get_image()

    if image_url:
        await msg.answer_photo(photo=image_url, caption=text)
    else:
        await msg.answer(text + "\n\n(даже интернет не захотел тебе помогать)")

# ===================== ЗАПОМИНАНИЕ =====================

@dp.message()
async def remember(msg: types.Message):
    if "судьбу" not in msg.text.lower():
        user_memory[msg.from_user.id] = msg.text[:100]

# ===================== ЗАПУСК =====================

async def main():
    print("✅ Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())