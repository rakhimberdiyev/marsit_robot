import datetime
import random

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.utils.executor import start_webhook
from aiogram import Bot, Dispatcher, types

from keyboards.default.all_defaults import phone_uz
from keyboards.inline.all_inlines import start_test_ru, contact, application, start_test_uz, langs, application_ru, \
    contact_ru, filials_ru, filials
from keyboards.tests import test_ru, test_uz
from states.all_states import TestStateRu, RegStateRu, ApplicationState, TestState, RegState, ApplicationStateRu
from data.config import BOT_TOKEN, WEBHOOK_PATH, WEBHOOK_URI

from utils.notify_admins import on_startup_notify, on_shutdown_notify
from utils.set_bot_commands import set_default_commands

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URI)
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher, user=None)


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


@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegState.phone)
async def uz_phone_state(message: types.Message, state=FSMContext):
    phone = message.contact.phone_number

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
            {'age': age
            }
        )
        await save_message_id(state, message)

        data = await state.get_data()
        phone = data.get('phone')
        full_name = data.get('full_name')
        age = data.get('age')

        await state.reset_state(with_data=False)

        message_ids = data.get('message_ids', [])
        for message_id in message_ids:
            try:
                await dp.bot.delete_message(message.from_user.id, message_id)
            except Exception as e:
                print(f"Xabarni o'chirishda xato: {e}")
        await message.answer("Ro’yxatdan o’tganingiz uchun raxmat! 😊")
        await message.answer(f"Telefon raqam: {phone}\n\nIsm familiya: {full_name}\n\nYosh: {age}")

        await message.answer_photo(
            photo="AgACAgIAAxkBAAIIIGYFEeXP2H0XOmOusUutrf0DQptxAAI71TEbfGQpSBomsz22M-_jAQADAgADcwADNAQ",
            caption="Farzandingiz  qaysi yo’nalishda qobiliyati kuchli ekanligini bilishni xohlaysizmi?🤔\n\n",
            reply_markup=start_test_uz)


    except Exception as e:
        print(e)
        await message.answer("Itimos raqam kiriting:\n\nMisol uchun 14")


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
            photo="AgACAgIAAxkBAAIIImYFEpV7blhrRZg1PYGkjVMn-ajaAAI91TEbfGQpSCTfeMCLWVVBAQADAgADcwADNAQ",
            caption=results_message, reply_markup=application)


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

    user = f"Phone: {phone}\nFull name: {full_name}\nUsername: @{username}\nAge: {age}\nResult: {result}\nFilial: {filial}\nDate: {date}"

    await call.message.delete()
    await call.message.answer("Arizangiz qabul qilindi ✅ \n\nBiz tez orada sizga aloqaga chiqamiz📞",
                            reply_markup=contact)
    await state.finish()
    await on_startup_notify(dp, user)


@dp.callback_query_handler(text='contact')
async def contact_state_handler(call: types.CallbackQuery):
    await call.message.answer("""📞“Mars IT” aloqa raqami 78 777 77 57

💬 Biz bilan bog’lanish @mars_edu_admin

🌐 Telegram kanal: @mars_it_school""")


#######################################################################################################
# Russian
#######################################################################################################


async def save_message_id(state: FSMContext, message: types.Message):
    async with state.proxy() as data:
        if 'message_ids' not in data:
            data['message_ids'] = []
        data['message_ids'].append(message.message_id)


@dp.callback_query_handler(text='ru', state=None)
async def uz_state_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    reply = await call.message.answer("Для того чтобы начать, отправьте номер телефона 📱\n\n", reply_markup=phone_ru)
    await save_message_id(state, reply)
    await RegStateRu.phone.set()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegStateRu.phone)
async def uz_phone_state(message: types.Message, state=FSMContext):
    phone = message.contact.phone_number

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

        data = await state.update_data(
            {'age': age}
        )
        await save_message_id(state, message)

        data = await state.get_data()
        phone = data.get('phone')
        full_name = data.get('full_name')
        age = data.get('age')

        await state.reset_state(with_data=False)

        message_ids = data.get('message_ids', [])
        for message_id in message_ids:
            try:
                await dp.bot.delete_message(message.from_user.id, message_id)
            except Exception as e:
                print(f"Xabarni o'chirishda xato: {e}")
        await message.answer("Спасибо за регистрацию! 😊")
        await message.answer(f"Номер телефона: {phone}\n\nИмя и Фамилия: {full_name}\n\nВозраст: {age}")

        await message.answer_photo(
            photo="AgACAgIAAxkBAAIIIGYFEeXP2H0XOmOusUutrf0DQptxAAI71TEbfGQpSBomsz22M-_jAQADAgADcwADNAQ",
            caption="Хотите узнать в какой сфере IT у вашего ребенка есть предрасположенности?🤔\n\n",
            reply_markup=start_test_ru)


    except Exception as e:
        print(e)
        await message.answer("Пожалуйста отправьте возраст👨‍👩‍👦:\n\nПример 14")


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
        await state.reset_state(with_data=False)
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
            photo="AgACAgIAAxkBAAIIImYFEpV7blhrRZg1PYGkjVMn-ajaAAI91TEbfGQpSCTfeMCLWVVBAQADAgADcwADNAQ",
            caption=results_message, reply_markup=application_ru)


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

    user = f"Phone: {phone}\nFull name: {full_name}\nUsername: @{username}\nAge: {age}\nResult: {result}\nFilial: {filial}\nDate: {date}"

    await call.message.delete()
    await call.message.answer("Ваша заявка принята ✅ \n\nВ скором времени с вами свяжутся 📞", reply_markup=contact_ru)
    await state.finish()
    await on_startup_notify(dp, user)


@dp.callback_query_handler(text='contact_ru')
async def contact_state_handler(call: types.CallbackQuery):
    await call.message.answer("""📞Номер “Mars IT” 78 777 77 57

👩‍💻Чат с Администратором @mars_edu_admin

🌐Наш канал: @mars_it_school""")


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
