import datetime
import random
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.utils.executor import start_webhook
from aiogram import Bot, Dispatcher, types

from keyboards.default.all_defaults import phone_uz, phone_ru
from keyboards.inline.all_inlines import start_test_ru, contact, application, start_test_uz, langs, application_ru, \
    contact_ru, filials_ru, filials, area_uz, area_ru
from keyboards.tests import test_ru, test_uz
from states.all_states import TestStateRu, RegStateRu, ApplicationState, TestState, RegState, ApplicationStateRu, \
    UserState
from data.config import BOT_TOKEN, WEBHOOK_PATH, WEBHOOK_URI, ADMINS

from utils.notify_admins import on_startup_notify, on_shutdown_notify
from utils.set_bot_commands import set_default_commands

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URI)
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher, user=None, id=123456, address=None, language=None)


async def on_shutdown(_):
    await on_shutdown_notify(bot)

    
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(
        f"Assalamu alaykum, {message.from_user.full_name}!\n\nMARS ITSchoolning sales botiga xush kelibsiz!\nTillardan birini tanlang\n\nДобро пожаловать в sales bot от Mars IT School!\nВыберите один из языков:",
        reply_markup=langs)


@dp.message_handler(CommandStart(), state="*")  # Har qanday state'da ishlaydi
async def bot_restart(message: types.Message, state: FSMContext):
    await state.finish()  # Joriy state'dagi barcha ma'lumotlarni tozalash
    await message.answer("Bot qayta ishga tushirildi.")
    await bot_start(message)


async def save_message_id(state: FSMContext, message: types.Message):
    async with state.proxy() as data:
        if 'message_ids' not in data:
            data['message_ids'] = []
        data['message_ids'].append(message.message_id)


@dp.callback_query_handler(text='uz', state=None)
async def uz_state_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    reply = await call.message.answer("Testni boshlash uchun iltimos, telefon raqamingizni kiriting📱\n\n",
                                    reply_markup=phone_uz)
    await save_message_id(state, reply)
    await RegState.phone.set()


@dp.message_handler(content_types=['contact', 'text'], state=RegState.phone)
async def uz_phone_state(message: types.Message, state=FSMContext):
    if message.content_type == 'contact':
        phone = message.contact.phone_number
    elif message.content_type == 'text':
        phone = message.text
    await state.update_data(
        {'phone': phone}
    )
    reply = await message.answer("Farzandingizning ism-familiyasi👨‍👨‍👧 \n\n", reply_markup=ReplyKeyboardRemove())
    await save_message_id(state, reply)
    await save_message_id(state, message)
    await RegState.next()


@dp.message_handler(state=RegState.fullname)
async def us_fullname_state(message: types.Message, state=FSMContext):
    fullname = message.text

    await state.update_data(
        {'full_name': fullname}
    )
    reply = await message.answer("Farzandingizning yoshi👫 \n\nMisol uchun 14\n")
    await save_message_id(state, reply)
    await save_message_id(state, message)
    await RegState.age.set()


@dp.message_handler(state=RegState.age)
async def us_fullname_state(message: types.Message, state=FSMContext):
    try:
        age = int(message.text)

        await state.update_data(
            {'age': age,
            'username': message.from_user.username,
            }
        )
        await save_message_id(state, message)
        reply = await message.answer("Qaysi hududda yashaysiz?", reply_markup=area_uz)
        await save_message_id(state, reply)
        await save_message_id(state, message)
        await RegState.address.set()
        
    except Exception as e:
        print(e)
        reply = await message.answer("Itimos raqam kiriting:\n\nMisol uchun 14")
        await save_message_id(state, reply)
        await save_message_id(state, message)

    


@dp.callback_query_handler(state=RegState.address)
async def us_fullname_state(call: types.CallbackQuery, state=FSMContext):
        address = call.data

        await state.update_data(
            {'address': address}
        )
        await save_message_id(state, call.message)

        data = await state.get_data()
        phone = data.get('phone')
        full_name = data.get('full_name')
        age = data.get('age')

        await state.reset_state(with_data=False)

        message_ids = data.get('message_ids', [])
        for message_id in message_ids:
            try:
                await dp.bot.delete_message(call.from_user.id, message_id)
            except Exception as e:
                print(f"Xabarni o'chirishda xato: {e}")

        await call.message.answer("Ro’yxatdan o’tganingiz uchun raxmat! 😊")
        await call.message.answer(f"Telefon raqam: {phone}\n\nIsm familiya: {full_name}\n\nYosh: {age}")

        await call.message.answer_photo(
            # photo="AgACAgIAAxkBAAIBaGYL81IeEHYod-0trHvlY0eeeV9JAAJF2zEbwp1gSF2lTOActrf1AQADAgADcwADNAQ",
            photo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT873pgw_FPhwhcCT2p11KJgy8DM0hVEtxDXZ-fqMAnOA&s",
            caption="Farzandingiz  qaysi yo’nalishda qobiliyati kuchli ekanligini bilishni xohlaysizmi?🤔\n\n",
            reply_markup=start_test_uz)


    

@dp.callback_query_handler(text='start_test_uz', state=None)
async def start_test_uz_handler(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(TestState.waiting_for_answer)
    await state.update_data(current_question_index=0, answers=[])
    await call.message.delete()
    await send_question(call.message, state, answers=None, id=call.from_user.id)


async def send_question(message: types.Message, state: FSMContext, answers: list, id):
    user_data = await state.get_data()
    current_question_index = user_data.get("current_question_index", 0)
    questions = list(test_uz.keys())

    if current_question_index < len(questions):
        question = questions[current_question_index]
        options = test_uz[question]

        markup = InlineKeyboardMarkup()
        for option, value in options.items():
            callback_data = f"answer_{current_question_index}_{value}"
            markup.add(InlineKeyboardButton(option, callback_data=callback_data))

        await message.answer(f"{current_question_index + 1}-savol \n\n{question}\n\n", reply_markup=markup)
    else:
        await state.reset_state(with_data=False)

        categories = {'Dizayn': 0, 'Frontend': 0, 'Backend': 0, 'Fullstack': 0}
        for answer in answers:
            for value in answer.values():
                if value in categories:
                    categories[value] += 1

        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        results_message = """Siz testni muvaffaqiyatli yakunladingiz🥳

Natijalaringiz asosida quyidagi kurslar siz uchun eng mos keladi:\n\n"""
        result = ""
        a = 95
        b = 100
        for category, count in sorted_categories:
            result += f"{category}:{count}ta,"

        await state.update_data(
            {'result': result}
        )

        for category, count in sorted_categories:
            if category == "Backend":
                results_message += f"⚙️ {category} dasturchi - {random.randint(a, b)}%\n\n"
            elif category == "Frontend":
                results_message += f"💻 {category} dasturchi - {random.randint(a, b)}%\n\n"
            elif category == "Fullstack":
                results_message += f"😎 {category} dasturchi  (backend + Frontend) - {random.randint(a, b)}%\n\n"
            elif category == "Dizayn":
                results_message += f"🧑‍🎨Grafik dizayner - {random.randint(a, b)}%\n\n"

            a -= 5
            b -= 5

        # Natijalarni foydalanuvchiga yuborish
        await message.answer_photo(
            # photo="AgACAgIAAxkBAAIBamYL8-MkkRjuMJjOYn1GqWd141TfAAJG2zEbwp1gSIVdQ1pU3z7sAQADAgADcwADNAQ",
            # photo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT873pgw_FPhwhcCT2p11KJgy8DM0hVEtxDXZ-fqMAnOA&s",
            photo = "AgACAgIAAxkBAAIj1WYguB910TqKb-RJJlEHvojqLumgAAKa2DEbwigJSYFqDT2-has0AQADAgADcwADNAQ",
            caption=results_message)

        user_data = await state.get_data()
        phone = user_data.get('phone')
        full_name = user_data.get('full_name')
        age = user_data.get('age')
        result = user_data.get('result')
        username = user_data.get('username')
        date = datetime.datetime.now()
        address = user_data.get('address')


        user = f"Phone: {phone}\nFull name: {full_name}\nUsername: @{username}\nAge: {age}\nResult: {result}\nDate: {date}\nHudud: {address}\nTil: uz\n\nSinov darsiga yozilmadi"

        await on_startup_notify(dp, user, id, address, language='uz')
        
        
@dp.callback_query_handler(text_contains='answer_', state=TestState.waiting_for_answer)
async def handle_answer(call: types.CallbackQuery, state: FSMContext):
    answer_data = call.data.split('_')
    question_index = int(answer_data[1])
    answer_value = answer_data[2]

    user_data = await state.get_data()
    answers = user_data.get("answers", [])
    answers.append({question_index: answer_value})

    await state.update_data(answers=answers, current_question_index=question_index + 1)

    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass

    await send_question(call.message, state, answers, id=call.from_user.id)

    # print(answers[-1])





@dp.callback_query_handler(text='application', state=None)
async def application_handler(call: types.CallbackQuery, state=None):
    await call.message.answer("Sizga qulay bo’lgan filialni tanlang📍", reply_markup=filials)
    await state.set_state(ApplicationState.filial)


@dp.callback_query_handler(text=['yunusobod', 'tinchlik', 'chilonzor', 'sergeli'], state=ApplicationState.filial)
async def application_handler(call: types.CallbackQuery, state: FSMContext):
    filial = call.data
    user_data = await state.get_data()
    phone = user_data.get('phone')
    full_name = user_data.get('full_name')
    age = user_data.get('age')
    result = user_data.get('result')
    username = call.from_user.username
    date = datetime.datetime.now()
    address = user_data.get('address')

    user = f"Phone: {phone}\nFull name: {full_name}\nUsername: @{username}\nAge: {age}\nResult: {result}\nFilial: {filial}\nDate: {date}\nHudud: {address}\nTil: uz"

    await call.message.delete()
    await call.message.answer("Arizangiz qabul qilindi ✅ \n\nBiz tez orada sizga aloqaga chiqamiz📞",
                            reply_markup=contact)
    await state.finish()
    await on_startup_notify(dp, user, call.from_user.id, address, language=None)


@dp.callback_query_handler(text='contact')
async def contact_state_handler(call: types.CallbackQuery):
    await call.message.answer("""📞“Mars IT” aloqa raqami 78 777 77 57

💬 Biz bilan bog’lanish @mars_edu_admin

🌐 Telegram kanal: @mars_it_school""")


#######################################################################################################
# Russian
#######################################################################################################


# async def save_message_id(state: FSMContext, message: types.Message):
#     async with state.proxy() as data:
#         if 'message_ids' not in data:
#             data['message_ids'] = []
#         data['message_ids'].append(message.message_id)


@dp.callback_query_handler(text='ru', state=None)
async def uz_state_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    reply = await call.message.answer("Для того чтобы начать, отправьте номер телефона 📱\n\n", reply_markup=phone_ru)
    await save_message_id(state, reply)
    await RegStateRu.phone.set()


@dp.message_handler(content_types=['contact', 'text'], state=RegStateRu.phone)
async def ru_phone_state(message: types.Message, state=FSMContext):
    if message.content_type == 'contact':
        phone = message.contact.phone_number
    elif message.content_type == 'text':
        phone = message.text

    await state.update_data(
        {'phone': phone}
    )
    reply = await message.answer("Имя и Фамилия ребенка 👨‍👨‍👧 \n\n", reply_markup=ReplyKeyboardRemove())
    await save_message_id(state, reply)
    await save_message_id(state, message)
    await RegStateRu.next()


@dp.message_handler(state=RegStateRu.fullname)
async def us_fullname_state(message: types.Message, state=FSMContext):
    fullname = message.text

    await state.update_data(
        {'full_name': fullname}
    )
    reply = await message.answer("Возраст вашего ребенка👫 \n\nПример 14\n")
    await save_message_id(state, reply)
    await save_message_id(state, message)
    await RegStateRu.age.set()


@dp.message_handler(state=RegStateRu.age)
async def us_fullname_state(message: types.Message, state=FSMContext):
    try:
        age = int(message.text)

        await state.update_data(
            {'age': age,
            'username': message.from_user.username,
            }
        )
        await save_message_id(state, message)
        reply = await message.answer("В каком районе вы живете?", reply_markup=area_ru)
        await save_message_id(state, reply)
        await save_message_id(state, message)
        await RegStateRu.address.set()
        
    except Exception as e:
        print(e)
        reply = await message.answer("Пожалуйста отправьте возраст👨‍👩‍👦:\n\nПример 14")
        await save_message_id(state, reply)
        await save_message_id(state, message)


@dp.callback_query_handler(state=RegStateRu.address)
async def us_fullname_state(call: types.CallbackQuery, state=FSMContext):
        address = call.data
        await state.update_data(
            {'address': address}
        )
        await save_message_id(state, call.message)

        data = await state.get_data()
        phone = data.get('phone')
        full_name = data.get('full_name')
        age = data.get('age')

        await state.reset_state(with_data=False)

        message_ids = data.get('message_ids', [])
        for message_id in message_ids:
            try:
                await dp.bot.delete_message(call.from_user.id, message_id)
            except Exception as e:
                print(f"Xabarni o'chirishda xato: {e}")

        await call.message.answer("Спасибо за регистрацию! 😊")
        await call.message.answer(f"Номер телефона: {phone}\n\nИмя и Фамилия: {full_name}\n\nВозраст: {age}\n\n")

        await call.message.answer_photo(
            photo="AgACAgIAAxkBAAIBaGYL81IeEHYod-0trHvlY0eeeV9JAAJF2zEbwp1gSF2lTOActrf1AQADAgADcwADNAQ",
            # photo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT873pgw_FPhwhcCT2p11KJgy8DM0hVEtxDXZ-fqMAnOA&s",
            caption="Хотите узнать в какой сфере IT у вашего ребенка есть предрасположенности?🤔\n\n",
            reply_markup=start_test_ru)

    
    
@dp.callback_query_handler(text='start_test_ru', state=None)
async def start_test_ru_handler(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(TestStateRu.waiting_for_answer)
    await state.update_data(current_question_index=0, answers=[])
    await call.message.delete()
    await send_question_ru(call.message, state, answers=None, id=call.from_user.id)


async def send_question_ru(message: types.Message, state: FSMContext, answers: list, id):
    user_data = await state.get_data()
    current_question_index = user_data.get("current_question_index", 0)
    questions = list(test_ru.keys())

    if current_question_index < len(questions):
        question = questions[current_question_index]
        options = test_ru[question]

        markup_ru = InlineKeyboardMarkup()
        for option, value in options.items():
            callback_data = f"answer_{current_question_index}_{value}"
            markup_ru.add(InlineKeyboardButton(option, callback_data=callback_data))

        await message.answer(f"Вопрос {current_question_index + 1} \n\n{question}\n\n", reply_markup=markup_ru)
    else:
        categories = {'Dizayn': 0, 'Frontend': 0, 'Backend': 0, 'Fullstack': 0}
        for answer in answers:
            for value in answer.values():
                if value in categories:
                    categories[value] += 1

        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        results_message = """Вы успешно прошли тест🥳

По вашим результатам вашему ребенку больше всего подойдут курсы:\n\n"""
        result = ""
        a = 95
        b = 100
        for category, count in sorted_categories:
            result += f"{category}:{count}ta,"

        await state.update_data(
            {'result': result}
        )

        for category, count in sorted_categories:
            if category == "Backend":
                results_message += f"⚙️ Разработчик {category} - {random.randint(a, b)}%\n\n"
            elif category == "Frontend":
                results_message += f"💻 Разработчик {category} - {random.randint(a, b)}%\n\n"
            elif category == "Fullstack":
                results_message += f"😎 Разработчик {category}  (backend + Frontend) - {random.randint(a, b)}%\n\n"
            elif category == "Dizayn":
                results_message += f"🧑‍🎨Графический дизайн - {random.randint(a, b)}%\n\n"

            a -= 5
            b -= 5

        # Natijalarni foydalanuvchiga yuborish
        await message.answer_photo(
            # photo="AgACAgIAAxkBAAIBamYL8-MkkRjuMJjOYn1GqWd141TfAAJG2zEbwp1gSIVdQ1pU3z7sAQADAgADcwADNAQ",
            # photo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT873pgw_FPhwhcCT2p11KJgy8DM0hVEtxDXZ-fqMAnOA&s",
            photo="AgACAgIAAxkBAAIj1WYguB910TqKb-RJJlEHvojqLumgAAKa2DEbwigJSYFqDT2-has0AQADAgADcwADNAQ",
            caption=results_message)

        user_data = await state.get_data()
        phone = user_data.get('phone')
        full_name = user_data.get('full_name')
        age = user_data.get('age')
        result = user_data.get('result')
        username = user_data.get('username')
        date = datetime.datetime.now()
        address = user_data.get('address')

        await state.reset_state(with_data=False)

        user = f"Phone: {phone}\nFull name: {full_name}\nUsername: @{username}\nAge: {age}\nResult: {result}\nDate: {date}\nHudud: {address}\nTil: ru\n\nSinov darsiga yozilmadi"

        await on_startup_notify(dp, user, id, address, language='ru')
        
        
@dp.callback_query_handler(text_contains='answer_', state=TestStateRu.waiting_for_answer)
async def handle_answer(call: types.CallbackQuery, state: FSMContext):
    answer_data = call.data.split('_')
    question_index = int(answer_data[1])
    answer_value = answer_data[2]

    user_data = await state.get_data()
    answers = user_data.get("answers", [])
    answers.append({question_index: answer_value})

    await state.update_data(answers=answers, current_question_index=question_index + 1)

    # await asyncio.sleep(1)  # 1 soniya kutish
    try:
        await call.message.delete()
    except MessageToDeleteNotFound:
        pass

    await send_question_ru(call.message, state, answers, id=call.from_user.id)


@dp.callback_query_handler(text='application_ru')
async def application_handler(call: types.CallbackQuery, state=None):
    # await call.message.delete()
    await call.message.answer("Выберите удобный для вас филиал📍", reply_markup=filials_ru)
    await ApplicationStateRu.filial.set()


@dp.callback_query_handler(text=['yunusobod', 'tinchlik', 'chilonzor', 'sergeli'], state=ApplicationStateRu.filial)
async def application_handler(call: types.CallbackQuery, state: FSMContext):
    filial = call.data
    user_data = await state.get_data()
    phone = user_data.get('phone')
    full_name = user_data.get('full_name')
    age = user_data.get('age')
    result = user_data.get('result')
    username = call.from_user.username
    date = datetime.datetime.now()
    address = user_data.get('address')

    user = f"Phone: {phone}\nFull name: {full_name}\nUsername: @{username}\nAge: {age}\nResult: {result}\nFilial: {filial}\nDate: {date}\nHudud: {address}\nTil: uz"

    await call.message.delete()
    await call.message.answer("Ваша заявка принята ✅ \n\nВ скором времени с вами свяжутся 📞", reply_markup=contact_ru)
    await state.finish()
    await on_startup_notify(dp, user, call.from_user.id, address, language=None)


@dp.callback_query_handler(text='contact_ru')
async def contact_state_handler(call: types.CallbackQuery):
    await call.message.answer("""📞Номер “Mars IT” 78 777 77 57

👩‍💻Чат с Администратором @mars_edu_admin

🌐Наш канал: @mars_it_school""")
    
    
# @dp.message_handler(content_types=['video', 'photo'])
# async def send_file_id(message: types.Message):
#     print(message)
#     if message.content_type == 'video':
#         await message.answer_video(video=message.video.file_id)
#     elif message.content_type == 'photo':
#         await message.answer_photo(photo=message.photo[0]['file_id'])


if __name__ == "__main__":
    print("Ishga tushdi")

    # executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host='0.0.0.0',
        port=8080
    )
