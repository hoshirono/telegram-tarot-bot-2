import asyncio
import random
import time
from io import BytesIO

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.enums import ChatAction

TOKEN = "ТВОЙ_ТОКЕН"
HF_TOKEN = "ТВОЙ_HF_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher()

memory = {}
active_users = set()
last_message_time = {}
used_predictions = set()  # ✅ фикс

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔮 ну давай, разъеби мою судьбу")]],
    resize_keyboard=True
)

# 🧠 генерация текста
def generate_prediction(user_id=None):
    subjects = [
        "Сегодня", "Эта неделя", "Твоя жизнь", "Судьба",
        "Реальность вокруг тебя", "Твои попытки жить нормально"
    ]

    actions = [
        "будет выглядеть как", "превратится в", "станет",
        "скатится в", "окажется", "будет ощущаться как"
    ]

    trash = [
        "бессмысленная хуета",
        "цирк долбоебизма",
        "медленный краш твоих ожиданий",
        "жалкая попытка всё исправить",
        "хаос без смысла",
        "пиздец, но уже привычный"
    ]

    endings = [
        "и ты даже не заметишь, как это началось.",
        "но ты сделаешь вид, что всё ок.",
        "и да, ты опять виноват.",
        "но ты уже привык.",
        "и ты ничего не поменяешь."
    ]

    sarcasm = [
        "Красавчик.",
        "Стабильность.",
        "Ну ты даёшь.",
        "Это уже стиль жизни.",
        "Всё по канону."
    ]

    for _ in range(200):
        text = f"{random.choice(subjects)} {random.choice(actions)} {random.choice(trash)}, {random.choice(endings)} {random.choice(sarcasm)}"

        if text not in used_predictions:
            used_predictions.add(text)

            # персонализация
            if user_id and user_id in memory and memory[user_id]:
                user_msg = random.choice(memory[user_id])
                text += f"\n\nты писал: '{user_msg}' — это многое объясняет."

            return text

    return "Даже судьба устала придумывать тебе новые провалы."

# 🖼 генерация картинки
async def generate_image(prompt):
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://router.huggingface.co/hf-inference/models/stabilityai/sdxl-turbo"

            headers = {
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            }

            payload = {
                "inputs": f"{prompt}, cursed, absurd, realistic photo"
            }

            async with session.post(url, headers=headers, json=payload, timeout=25) as r:
                if r.status == 200:
                    data = await r.read()

                    return BufferedInputFile(data, filename="img.jpg")
    except:
        pass

    # fallback
    fallback = f"https://picsum.photos/512?random={random.randint(1,9999)}"

    async with aiohttp.ClientSession() as session:
        async with session.get(fallback) as r:
            data = await r.read()
            return BufferedInputFile(data, filename="img.jpg")


# 🧠 промпты
def generate_prompt():
    return random.choice([
        "awkward silence, people staring",
        "man embarrassed in public",
        "weird surreal situation",
        "person alone at night sad",
        "absurd uncanny photo"
    ])


# 🎴 отправка
async def send_card(message: types.Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    prediction = generate_prediction(message.from_user.id)
    prompt = generate_prompt()

    photo = await generate_image(prompt)

    await message.answer_photo(photo=photo, caption=f"🔮 {prediction}")


# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "жми кнопку и посмотрим, как ты сегодня облажаешься",
        reply_markup=keyboard
    )


# 🎰 кнопка
@dp.message(lambda m: m.text == "🔮 ну давай, разъеби мою судьбу")
async def spin(message: types.Message):
    active_users.add(message.from_user.id)
    await send_card(message)


# 🧠 память
@dp.message()
async def remember(message: types.Message):
    user_id = message.from_user.id
    active_users.add(user_id)

    memory.setdefault(user_id, []).append(message.text)

    if len(memory[user_id]) > 100:
        memory[user_id].pop(0)

    await message.answer(
        f"я запомнил: '{message.text}'",
        reply_markup=keyboard
    )


# 👁 инициатива
async def watcher():
    while True:
        await asyncio.sleep(60)

        for user_id in list(active_users):
            now = time.time()
            last = last_message_time.get(user_id, 0)

            if now - last < 43200:
                continue

            text = random.choice([
                "я всё ещё думаю о тебе",
                "ты странно себя ведёшь",
                "ты ведь не забыл про меня?",
                "мне кажется, ты снова ошибся"
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