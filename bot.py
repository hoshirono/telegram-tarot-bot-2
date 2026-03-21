import asyncio
import random
import os
from io import BytesIO

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.enums import ChatAction

TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

memory = {}
used_predictions = set()
active_users = set()

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔮 получить проклятие")]],
    resize_keyboard=True
)

# 🧠 генерация текста
SUBJECTS = ["ты", "твоя жизнь", "твои попытки"]
ACTIONS = ["разваливаются", "уходят в никуда", "ломаются"]
INSULTS = ["как обычно", "потому что это ты", "и это жалко"]

CARD1 = ["Император", "Шут", "Жертва", "Дурак"]
CARD2 = ["кринжа", "позора", "самообмана"]

# 🧠 уникальное предсказание
def generate_prediction(user_id):
    while True:
        text = f"{random.choice(SUBJECTS)} {random.choice(ACTIONS)} {random.choice(INSULTS)}"
        if text not in used_predictions:
            used_predictions.add(text)
            break

    if user_id in memory and memory[user_id]:
        text += f"\n\nты писал: '{memory[user_id][-1]}'"

    return text

def generate_card():
    return f"{random.choice(CARD1)} {random.choice(CARD2)}"

# 💀 генерация ПРОКЛЯТОЙ картинки
async def generate_cursed_image(prompt):
    async with aiohttp.ClientSession() as session:
        try:
            url = "https://router.huggingface.co/hf-inference/models/stabilityai/sdxl-turbo"

            headers = {
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            }

            payload = {
                "inputs": f"{prompt}, horror, cursed image, distorted face, surreal nightmare, dark lighting",
            }

            async with session.post(url, headers=headers, json=payload, timeout=20) as r:
                if r.status == 200:
                    return BytesIO(await r.read())
                else:
                    print(await r.text())
                    return None

        except Exception as e:
            print("IMG ERROR:", e)
            return None

# 🎴 отправка карты
async def send_card(message: types.Message):
    user_id = message.from_user.id

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    card = generate_card()
    prediction = generate_prediction(user_id)

    prompt = f"{card}, {prediction}"

    img = await generate_cursed_image(prompt)

    text = f"🃏 {card}\n\n🔮 {prediction}"

    if img:
        photo = BufferedInputFile(img.read(), filename="cursed.jpg")
        await message.answer_photo(photo=photo, caption=text)
    else:
        await message.answer(text + "\n(даже картинка не захотела появляться)")

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "я покажу тебе то, что лучше не видеть",
        reply_markup=keyboard
    )

# 🎰 кнопка
@dp.message(lambda m: m.text == "🔮 получить проклятие")
async def spin(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    await send_card(message)

# 🧠 память
@dp.message()
async def remember(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    memory.setdefault(user_id, []).append(message.text)

    if len(memory[user_id]) > 50:
        memory[user_id].pop(0)

    await message.answer("я это запомнил", reply_markup=keyboard)

# 👁 инициатива
async def watcher():
    while True:
        await asyncio.sleep(random.randint(60, 120))

        if not active_users:
            continue

        user_id = random.choice(list(active_users))

        text = random.choice([
            "я всё ещё думаю о тебе",
            "ты не должен был это видеть",
            "это только начало",
        ])

        try:
            await bot.send_message(user_id, f"👁 {text}")
        except:
            pass

# ▶️ запуск
async def main():
    print("бот запущен")
    asyncio.create_task(watcher())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())