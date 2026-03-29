from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.database import get_user_role, get_user_group_info, get_group_members, remove_user_from_group
from utils.config import settings

def get_starosta_main_keyboard(group_id: int):
    keyboard = [
        [InlineKeyboardButton("🔗 Ссылка для вступления", callback_data=f"st_invite_{group_id}")],
        [InlineKeyboardButton("👥 Список группы", callback_data=f"st_members_{group_id}")],
        [InlineKeyboardButton("📣 Рассылка в группу", callback_data="st_post_news")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def starosta_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    role = await get_user_role(user_id)
    if role != 'starosta' and user_id != settings.admin_id: return

    group_info = await get_user_group_info(user_id)
    if not group_info:
        await update.message.reply_text("❌ У вас не назначена группа.")
        return

    await update.message.reply_text(
        f"🎓 *Панель старосты группы {group_info['name']}*\nВыберите действие:",
        reply_markup=get_starosta_main_keyboard(group_info['id']),
        parse_mode="Markdown"
    )

async def _render_group_members(query, group_id: int):
    members = await get_group_members(group_id)
    text = "👥 *Студенты в вашей группе:*\n\n"
    keyboard = []
    for m in members:
        name = f"@{m['username']}" if m['username'] else f"ID: {m['tg_id']}"
        text += f"• {name}\n"
        if m['tg_id'] != settings.admin_id:
            keyboard.append([InlineKeyboardButton(f"❌ Исключить {name}", callback_data=f"st_rem_{m['tg_id']}_{group_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="st_back")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def starosta_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("st_invite_"):
        await query.answer()
        group_id = data.split("_")[2]
        bot_username = context.bot.username
        link = f"https://t.me/{bot_username}?start=reg_{group_id}"
        await query.edit_message_text(f"🔗 *Ссылка для вступления в группу:*\n\n`{link}`", 
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="st_back")]]),
                                     parse_mode="Markdown")

    elif data.startswith("st_members_"):
        await query.answer()
        group_id = int(data.split("_")[2])
        await _render_group_members(query, group_id)

    elif data.startswith("st_rem_"):
        user_id = int(data.split("_")[2])
        group_id = int(data.split("_")[3])
        await remove_user_from_group(user_id)
        await query.answer("Студент исключен!")
        await _render_group_members(query, group_id)

    elif data == "st_back":
        await query.answer()
        user_id = query.from_user.id
        group_info = await get_user_group_info(user_id)
        if group_info:
            await query.edit_message_text(f"🎓 *Панель старосты группы {group_info['name']}*\nВыберите действие:", 
                                         reply_markup=get_starosta_main_keyboard(group_info['id']), 
                                         parse_mode="Markdown")
