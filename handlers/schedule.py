from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.scheduler import get_schedule_for_day, get_full_week_schedule
from utils.scheduler import get_current_and_next_lessons
from utils.database import get_user_group_info

async def get_user_group_name(user_id: int) -> str:
    group_info = await get_user_group_info(user_id)
    return group_info['name'] if group_info else None

async def get_today_schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = await get_user_group_name(update.effective_user.id)
    if not group_name:
        await update.message.reply_text("Вы не привязаны к группе. Обратитесь к старосте.")
        return
    text = get_schedule_for_day(group_name)
    await update.message.reply_text(text, parse_mode="Markdown")

async def get_tomorrow_schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = await get_user_group_name(update.effective_user.id)
    if not group_name:
        await update.message.reply_text("Вы не привязаны к группе. Обратитесь к старосте.")
        return
    text = get_schedule_for_day(group_name, is_tomorrow=True)
    await update.message.reply_text(text, parse_mode="Markdown")

async def get_current_lesson_handler(update, context):
    group_name = await get_user_group_name(update.effective_user.id)
    if not group_name:
        await update.message.reply_text("Вы не привязаны к группе.")
        return
    current, _ = get_current_and_next_lessons(group_name)
    text = f"🔔 *Сейчас идет ({group_name}):*\n\n{current}" if current else "☕️ Сейчас перерыв или пары уже закончились."
    await update.message.reply_text(text, parse_mode="Markdown")

async def get_next_lesson_handler(update, context):
    group_name = await get_user_group_name(update.effective_user.id)
    if not group_name:
        await update.message.reply_text("Вы не привязаны к группе.")
        return
    _, next_l = get_current_and_next_lessons(group_name)
    text = f"⏭ *Следующая пара ({group_name}):*\n\n{next_l}" if next_l else "😴 Больше пар сегодня не будет!"
    await update.message.reply_text(text, parse_mode="Markdown")

async def select_day_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = await get_user_group_name(update.effective_user.id)
    if not group_name:
        await update.message.reply_text("Сначала вступите в группу по ссылке от старосты.")
        return

    keyboard = [
        [
            InlineKeyboardButton("Пн", callback_data=f"day_Monday_{group_name}"),
            InlineKeyboardButton("Вт", callback_data=f"day_Tuesday_{group_name}"),
            InlineKeyboardButton("Ср", callback_data=f"day_Wednesday_{group_name}"),
        ],
        [
            InlineKeyboardButton("Чт", callback_data=f"day_Thursday_{group_name}"),
            InlineKeyboardButton("Пт", callback_data=f"day_Friday_{group_name}"),
            InlineKeyboardButton("Сб", callback_data=f"day_Saturday_{group_name}"),
        ],
        [
            InlineKeyboardButton("Вс", callback_data=f"day_Sunday_{group_name}"),
            InlineKeyboardButton("Вся неделя", callback_data=f"day_WholeWeek_{group_name}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Расписание для {group_name}. Выберите день:", reply_markup=reply_markup)

async def day_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Формат: day_Monday_05-507
    parts = query.data.split("_")
    action = parts[1]
    group_name = parts[2]

    if action == "WholeWeek":
        text = get_full_week_schedule(group_name)
    else:
        text = get_schedule_for_day(group_name, specific_day=action)

    await query.edit_message_text(text, parse_mode="Markdown")