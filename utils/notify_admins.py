import asyncio
import logging

from aiogram import Bot, Dispatcher
from data.config import ADMINS
from aiogram.dispatcher import FSMContext


message_ids = {}
message_num = {"id_sh": 1, "id_v": 1, "id_b": 1}
async def on_startup_notify(dp: Dispatcher, user: str, id, address):
    for admin in ADMINS:
        try:
            if user != None:
                    if 'Filial' not in user:
                        if address == 'shahar':
                            msg = await dp.bot.send_message(chat_id="-1002088539701",
                                                            text=f"Id: {message_num['id_sh']}\n{user}", parse_mode=None, message_thread_id=9)
                            message_ids[id] = msg.message_id
                            message_num['id_sh'] += 1
                            
                        elif address == 'viloyat':
                            msg = await dp.bot.send_message(chat_id="-1002088539701",
                                                            text=f"Id: {message_num['id_v']}\n{user}", parse_mode=None, message_thread_id=6)
                            message_ids[id] = msg.message_id
                            message_num['id_v'] += 1
                        elif address == 'boshqa':
                            msg = await dp.bot.send_message(chat_id="-1002088539701",
                                                            text=f"Id: {message_num['id_b']}\n{user}", parse_mode=None, message_thread_id=8)
                            message_ids[id] = msg.message_id
                            message_num['id_b'] += 1

                    elif 'Filial' in user:
                        if address == 'shahar':
                            await dp.bot.send_message(chat_id="-1002088539701",
                                                    text=f"Id: {message_num['id_sh']}\n{user}\n\nUshbu user barcha jarayonni yakunladi", message_thread_id=9)
                            last_msg_id = message_ids[id]
                            message_num['id_sh'] += 1
                            await dp.bot.delete_message(chat_id='-1002088539701',
                                                        message_id=last_msg_id)
                        elif address == 'viloyat':
                            await dp.bot.send_message(chat_id="-1002088539701",
                                                    text=f"Id: {message_num['id_v']}\n{user}\n\nUshbu user barcha jarayonni yakunladi", message_thread_id=6)
                            last_msg_id = message_ids[id]
                            message_num['id_v'] += 1
                            await dp.bot.delete_message(chat_id='-1002088539701',
                                                        message_id=last_msg_id)
                        elif address == 'boshqa':
                            await dp.bot.send_message(chat_id="-1002088539701",
                                                    text=f"Id: {message_num['id_b']}\n{user}\n\nUshbu user barcha jarayonni yakunladi", message_thread_id=8)
                            last_msg_id = message_ids[id]
                            message_num['id_b'] += 1
                            await dp.bot.delete_message(chat_id='-1002088539701',
                                                        message_id=last_msg_id)

                            del message_ids[id]
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
