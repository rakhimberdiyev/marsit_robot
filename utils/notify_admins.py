import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from data.config import ADMINS
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile
from keyboards.inline.all_inlines import application, application_ru



message_ids = {}
message_num = {"id_sh": 1, "id_v": 1, "id_b": 1}
async def on_startup_notify(dp: Dispatcher, user: str, id, address, language):
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
                        
                        await asyncio.sleep(30)
                        if language == 'uz':
                            
                            video = "BAACAgIAAxkBAAIj2WYguN4b7rToZY1zrMJW5JoohcAbAAKQSAACwrPwSLn2sm6Y3jLENAQ"
                            await dp.bot.send_video(chat_id=id, video=video, caption="""
😎 Farzandingiz Toshkent shahridagi yetakchi IT kurslarda o‘qishini istaysizmi?

🙌🏻 Unda «Mars IT»ga marhamat!

Bizning oliy maqsadimiz: 8 yoshdan 16 yoshgacha bo‘lgan bolalarga zamonaviy kompyuter ko‘nikmalarini o‘rgatib kelajakka tayyorlash!

👨🏻‍💻 «Mars IT» 3 yildan buyon maxsus o‘quv metodikasi yordamida bolalarga Dasturlash va dizayn ko‘nikmalarini o’rgatib keladi.

Kurs davomida farzandingiz:
- Zamonaviy atmosferada bilim oladi;
- Jamoa bilan ishlashni o‘rganadi;
- O‘zining portfoliosiga ega bo‘ladi.

😍 Farzandingizga yorqin kelajakni sovg‘a qiling, bunda biz sizga yordam beradi!

Kurslarimizga ro'yxatdan o‘tish uchun biz bilan bog’laning!

«Mars» — bu kelajak!""", reply_markup=application)
                        elif language == 'ru':
                            video = "BAACAgIAAxkBAAIj2WYguN4b7rToZY1zrMJW5JoohcAbAAKQSAACwrPwSLn2sm6Y3jLENAQ"
                            await dp.bot.send_video(chat_id=id, video=video, caption="""
😎 Хотите, чтобы ваш ребенок учился на ведущих ИТ курсах Ташкента?

🙌🏻 Тогда, добро пожаловать «Mars IT»!

Наша конечная цель: подготовить детей от 8 до 16 лет к будущему, обучая их современным навыкам работы с компьютером!

👨🏻‍💻 «Mars IT» уже 3 года обучает детей навыкам программирования и дизайна с помощью специальных образовательных методик.

В ходе курса ваш ребенок:
- Обучается в современной атмосфере;
- Учится работать в команде;
- У него будет свое портфолио.

😍 Подарите своему ребенку блестящее будущее, мы Вам поможем в этом!

Свяжитесь с нами, чтобы записаться на наши курсы!

«Mars» — это будущее!""", reply_markup=application_ru)

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
