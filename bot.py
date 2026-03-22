import asyncio
import random
import time
import os
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ChatAction

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

IMAGES_FOLDER = "images"

memory = {}
relation = {}
active_users = set()
last_photo_time = {}
last_messages = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="накаркай, гад 🐦‍⬛️")]],
    resize_keyboard=True
)

# ================== ОБУЧЕНИЕ ==================

def learn(user_id, text):
    memory.setdefault(user_id, []).append(text)
    if len(memory[user_id]) > 10:
        memory[user_id].pop(0)

    rel = relation.get(user_id, 0)

    if any(w in text.lower() for w in ["спасибо", "норм"]):
        rel += 1
    if any(w in text.lower() for w in ["иди", "тупой", "бред"]):
        rel -= 2

    relation[user_id] = max(-10, min(10, rel))


# ================== ЛОГИКА ДИАЛОГА ==================

def generate_reply(user_id, text):
    text_l = text.lower()

    # ================= ОСКОРБЛЕНИЯ =================
    insults = ["нахуй", "иди", "тупой", "дебил", "бред", "заткнись"]

    if any(w in text_l for w in insults):
        return random.choice([
            "слабовато. ты можешь лучше",
            "оскорбления — это максимум, на что ты способен?",
            "я ожидал чего-то интереснее",
            "ты даже злишься скучно",
            "продолжай. мне любопытно, насколько ты опустишься",
            "ты сейчас разговариваешь со мной или с собой?",
            "знаешь, что хуже? ты в это веришь",
            "даже агрессия у тебя без характера",
            "ещё. давай. ты почти сказал что-то осмысленное",
        ])

    # ================= КАК ТЫ =================
    if any(q in text_l for q in ["как ты", "как дела", "как настроение"]):
        return random.choice([
            "я существую. этого достаточно",
            "лучше, чем ты думаешь",
            "стабильно. ты вот нет",
            "я не меняюсь. в отличие от тебя",
            "нормально. наблюдаю",
            "мне не нужно настроение",
            "спокойно. слишком спокойно",
        ])

    # ================= И ЧТО =================
    if text_l.strip() in ["и что", "что", "ну и", "и?"]:
        return random.choice([
            "и всё. ты уже тратишь время",
            "и ничего. ты просто продолжаешь",
            "и ты всё ещё здесь",
            "и ты ожидал чего-то большего?",
            "и это был момент, где ты мог остановиться",
            "и ты сам не понял, зачем спросил",
            "и вот ты снова в этом месте",
        ])

    # ================= ПОЧЕМУ =================
    if "почему" in text_l:
        return random.choice([
            "потому что ты довёл до этого",
            "ты уже знаешь ответ",
            "это следствие, а не причина",
            "всё началось раньше, чем ты думаешь",
        ])

    # ================= КАК =================
    if "как" in text_l:
        return random.choice([
            "так же, как всегда — через ошибку",
            "слишком поздно спрашивать",
            "не так, как ты надеешься",
            "ты уже выбрал путь",
        ])

    # ================= КОРОТКИЕ ОТВЕТЫ =================
    if text_l in ["да", "нет", "ок", "понял"]:
        return random.choice([
            "вот и всё?",
            "ожидаемо",
            "и это весь твой ответ?",
            "ты мог бы сказать больше",
        ])

    # ================= ОБЩИЙ ДИАЛОГ =================
    base = random.choice([
        "ты снова здесь",
        "ничего не меняется",
        "я наблюдаю",
        "ты продолжаешь",
        "это становится привычкой",
        "интересно, когда ты поймёшь",
    ])

    # добавляем память
    if user_id in memory and random.random() < 0.4:
        base += f". {random.choice(memory[user_id])}"

    return base

    return base


# ================== ФОТО ==================

def get_image():
    files = [f for f in os.listdir(IMAGES_FOLDER) if f.endswith((".jpg",".png",".jpeg"))]
    if not files:
        return None
    return os.path.join(IMAGES_FOLDER, random.choice(files))


def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)

    if h > 0:
        return f"{h}ч {m}м"
    return f"{m}м"


async def send_photo(message):
    user_id = message.from_user.id
    now = time.time()

    last = last_photo_time.get(user_id, 0)
    left = 86400 - (now - last)

    if left > 0:
        await message.answer(random.choice([
            f"не сейчас. жди ещё {format_time(left)}",
            f"ты уже получил. приходи через {format_time(left)}",
            f"терпения нет? осталось {format_time(left)}",
            f"я сказал — позже. {format_time(left)}",
        ]))
        return

    path = get_image()

    if not path:
        await message.answer("пусто")
        return

    last_photo_time[user_id] = now

    await message.answer_photo(
        FSInputFile(path),
        caption=random.choice([
            "накаркал",
            "держи",
            "ты этого хотел",
            "оно теперь с тобой"
        ])
    )


# ================== ОБРАБОТЧИК ==================

@dp.message()
async def handle(message: types.Message):
    try:
        user_id = message.from_user.id
        text = message.text

        active_users.add(user_id)

        # кнопка
        if text == "накаркай, гад 🐦‍⬛️":
            await send_photo(message)
            return

        learn(user_id, text)

        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(random.uniform(1,2))

        reply = generate_reply(user_id, text)

        await message.answer(reply)

    except Exception as e:
        print("ERROR:", e)


# ================== НАБЛЮДЕНИЕ ==================

async def watcher():
    while True:
        await asyncio.sleep(300)

        hour = time.localtime().tm_hour

        for user in active_users:
            try:
                if 1 <= hour <= 5:
                    if random.random() < 0.3:
                        await bot.send_message(user, random.choice([
                            "не спишь?",
                            "я рядом",
                            "тишина странная"
                        ]))
                        await asyncio.sleep(2)
                        await bot.send_message(user, random.choice([
                            "я всё ещё здесь",
                            "не игнорируй"
                        ]))
                else:
                    if random.random() < 0.2:
                        await bot.send_message(user, random.choice([
                            "я думаю о тебе",
                            "ты не закончил",
                            "что-то не так"
                        ]))
            except:
                pass


# ================== СТАРТ ==================

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "каркуша наблюдает",
        reply_markup=keyboard
    )


# ================== ЗАПУСК ==================

async def main():
    print("каркуша исправлен")

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(watcher())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())