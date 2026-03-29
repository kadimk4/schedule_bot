from telegram import Update
from telegram.ext import ContextTypes

from utils.links import get_links


async def get_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_links()
    await update.message.reply_text(text)