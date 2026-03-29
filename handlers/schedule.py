from telegram import Update
from telegram.ext import ContextTypes
from utils.scheduler import get_schedule_for_day
from utils.scheduler import get_current_and_next_lessons

async def get_today_schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_schedule_for_day()
    await update.message.reply_text(text, parse_mode="Markdown")

async def get_tomorrow_schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_schedule_for_day(is_tomorrow=True)
    await update.message.reply_text(text, parse_mode="Markdown")

async def get_current_lesson_handler(update, context):
    current, _ = get_current_and_next_lessons()
    text = f"🔔 *Сейчас идет:*\n\n{current}" if current else "☕️ Сейчас перерыв или пары уже закончились."
    await update.message.reply_text(text, parse_mode="Markdown")

async def get_next_lesson_handler(update, context):
    _, next_l = get_current_and_next_lessons()
    text = f"⏭ *Следующая пара:*\n\n{next_l}" if next_l else "😴 Больше пар сегодня не будет!"
    await update.message.reply_text(text, parse_mode="Markdown")