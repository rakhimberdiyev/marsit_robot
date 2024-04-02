import asyncio
import logging

from aiogram import Bot, Dispatcher
from data.config import ADMINS


async def on_startup_notify(dp: Dispatcher, user: str):
    for admin in ADMINS:
        try:
            if user != None:
                await dp.bot.send_message(chat_id="-1002102115794",
                                        text=f"{user}\n\nUshbu user barcha jarayonni yakunladi", parse_mode=None)
            else:
                await dp.bot.send_message(admin, "Bot ishga tushdi")

        except Exception as err:
            logging.exception(err)


async def on_shutdown_notify(bot: Bot):
    """Notify admins about successful stop"""
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=admin, text="Bot to'xtadi.")
        except Exception as err:
            logging.exception(err)
