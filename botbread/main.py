import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, or_f, Command
from aiogram.types import Message
from botbread.models import UserRequest, session
from aiogram.client.session.aiohttp import AiohttpSession

# указать токен бота, получить у botFather в телеграме
TOKEN = ""

dp = Dispatcher()


# cловарь с углеводным содержанием продуктов для расчета ХЕ
carb_content = {
    'яблоко': 10,
    'хлеб': 20,
    'картошка': 15,
    'банан': 25,
    'рис': 30,
    'макароны': 35,
    'помидор': 4,
    'огурец': 3,
    'молоко': 5,
    'сыр': 1,
    'яйцо': 1,
    'гречка': 30,
    'салат': 2,
    'мандарин': 10,
    'апельсин': 9,
    'лимон': 3,
    'сахар': 100,
    # Продукты без углеводов
    'курица': 0, 
    'говядина': 0,
    'свинина': 0,
    'рыба': 0,
    'масло': 0,
    'соль': 0,
    'перец': 0,
    'вода': 0,
}


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

    kb = [
        [types.KeyboardButton(text="/calculate_he")],
        [types.KeyboardButton(text="/about_bot")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder='Выберите для продолжения')
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! \nЯ бот для расчета хлебных единиц в продуктах. Для начала работы укажите название продукта и его количество в граммах. \nНапример, /calculate_he яблоко 200", reply_markup=keyboard)


@dp.message(or_f(Command("calculate_he")))
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
                await message.reply(f"{product_name.capitalize()} соответствующий продукт не содержит углеводов или содержит их в незначительных количествах, которые не учитываются при расчете хлебных единиц. Например, мясо, рыба, масло, соль, перец и вода не содержат углеводов или содержат их в очень низких количествах, которые не влияют на уровень глюкозы в крови.")
            else:
                bread_units = (carb_per_100g / 100) * quantity / 12
                await message.reply(f"В {quantity} граммах {product_name} - {bread_units:.2f} хлебных единиц")
        else:
            await message.reply("Продукт не найден")
    except ValueError:
        await message.reply("Использование: /calculate_he [название продукта] [количество в граммах]")

@dp.message(or_f(Command('about_bot')))
async def about_bot_handler(message: Message):
    about_text = (
        "Этот бот предназначен для расчета хлебных единиц в продуктах. "
        "Для расчета укажите название продукта и его количество в граммах. "
        "Например, /calculate_he яблоко 200"
    )
    await message.reply(about_text)


async def main() -> None:
    session = AiohttpSession(proxy="http://proxy.server:3128")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())