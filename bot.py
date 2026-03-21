import asyncio
import random
import os
import time
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
last_message_time = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔮 ну давай, удиви меня")]],
    resize_keyboard=True
)

# 😏 СТЁБ + ПРЕДСКАЗАНИЯ
SUBJECTS = ["ты", "твоя гениальная стратегия", "твой план"]
ACTIONS = [
    "снова пойдёт не туда",
    "развалится в самый неподходящий момент",
    "приведёт к максимально странному результату",
]
IRONY = [
    "но ты же этого и хотел, да?",
    "всё под контролем, конечно",
    "прямо как ты и планировал",
]

# 🎴 карты
CARD1 = ["Император", "Шут", "Гений", "Стратег"]
CARD2 = ["сомнительных решений", "кринж-логики", "самообмана"]

# 🧠 генерация предсказания
def generate_prediction(user_id):
    while True:
        text = f"{random.choice(SUBJECTS)} {random.choice(ACTIONS)}, {random.choice(IRONY)}"
        if text not in used_predictions:
            used_predictions.add(text)
            break

    if user_id in memory and memory[user_id]:
        last = memory[user_id][-1]
        text += f"\n\nкстати, '{last}' — это вообще отдельный уровень"

    return text

def generate_card():
    return f"{random.choice(CARD1)} {random.choice(CARD2)}"

# 💀 генерация картинки (с fallback)
async def generate_image(prompt):
    async with aiohttp.ClientSession() as session:
        try:
            url = "https://router.huggingface.co/hf-inference/models/stabilityai/sdxl-turbo"

            headers = {
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            }

            payload = {
                "inputs": f"{prompt}, surreal, cursed, weird, absurd"
            }

            async with session.post(url, headers=headers, json=payload, timeout=15) as r:
                if r.status == 200:
                    return BytesIO(await r.read())

        except:
            pass

    # fallback (чтобы НЕ ломалось)
    fallback = random.choice([
        "https://picsum.photos/512?random=1",
        "https://picsum.photos/512?random=2"
    ])

    async with aiohttp.ClientSession() as session:
        async with session.get(fallback) as r:
            return BytesIO(await r.read())

# 🎴 отправка
async def send_card(message: types.Message):
    user_id = message.from_user.id

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    card = generate_card()
    prediction = generate_prediction(user_id)

    text = f"🃏 {card}\n\n🔮 {prediction}"

    img = await generate_image(text)

    photo = BufferedInputFile(img.read(), filename="img.jpg")
    await message.answer_photo(photo=photo, caption=text)

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "ну давай посмотрим, насколько ты сегодня облажаешься",
        reply_markup=keyboard
    )

# 🎰 кнопка
@dp.message(lambda m: m.text == "🔮 ну давай, удиви меня")
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

    await message.answer("записал. потом пригодится.", reply_markup=keyboard)

# 👁 инициатива (НЕ БОЛЬШЕ 2 РАЗ В ДЕНЬ)
async def watcher():
    while True:
        await asyncio.sleep(60)

        for user_id in list(active_users):
            now = time.time()
            last = last_message_time.get(user_id, 0)

            # 12 часов между сообщениями
            if now - last < 43200:
                continue

            text = random.choice([
                "я всё ещё думаю о твоём последнем решении",
                "интересно, ты уже понял, где ошибся?",
                "ну что, всё идёт по плану? :)",
            ])

            try:
                await bot.send_message(user_id, f"👁 {text}")
                last_message_time[user_id] = now
            except:
                pass

# ▶️ запуск
async def main():
    print("бот запущен")
    asyncio.create_task(watcher())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())