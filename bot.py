import asyncio
import random
import logging
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ChatAction

# ===================== НАСТРОЙКИ =====================

TOKEN = "ТВОЙ_TELEGRAM_TOKEN"
UNSPLASH_KEY = "ТВОЙ_UNSPLASH_ACCESS_KEY"

# ===================== ЛОГИ =====================

logging.basicConfig(level=logging.INFO)

# ===================== БОТ =====================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===================== КНОПКА =====================

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔮 Дай мне кринж-судьбу")]
    ],
    resize_keyboard=True
)

# ===================== ПАМЯТЬ =====================

used_predictions = set()
user_memory = {}

# ===================== ГЕНЕРАЦИЯ ПРЕДСКАЗАНИЙ =====================

subjects = [
    "Сегодня", "В ближайшее время", "Судьба", "Вселенная", "Ты",
    "Этот день", "Твоя жизнь", "Реальность"
]

actions = [
    "подкинет тебе шанс", "снова проверит тебя", "решит пошутить над тобой",
    "даст тебе знак", "оставит тебя в недоумении", "сделает вид, что всё нормально",
    "покажет тебе правду", "сломает твои ожидания"
]

outcomes = [
    "но ты его пропустишь",
    "и ты сделаешь всё наоборот",
    "и это было ошибкой",
    "но ты не поймёшь этого сразу",
    "и станет только хуже",
    "но ты будешь доволен собой",
    "и это даже не самый плохой вариант",
    "но всем будет всё равно"
]

sarcasm = [
    "В целом, стабильно.",
    "Ничего нового.",
    "Ты держишь уровень.",
    "Это уже стиль жизни.",
    "Можно было хуже, но ты справился.",
    "Гордиться нечем, но и стыдиться лень.",
    "Ты хотя бы стараешься. Наверное."
]

def generate_prediction():
    for _ in range(100):
        text = f"{random.choice(subjects)} {random.choice(actions)}, {random.choice(outcomes)}. {random.choice(sarcasm)}"
        if text not in used_predictions:
            used_predictions.add(text)
            return text
    return "Ты исчерпал даже плохие варианты. Поздравляю."

# ===================== ПОИСК КАРТИНОК =====================

def get_image(query):
    try:
        url = "https://api.unsplash.com/photos/random"
        headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
        params = {"query": query}

        r = requests.get(url, headers=headers, params=params, timeout=10)

        if r.status_code == 200:
            data = r.json()
            return data["urls"]["regular"]
        else:
            return None
    except:
        return None

# ===================== СЦЕНАРИИ (ФОТО + ТЕМА) =====================

image_themes = [
    "creepy empty room",
    "strange person staring",
    "liminal space",
    "weird office situation",
    "awkward social moment",
    "sad clown",
    "distorted face",
    "dark hallway",
    "surreal photo",
    "uncomfortable situation"
]

# ===================== СТАРТ =====================

@dp.message(lambda msg: msg.text == "/start")
async def start(msg: types.Message):
    await msg.answer(
        "Я уже здесь.\nЖми кнопку. Посмотрим, насколько всё плохо.",
        reply_markup=keyboard
    )

# ===================== ОСНОВНАЯ КНОПКА =====================

@dp.message(lambda msg: "кринж" in msg.text.lower())
async def tarot(msg: types.Message):
    await bot.send_chat_action(msg.chat.id, ChatAction.TYPING)
    await asyncio.sleep(1.5)

    prediction = generate_prediction()

    # персональная подколка (только если писал текст)
    insult = ""
    if msg.from_user.id in user_memory:
        memory = user_memory[msg.from_user.id]
        insult = f"\n\nКстати, ты писал: \"{memory}\". Это многое объясняет."

    text = f"🔮 {prediction}{insult}"

    theme = random.choice(image_themes)
    image_url = get_image(theme)

    if image_url:
        await msg.answer_photo(photo=image_url, caption=text)
    else:
        await msg.answer(text + "\n\n(даже картинка не захотела появляться)")

# ===================== ЗАПОМИНАНИЕ СООБЩЕНИЙ =====================

@dp.message()
async def remember(msg: types.Message):
    if "кринж" not in msg.text.lower():
        user_memory[msg.from_user.id] = msg.text[:100]

# ===================== ЗАПУСК =====================

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())