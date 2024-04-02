from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app import dp
from data import config

# from aiogram.contrib.middlewares.logging import LoggingMiddleware

# bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
# storage = MemoryStorage()
# dp = Dispatcher(bot, storage=storage)


# dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(text='salom')
async def salom(message: types.Message):
    await message.answer('Salom')
