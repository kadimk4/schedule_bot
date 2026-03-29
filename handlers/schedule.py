from telegram import Update
from telegram.ext import ContextTypes
from utils.scheduler import get_schedule_for_day

async def get_today_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_schedule_for_day()
    await update.message.reply_text(text)

async def get_tomorrow_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_schedule_for_day(is_tomorrow=True)
    await update.message.reply_text(text)

