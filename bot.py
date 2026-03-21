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
active_users = set()
last_message_time = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔮 ну давай, предскажи мне жизнь")]],
    resize_keyboard=True
)

# 💀 СЦЕНАРИИ
SCENARIOS = [
    {
        "name": "Социальный провал",
        "text": [
            "ты скажешь что-то, после чего станет неловко",
            "ты попробуешь пошутить и пожалеешь",
        ],
        "irony": [
            "но ты сделаешь вид, что всё нормально",
            "и это запомнят",
        ],
        "prompt": "awkward silence, people staring, realistic photo"
    },
    {
        "name": "Иллюзия контроля",
        "text": [
            "тебе будет казаться, что всё под контролем",
            "ты будешь уверен в своём плане",
        ],
        "irony": [
            "и всё сломается в этот момент",
            "и это будет глупо",
        ],
        "prompt": "man confident but chaos behind him, surreal photo"
    },
    {
        "name": "Абсурдная ошибка",
        "text": [
            "ты сделаешь ошибку, которую сложно объяснить",
            "ты сам не поймёшь, зачем это сделал",
        ],
        "irony": [
            "но объяснение придумаешь",
            "и даже поверишь в него",
        ],
        "prompt": "confused person, surreal weird situation"
    },
    {
        "name": "Неловкое сообщение",
        "text": [
            "ты отправишь сообщение и сразу пожалеешь",
            "ты перечитаешь это и зависнешь",
        ],
        "irony": [
            "но уже поздно",
            "и ответ будет хуже",
        ],
        "prompt": "person staring at phone in shock, night"
    },
    {
        "name": "Самообман",
        "text": [
            "ты убедишь себя, что всё нормально",
            "ты проигнорируешь очевидное",
        ],
        "irony": [
            "и это будет ошибкой",
            "но не сразу",
        ],
        "prompt": "person smiling but everything collapsing"
    },
]

# 🧠 генерация
def generate_scenario():
    s = random.choice(SCENARIOS)

    text = f"{random.choice(s['text'])}, {random.choice(s['irony'])}"
    return s["name"], text, s["prompt"]

# 💀 генерация картинки
async def generate_image(prompt):
    async with aiohttp.ClientSession() as session:
        try:
            url = "https://router.huggingface.co/hf-inference/models/stabilityai/sdxl-turbo"

            headers = {
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            }

            payload = {
                "inputs": f"{prompt}, surreal, cursed, weird, realistic photo"
            }

            async with session.post(url, headers=headers, json=payload, timeout=20) as r:
                if r.status == 200:
                    return BytesIO(await r.read())

        except:
            pass

    # fallback (чтобы не ломалось)
    fallback = random.choice([
        "https://picsum.photos/512?random=1",
        "https://picsum.photos/512?random=2",
        "https://picsum.photos/512?random=3",
    ])

    async with aiohttp.ClientSession() as session:
        async with session.get(fallback) as r:
            return BytesIO(await r.read())

# 🎴 отправка
async def send_card(message: types.Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    card, prediction, prompt = generate_scenario()

    text = f"🃏 {card}\n\n🔮 {prediction}"

    img = await generate_image(prompt)

    photo = BufferedInputFile(img.read(), filename="img.jpg")
    await message.answer_photo(photo=photo, caption=text)

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "ну давай посмотрим, что у тебя сегодня сломается",
        reply_markup=keyboard
    )

# 🎰 кнопка
@dp.message(lambda m: m.text == "🔮 ну давай, предскажи мне жизнь")
async def spin(message: types.Message):
    active_users.add(message.from_user.id)
    await send_card(message)

# 🧠 память (ТОЛЬКО тут используется)
@dp.message()
async def remember(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    memory.setdefault(user_id, []).append(message.text)

    if len(memory[user_id]) > 50:
        memory[user_id].pop(0)

    reply = f"интересно ты пишешь:\n'{message.text}'\n\nуверен, это тебе поможет"

    await message.answer(reply, reply_markup=keyboard)

# 👁 инициатива (макс 2 раза в день)
async def watcher():
    while True:
        await asyncio.sleep(60)

        for user_id in list(active_users):
            now = time.time()
            last = last_message_time.get(user_id, 0)

            if now - last < 43200:
                continue

            text = random.choice([
                "я всё ещё думаю о твоих решениях",
                "ты правда уверен в себе?",
                "интересно, когда ты заметишь",
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