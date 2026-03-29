from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.database import (
    set_user_role, 
    get_user_id_by_identifier, 
    add_group, 
    update_user_group, 
    get_groups, 
    get_all_users_detailed,
    delete_user,
    delete_group
)
from utils.config import settings

def get_admin_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Список пользователей", callback_data="adm_users_list")],
        [InlineKeyboardButton("📂 Управление группами", callback_data="adm_groups_list")],
        [InlineKeyboardButton("➕ Создать группу", callback_data="adm_add_group_prompt")],
        [InlineKeyboardButton("📢 Рассылка новостей", callback_data="adm_post_news")]
    ])

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != settings.admin_id: return
    await update.message.reply_text("👑 *Админ-панель*\nВыберите действие:", 
                                   reply_markup=get_admin_main_keyboard(), 
                                   parse_mode="Markdown")

async def _render_users_list(query):
    users = await get_all_users_detailed()
    text = "👥 *Все пользователи:*\n\n"
    keyboard = []
    for u in users:
        name = f"@{u['username']}" if u['username'] else f"ID: {u['tg_id']}"
        role_icon = "👑" if u['role'] == 'admin' else ("🎓" if u['role'] == 'starosta' else "👤")
        text += f"{role_icon} {name} | {u['group_name'] or '❌'}\n"
        keyboard.append([InlineKeyboardButton(f"⚙️ {name}", callback_data=f"adm_usr_edit_{u['tg_id']}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="adm_back")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def _render_groups_list(query):
    groups = await get_groups()
    text = "📂 *Управление группами:*\n\n"
    keyboard = []
    for g in groups:
        text += f"• {g['name']}\n"
        keyboard.append([InlineKeyboardButton(f"❌ Удалить {g['name']}", callback_data=f"adm_grp_del_{g['id']}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="adm_back")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != settings.admin_id: return
    data = query.data

    if data == "adm_users_list":
        await query.answer()
        await _render_users_list(query)

    elif data == "adm_groups_list":
        await query.answer()
        await _render_groups_list(query)

    elif data.startswith("adm_usr_edit_"):
        await query.answer()
        target_id = int(data.split("_")[3])
        # Меню управления конкретным юзером
        groups = await get_groups()
        keyboard = []
        for g in groups:
            keyboard.append([InlineKeyboardButton(f"В группу {g['name']}", callback_data=f"adm_usr_setgrp_{target_id}_{g['id']}")])
        
        keyboard.append([InlineKeyboardButton("🎓 Назначить старостой", callback_data=f"adm_usr_setrole_{target_id}_starosta")])
        keyboard.append([InlineKeyboardButton("👤 Сделать студентом", callback_data=f"adm_usr_setrole_{target_id}_student")])
        keyboard.append([InlineKeyboardButton("❌ Удалить из базы", callback_data=f"adm_del_{target_id}")])
        keyboard.append([InlineKeyboardButton("🔙 К списку", callback_data="adm_users_list")])
        
        await query.edit_message_text(f"⚙️ Управление пользователем ID: {target_id}:", 
                                     reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_usr_setgrp_"):
        parts = data.split("_")
        target_id, group_id = int(parts[3]), int(parts[4])
        await update_user_group(target_id, group_id)
        await query.answer("Группа изменена!")
        await _render_users_list(query)

    elif data.startswith("adm_usr_setrole_"):
        parts = data.split("_")
        target_id, role = int(parts[3]), parts[4]
        await set_user_role(target_id, role)
        await query.answer("Роль изменена!")
        await _render_users_list(query)

    elif data.startswith("adm_grp_del_"):
        group_id = int(data.split("_")[3])
        await delete_group(group_id)
        await query.answer("Группа удалена!")
        await _render_groups_list(query)

    elif data == "adm_add_group_prompt":
        await query.answer()
        await query.edit_message_text("Чтобы создать группу, напишите в чат:\n`/add_group <название>`", parse_mode="Markdown")

    elif data.startswith("adm_del_"):
        user_id = int(data.split("_")[2])
        if user_id != settings.admin_id:
            await delete_user(user_id)
            await query.answer("Пользователь удален!")
        await _render_users_list(query)

    elif data == "adm_back":
        await query.answer()
        await query.edit_message_text("👑 *Админ-панель*\nВыберите действие:", 
                                     reply_markup=get_admin_main_keyboard(), 
                                     parse_mode="Markdown")

# Оставляем консольные команды как запасной вариант
async def add_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != settings.admin_id: return
    if not context.args:
        await update.message.reply_text("Использование: /add_group <название>")
        return
    await add_group(context.args[0])
    await update.message.reply_text(f"✅ Группа {context.args[0]} создана!")

async def set_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != settings.admin_id: return
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /set_group @username_или_ID <название_группы>")
        return
    
    identifier = context.args[0]
    group_name = context.args[1]
    
    # Ищем пользователя
    user_id = await get_user_id_by_identifier(identifier)
    if not user_id:
        await update.message.reply_text(f"❌ Пользователь '{identifier}' не найден в базе.")
        return

    # Ищем группу
    groups = await get_groups()
    group_id = next((g['id'] for g in groups if g['name'] == group_name), None)
    
    if not group_id:
        await update.message.reply_text(f"❌ Группа {group_name} не найдена.")
        return

    await update_user_group(user_id, group_id)
    await update.message.reply_text(f"✅ Пользователь {identifier} добавлен в группу {group_name} как участник!")

async def set_starosta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != settings.admin_id: return
    if len(context.args) < 2: return
    identifier, group_name = context.args[0], context.args[1]
    user_id = await get_user_id_by_identifier(identifier)
    groups = await get_groups()
    group_id = next((g['id'] for g in groups if g['name'] == group_name), None)
    if user_id and group_id:
        await set_user_role(user_id, 'starosta')
        await update_user_group(user_id, group_id)
        await update.message.reply_text("✅ Готово!")
