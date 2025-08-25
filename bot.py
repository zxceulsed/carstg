import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from parser import get_random_cars
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from db import init_db

# вставь сюда токен своего бота
TOKEN = "7644070125:AAEoq74URgg-zXfIH5vSVBRxPZxUlj0ugfo"
CHAT_ID = -1002898879716

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

time_send = ["08:00","10:00", "12:00", "14:00","16:00","18:00","20:00"]

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("zxc")

@dp.message(Command("next"))
async def next_time(message: types.Message):
    now = datetime.now()
    today_times = []

    for t in time_send:
        h, m = map(int, t.split(":"))
        candidate = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if candidate < now:
            candidate += timedelta(days=1)  # перенос на завтра
        today_times.append(candidate)

    nearest = min(today_times)
    await message.answer(f"⏳ Следующая рассылка в {nearest.strftime('%d.%m %H:%M')}")


# 📌 функция отправки объявления
async def send_ad():
    cars = get_random_cars(count=1)
    if not cars:
        await bot.send_message(chat_id=CHAT_ID, text="⚠️ Объявлений не найдено.")
        return

    car = cars[0]

    # текст, который будет в описании первой фотки
    caption = f"""
🚗 {car['title']}
💵 {car['price']}
📍 {car['location']}
📋 {car['params']}

{car['description']}

👤 <a href="{car['link']}">Владелец</a>
"""

    if car["photos"]:
        media = []
        for idx, url in enumerate(car["photos"][:10]):
            if idx == 0:
                media.append(types.InputMediaPhoto(media=url, caption=caption.strip(), parse_mode="HTML"))
            else:
                media.append(types.InputMediaPhoto(media=url))
        await bot.send_media_group(chat_id=CHAT_ID, media=media)
    else:
        await bot.send_message(chat_id=CHAT_ID, text=caption.strip(), parse_mode="HTML")




async def main():
    # добавляем задачи из списка
    for t in time_send:
        h, m = map(int, t.split(":"))
        scheduler.add_job(send_ad, "cron", hour=h, minute=m, name=f"Рассылка {t}")
    init_db()
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
