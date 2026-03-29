from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.config import messages
from utils.database import register_user, update_user_group, get_group_name_by_id

import logging
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await register_user(tg_id=user.id, username=user.username)
    logger.info(f"Зарегистрирован пользователь: {user.username} (ID: {user.id})")

    # Проверка на регистрационную ссылку (Deep Linking)
    if context.args and context.args[0].startswith("reg_"):
        try:
            group_id = int(context.args[0].split("_")[1])
            group_name = await get_group_name_by_id(group_id)
            if group_name:
                await update_user_group(user.id, group_id)
                await update.message.reply_text(f"✅ Вы успешно привязаны к группе: *{group_name}*", parse_mode="Markdown")
        except (ValueError, IndexError):
            pass

    keyboard = [
        [messages.current_lesson, messages.next_lesson],
        [messages.schedule_today, messages.schedule_tomorrow],
        [messages.choose_day, messages.other]
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