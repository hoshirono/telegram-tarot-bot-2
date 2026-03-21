import asyncio
import random
import time
from io import BytesIO

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.enums import ChatAction

# 🔑 ВСТАВЬ СЮДА
TOKEN = "ТВОЙ_ТЕЛЕГРАМ_ТОКЕН"
HF_TOKEN = "ТВОЙ_HF_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher()

memory = {}
active_users = set()
last_message_time = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔮 ну давай, разъеби мою судьбу")]],
    resize_keyboard=True
)

# 🧠 генерация сценариев (динамика)
subjects = [
    "ты", "твоя жизнь", "твои решения", "твоя неделя",
    "твой мозг", "твои попытки быть нормальным"
]

events = [
    "попытаешься что-то исправить",
    "решишь, что понял жизнь",
    "снова сделаешь выбор",
    "скажешь лишнее",
    "поверишь в себя (зря)"
]

failures = [
    "и всё пойдет по пизде",
    "и это обернется кринжем",
    "и будет максимально неловко",
    "и ты потом будешь это вспоминать ночью",
    "и это было лишним"
]

irony = [
    "но ты будешь делать вид, что так и задумано",
    "и никто не поверит тебе",
    "и ты сам не поймешь, зачем это сделал",
    "и это станет твоим новым дном",
    "и да, это запомнят"
]

image_prompts = [
    "awkward silence, people staring, realistic photo",
    "man failing in public, embarrassing moment, realistic",
    "confused person in chaos, weird situation, photo",
    "person alone at night thinking, depressed realistic",
    "strange absurd situation, uncanny valley photo"
]


def generate_prediction(user_id=None):
    base = f"{random.choice(subjects)} сегодня {random.choice(events)}, {random.choice(failures)}, {random.choice(irony)}."

    extra = random.choice([
        "в целом, стандартный твой день",
        "ничего нового, если честно",
        "ты стабилен в этом",
        "можно было и хуже, но ты справился",
        "хотя ты явно старался сделать хуже"
    ])

    # персональное унижение (только если писал)
    if user_id and user_id in memory and memory[user_id]:
        user_word = random.choice(memory[user_id])
        personal = f"\n\nкстати, ты писал: '{user_word}' — это многое объясняет."
    else:
        personal = ""

    return base + "\n\n" + extra + personal


def generate_prompt():
    return random.choice(image_prompts)


# 💀 генерация картинки
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

                    file = BytesIO(data)
                    file.name = "img.jpg"
                    file.seek(0)

                    return file
    except:
        pass

    # fallback
    fallback_url = f"https://picsum.photos/512?random={random.randint(1,10000)}"

    async with aiohttp.ClientSession() as session:
        async with session.get(fallback_url) as r:
            data = await r.read()
            file = BytesIO(data)
            file.name = "img.jpg"
            file.seek(0)
            return file


# 🎴 отправка карты
async def send_card(message: types.Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(random.uniform(1, 2))

    prediction = generate_prediction(message.from_user.id)
    prompt = generate_prompt()

    img = await generate_image(prompt)

    photo = InputFile(img)
    await message.answer_photo(photo=photo, caption=f"🔮 {prediction}")


# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    active_users.add(message.from_user.id)

    await message.answer(
        "я уже здесь.\n\nжми кнопку и посмотрим, насколько всё плохо",
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
        f"ты написал: '{message.text}'\n\nя это запомнил.",
        reply_markup=keyboard
    )


# 👁 инициатива (2 раза в день)
async def watcher():
    while True:
        await asyncio.sleep(60)

        for user_id in list(active_users):
            now = time.time()
            last = last_message_time.get(user_id, 0)

            if now - last < 43200:
                continue

            text = random.choice([
                "я тут подумал о тебе",
                "ты ведь не забыл про меня?",
                "знаешь, я всё вижу",
                "ты странно себя ведёшь",
                "мне кажется, ты опять что-то сделал не так"
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