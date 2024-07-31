import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher, html, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from models import UserRequest, session
from matching import carb_content, glycemic_index, print_product_info


# Указать токен бота
TOKEN = ""

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = [
        [types.KeyboardButton(text="Расчитать ХЕ")],
        [types.KeyboardButton(text="о боте")],
        [types.KeyboardButton(text="Расчитать ГИ")],
        [types.KeyboardButton(text="Получить совет при диабете")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder='Выберите для продолжения')
    await message.answer(
        f"Привет, {message.from_user.full_name}! \nЯ бот для расчета хлебных единиц в продуктах и гликемического индекса в продуктах.\n"
        "Могу дать советы по управлению диабетом.\n"
        "Выберите одну из опций ниже:",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text == "Расчитать ХЕ")
async def calculate_he_prompt_handler(message: Message):
    await message.answer("Введите команду в формате: <code>/calculate_he хлеб 20</code>")

@dp.message(lambda message: message.text == "о боте")
async def about_bot_handler(message: Message):
    about_text = (
        "Этот бот предназначен для расчета хлебных единиц в продуктах и гликемического индекса в продуктах.\n"
        "Для расчета ХЕ укажите название продукта и его количество в граммах.\n"
        "Например: <code>/calculate_he яблоко 200</code>\n"
        "Для расчета ГИ укажите название продукта\n"
        "Например: <code>/calculate_gi яблоко</code>"
    )
    await message.reply(about_text)

@dp.message(lambda message: message.text == "Расчитать ГИ")
async def calculate_gi_prompt_handler(message: Message):
    await message.answer("Введите команду в формате: <code>/calculate_gi спаггети</code>")

@dp.message(lambda message: message.text == "Получить совет при диабете")
async def diabetes_tips_handler(message: Message):
    tips_text = (
        "Советы для диабетиков:\n"
        "1. Старайтесь есть продукты с низким гликемическим индексом.\n"
        "2. Следите за размером порций и избегайте переедания.\n"
        "3. Регулярно контролируйте уровень сахара в крови.\n"
        "4. Включите в рацион больше овощей, фруктов и цельнозерновых продуктов.\n"
        "5. Избегайте продуктов с высоким содержанием сахара и быстрых углеводов.\n"
        "6. Консультируйтесь с врачом для корректировки диеты и режима лечения."
    )
    await message.reply(tips_text)

@dp.message(Command("calculate_he"))
async def calculate_he_handler(message: Message):
    new_request = UserRequest(username=message.from_user.username,
                              user_id=message.from_user.id,
                              request_text=message.text)
    session.add(new_request)
    session.commit()
    try:
        command, product_name, quantity_str = message.text.split(maxsplit=2)
        quantity = int(quantity_str)
        if product_name.lower() in carb_content:
            carb_per_100g = carb_content[product_name.lower()]
            if carb_per_100g == 0:
                await message.reply(f"{product_name.capitalize()} не содержит значительное количество углеводов для расчета ХЕ.")
            else:
                bread_units = (carb_per_100g / 100) * quantity / 12
                await message.reply(f"В {quantity} граммах {product_name} - {bread_units:.2f} хлебных единиц")
        else:
            await message.reply("Продукт не найден")
    except ValueError:
        await message.reply("Использование: <code>/calculate_he хлеб 20</code>")

@dp.message(Command("calculate_gi"))
async def calculate_gi_handler(message: Message):
    new_request = UserRequest(username=message.from_user.username,
                              user_id=message.from_user.id,
                              request_text=message.text)
    session.add(new_request)
    session.commit()
    try:
        command, product_name = message.text.split(maxsplit=1)
        if product_name.lower() in glycemic_index:
            gi = glycemic_index[product_name.lower()]
            if gi <= 55:
                category = "низкий"
            elif 56 <= gi <= 69:
                category = "средний"
            else:
                category = "высокий"
            await message.reply(f"Гликемический индекс {product_name} составляет {gi}, что соответствует {category} ГИ.\nГИ показывает, насколько быстро продукт повышает уровень сахара в крови: низкий ГИ (0-55) — медленное повышение, средний (56-69) — умеренное, высокий (70 и выше) — быстрое.")
        else:
            await message.reply("Извините, продукт не найден в таблице гликемических индексов.")
    except ValueError:
        await message.reply("Пожалуйста, укажите название продукта после команды. Например: <code>/calculate_gi яблоко</code>")


# async def main() -> None:
#     session = AiohttpSession(proxy="http://proxy.server:3128")
#     bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)
#     await dp.start_polling(bot)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    print_product_info()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())