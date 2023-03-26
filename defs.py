import gspread 
import time
import datetime

from time import ctime
from google.oauth2 import service_account

gc = gspread.service_account('path')

def draw_table(values, weekday, user_class):

    times = ['08:15-08:55', '09:05-09:45', '09:55-10:35', '10:50-11:30', '11:40-12:20',
    '12:30-13:10', '13:20-14:00', '14:10-14:50', '14:55-15:35', '15:40-16:20']
    if len(values) < len(times):
        values += [''] * (len(times) - len(values))
    else:
        times += [''] * (len(values) - len(times))

    rows = list(zip(times, values))

    column_widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]

    table = f"Расписание на {weekday} для {user_class}" + "\n"
    table += "-" * column_widths[0] + "-" * column_widths[1] + "\n"

    for row in rows:
        table += str(row[0]).ljust(column_widths[0]) + " | " + str(row[1]).ljust(column_widths[1]) + "\n"

    table += "-" * column_widths[0] + "-" * column_widths[1] + "\n"
    return table 

def draw_lessons_table(weekday, user_class):

    spreadsheet = gc.open_by_key('key')

    worksheet = spreadsheet.worksheet(user_class)

    cell = worksheet.find(f"{weekday}")
    column_index = cell.col
    row_number = cell.row

    column = worksheet.col_values(column_index)
    values = column[row_number:]

    table = draw_table(values, weekday, user_class)

    return table

def find_user_class(user_id):
    spreadsheet = gc.open_by_key('key')
    worksheet = spreadsheet.get_worksheet(0)
    cell = worksheet.find(str(user_id))
    user_class = worksheet.cell(cell.row, 2).value

    if cell is None:
        return None
    else:
        return user_class

def time_until_next():
    lessons = [
        ((8 * 60 + 15) * 60),
        ((9 * 60 + 5) * 60),
        ((9 * 60 + 55) * 60),
        ((10 * 60 + 50) * 60),
        ((11 * 60 + 40) * 60),
        ((12 * 60 + 30) * 60),
        ((13 * 60 + 20) * 60),
        ((14 * 60 + 10) * 60),
        ((14 * 60 + 55) * 60),
        ((15 * 60 + 40) * 60)
    ]

    current_time = ctime()
    current_time_all_seconds = time.strptime(current_time).tm_hour * 3600 + time.strptime(current_time).tm_min * 60 + time.strptime(current_time).tm_sec

    for index, lesson in enumerate(lessons):
        if current_time_all_seconds < lesson:
            time_difference = lesson - current_time_all_seconds
            time_until_next = f'{time_difference // 3600} часов, {(time_difference % 3600) // 60} минут, {time_difference % 60} секунд'
            break
        elif index == len(lessons) - 1:
            time_until_next = 'хз'

    if current_time.startswith(('Sat', 'Sun')):
        time_until_next = 'Сегодня выходной, отдыхай:)'

    return time_until_next

def today():
    today = datetime.datetime.today()
    weekday = today.strftime("%A")
    if weekday == "Saturday" or weekday == "Sunday":
        weekday = "Monday"
    else:
        if today.hour >= 17:
            weekday = datetime.datetime.strptime(weekday, '%A') + datetime.timedelta(days=1)
            weekday = weekday.strftime('%A')

    return weekday

def class_exists(classid):
    print(classid)
    try:
        spreadsheet = gc.open_by_key('key')
        worksheet = spreadsheet.worksheet(classid)
        return True
    except:
        return False



