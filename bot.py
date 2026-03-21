import asyncio
import random
import logging
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ChatAction

# ===================== НАСТРОЙКИ =====================

TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН"
UNSPLASH_KEY = "ВСТАВЬ_СЮДА_UNSPLASH_KEY"

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

# ===================== ГЕНЕРАЦИЯ ПРЕДСКАЗАНИЙ =====================

def generate_prediction():
    subjects = [
        "Сегодня", "Эта неделя", "Твоя жизнь", "Судьба", "Вселенная"
    ]

    actions = [
        "превратится в", "будет выглядеть как", "станет",
        "скатится в", "окажется"
    ]

    trash = [
        "бессмысленная хуета",
        "цирк долбоебизма",
        "затянувшийся фейл",
        "полный пиздец",
        "дешёвая пародия на успех",
        "хаос, который ты называешь планом",
        "медленный краш твоих надежд",
        "то самое дно, которое ты копаешь дальше"
    ]

    endings = [
        "и ты это допустил",
        "и это полностью твоя вина",
        "но ты сделаешь вид, что всё нормально",
        "и ты опять ничего не поймёшь",
        "но ты уже привык к такому",
        "и да, лучше не станет"
    ]

    sarcasm = [
        "Красавчик.",
        "Стабильность.",
        "Ну ты даёшь.",
        "Всё по плану (нет).",
        "Это уже стиль жизни.",
        "Прогресс налицо. К сожалению."
    ]

    for _ in range(100):
        text = f"{random.choice(subjects)} {random.choice(actions)} {random.choice(trash)}, {random.choice(endings)}. {random.choice(sarcasm)}"
        if text not in used_predictions:
            used_predictions.add(text)
            return text

    return "Даже судьба устала тебя генерировать."

# ===================== КАРТИНКИ =====================

def get_image():
    try:
        url = "https://api.unsplash.com/photos/random"
        headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}

        themes = [
            "creepy face", "liminal space", "weird situation",
            "dark room", "awkward person", "surreal photo"
        ]

        params = {"query": random.choice(themes)}

        r = requests.get(url, headers=headers, params=params, timeout=10)

        if r.status_code == 200:
            return r.json()["urls"]["regular"]
    except:
        pass

    return None

# ===================== СТАРТ =====================

@dp.message(lambda msg: msg.text == "/start")
async def start(msg: types.Message):
    await msg.answer(
        "Я уже здесь.\nНажми кнопку и получи то, что заслужил.",
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
        await msg.answer(text + "\n\n(даже картинка отказалась участвовать)")

# ===================== ЗАПОМИНАНИЕ =====================

@dp.message()
async def remember(msg: types.Message):
    if "судьбу" not in msg.text.lower():
        user_memory[msg.from_user.id] = msg.text[:100]

# ===================== ЗАПУСК =====================

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())