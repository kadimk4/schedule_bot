from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📅 Расписание на сегодня", "🗓 На завтра"],
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True,
        one_time_keyboard=False 
    )
    
    await update.message.reply_text(
        "Привет! Я бот группы 05-507. Выбери нужное действие в меню ниже:",
        reply_markup=reply_markup
    )