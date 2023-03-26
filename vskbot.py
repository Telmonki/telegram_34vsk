import logging 
import datetime
import gspread

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage 
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters. state import State, StatesGroup 
from aiogram.utils import executor
from google.oauth2 import service_account
from defs import *
from bot_buttons import *

logging.basicConfig(level=logging.INFO)
TOKEN = 'token'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
gc = gspread.service_account('path')

class Form (StatesGroup):
    userclass = State()

@dp.message_handler(commands= ['start'])
async def send_welcome (message: types.Message):

    # ...

    spreadsheet = gc.open_by_key('key')
    worksheet = spreadsheet.get_worksheet(0)
    cell = worksheet.find(str(message.from_user.id))

    if cell is None:
        await Form.userclass.set()
        await bot.send_message(message.from_user.id,
            text=f"Привет, напиши свой класс в формате '10а', '12b' и тд. (Латинские буквы)")
    else:
        if cell.row is not None and cell.col is not None:
            await bot.send_message(message.from_user.id,
                text=f"Добро пожаловать, {message.from_user.full_name}! Как тебе помочь?", reply_markup=mainboard)
        else:
            await bot.send_message(message.from_user.id,
                text=f"Добро пожаловать, {message.from_user.full_name}! Как тебе помочь?", reply_markup=mainboard)

@dp.message_handler()
async def process_class_step (message: types.Message):

    # ...

    if message.text == "Расписание уроков":

        await bot.send_message(
            message.from_user.id,
            text = "Ищу расписание, подожди немного..."
        )

        today = datetime.datetime.today()
        weekday = today.strftime("%A")
        if weekday == "Saturday" or weekday == "Sunday":
            weekday = "Monday"
        else:
            if today.hour >= 17:
                weekday = datetime.datetime.strptime(weekday, '%A') + datetime.timedelta(days=1)
                weekday = weekday.strftime('%A')

        user_class = find_user_class(message.from_user.id)

        try:
            table = draw_lessons_table(weekday, user_class)
        #-----#
            await bot.delete_message(
                chat_id = message.chat.id,
                message_id = message.message_id + 1
            )
            
            await bot.send_message(
                message.from_user.id,
                text = table,
                reply_markup = weekboard
            )

            await bot.send_message(
                message.from_user.id,
                text = "Ишу изменения, подожди немного..."
            )

            #---ИЗМЕНЕНИЯ--#

            spreadsheet = gc.open_by_key('key')
            worksheet = spreadsheet.get_worksheet(0)

            cells = worksheet.findall(user_class.upper())

            cells.sort(key=lambda c: (c.row, c.col))
            try:
                lowest_cell = cells[0]

                column_index = lowest_cell.col
                row_number = lowest_cell.row

                column = worksheet.col_values(column_index)

                # Combine the times and subjects into a dictionary
                times = ['08:15-08:55', '09:05-09:45', '09:55-10:35', '10:50-11:30', '11:40-12:20',
                        '12:30-13:10', '13:20-14:00', '14:10-14:50', '14:55-15:35', '15:40-16:20']
                values = column[row_number:]
                data = {'times': times, 'subjects': values}

                # Pad the values with empty strings if necessary
                if len(values) < len(times):
                    values += [''] * (len(times) - len(values))
                else:
                    times += [''] * (len(values) - len(times))

                # Combine the times and values into rows
                rows = list(zip(times, values))

                # Format the table
                column_widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
                table = f"Изменения на {weekday} для {user_class}\n"
                table += "-" * column_widths[0] + " | " + "-" * column_widths[1] + "\n"
                for row in rows:
                    table += str(row[0]).ljust(column_widths[0]) + " | " + str(row[1]).ljust(column_widths[1]) + "\n"
                table += "-" * column_widths[0] + " | " + "-" * column_widths[1] + "\n"

                await bot.delete_message(
                    chat_id = message.chat.id,
                    message_id = message.message_id + 3
                )
                # Send the table to the user
                await bot.send_message(
                    message.from_user.id,
                    text=table
                )

                # Code for searching and processing schedule changes

            except IndexError:
                await bot.delete_message(
                    chat_id = message.chat.id,
                    message_id = message.message_id + 3
                )
                await bot.send_message(
                    message.from_user.id,
                    text="Изменений для твоего класса на завтра нет"
                )



        except: 
            await bot.send_message(
                message.from_user.id,
                text=f"Не нашел твое расписание. Скорее всего твой класс ({find_user_class(message.from_user.id)}) указан неправильно или мы пока его не добавили. Измени свой класс в настройках бота."
            )

    if message.text == "Настройки":

    
        await Form.userclass.set()
        await bot.send_message(
            message.from_user.id,
            text = "Напиши свой класс в формате '10а', '12b' и тд. (Латинские буквы)"
        )
    if message.text == "Время до урока":

        await bot.send_message(
            message.from_user.id,
            text = time_until_next()
        )
    if message.text == "Информация":
        await bot.send_message(
            message.from_user.id,
            text = "Бот создан учениками Рижской 34 средней школы\nГеоргием Воробьевом @vorobjovs, Артемом Маркушевским @Markushvili, Закаром Татевосьяном @zackburgers\n\nЕсли заметил какую-то ошибку или хочешь предложить новую функцию - пиши любому из нас"
        )

@dp.message_handler(state=Form.userclass)
async def process_name(message: types.Message, state:FSMContext):
    
    spreadsheet = gc.open_by_key('key')
    worksheet = spreadsheet.get_worksheet(0)
    cell = worksheet.find(str(message.from_user.id))

    if class_exists(message.text) == True:
        if not cell:
            worksheet.append_row([message.from_user.id, message.text])
            await bot.send_message(
                message.from_user.id,
                text='Сохранено',
                reply_markup=mainboard)
        else:
            worksheet.update_cell(cell.row, 2, message.text)
            await bot.send_message(
                message.from_user.id,
                text='Обновлено',
                reply_markup=mainboard)
        await state.finish()   

    else:
        await bot.send_message(
            message.from_user.id,
            text='Неправильно ввёл класс, попробуй еще раз. В данный момент поддерживаем все классы с 5 по 12',
            reply_markup=mainboard)
        await state.finish()   

@dp.callback_query_handler()
async def generate_text(call: types.CallbackQuery):


    # ...

    user_class = find_user_class(call.from_user.id)

    if call.data == "day1":
        await bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        await bot.send_message(
            call.from_user.id,
            text=draw_lessons_table("Monday", user_class),
            reply_markup=weekboard
        )

    if call.data == "day2":
        await bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        await bot.send_message(
            call.from_user.id,
            text=draw_lessons_table("Tuesday", user_class),
            reply_markup=weekboard
        )

    if call.data == "day3":
        await bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        await bot.send_message(
            call.from_user.id,
            text=draw_lessons_table("Wednesday", user_class),
            reply_markup=weekboard
        )

    if call.data == "day4":
        await bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        await bot.send_message(
            call.from_user.id,
            text=draw_lessons_table("Thursday", user_class),
            reply_markup=weekboard
        )

    if call.data == "day5":
        await bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        await bot.send_message(
            call.from_user.id,
            text=draw_lessons_table("Friday", user_class),
            reply_markup=weekboard
        )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)