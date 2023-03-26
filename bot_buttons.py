from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup 
from defs import *

btn1 = KeyboardButton("Расписание уроков")
btn2 = KeyboardButton("Время до урока")
btn3 = KeyboardButton("Настройки")
btn4 = KeyboardButton("Информация")
mainboard = ReplyKeyboardMarkup(resize_keyboard = True, row_width=2).add(btn1,btn2,btn3,btn4)

d1 = InlineKeyboardButton("Понедельник", callback_data="day1")
d2 = KeyboardButton("Вторник", callback_data="day2")
d3 = KeyboardButton("Среда", callback_data="day3")
d4 = KeyboardButton("Четверг", callback_data="day4")
d5 = KeyboardButton("Пятница", callback_data="day5")
weekboard = InlineKeyboardMarkup(resize_keyboard = True).add(d1, d2, d3, d4, d5)