import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler, 
    filters,
    CallbackQueryHandler
)
from utils.database import get_user_role, get_user_group_info, get_all_user_ids, get_group_user_ids
from utils.config import settings

logger = logging.getLogger(__name__)

WAIT_NEWS_TEXT = 1

async def start_news_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for both Admin and Starosta via button callback."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    # Determine scope: 'all' for admin, 'group' for starosta
    scope = 'all' if data == "adm_post_news" else 'group'
    context.user_data['broadcast_scope'] = scope
    
    await query.edit_message_text(
        "📝 *Создание новости*\n\nНапишите текст вашей новости. Вы можете использовать Markdown форматирование. Бот разошлет это сообщение " + 
        ("всем пользователям." if scope == 'all' else "участникам вашей группы."),
        parse_mode="Markdown"
    )
    return WAIT_NEWS_TEXT

async def receive_news_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_text = update.message.text
    scope = context.user_data.get('broadcast_scope', 'group')
    user_id = update.effective_user.id
    
    # Validation
    if not news_text:
        await update.message.reply_text("Пожалуйста, введите текст новости.")
        return WAIT_NEWS_TEXT

    # Get target IDs
    if scope == 'all':
        if user_id != settings.admin_id:
            await update.message.reply_text("У вас нет прав для рассылки всем.")
            return ConversationHandler.END
        targets = await get_all_user_ids()
        prefix = "📢 *ОБЩЕЕ ОБЪЯВЛЕНИЕ*"
    else:
        group_info = await get_user_group_info(user_id)
        if not group_info:
            await update.message.reply_text("Ваша группа не найдена.")
            return ConversationHandler.END
        targets = await get_group_user_ids(group_info['id'])
        prefix = f"📣 *НОВОСТЬ ГРУППЫ {group_info['name']}*"

    full_message = f"{prefix}\n\n{news_text}"
    
    # Broadcast
    count = 0
    for target in targets:
        try:
            # Skip sender if you want, or include them
            await context.bot.send_message(chat_id=target, text=full_message, parse_mode="Markdown")
            count += 1
        except Exception as e:
            logger.error(f"Failed to send news to {target}: {e}")

    await update.message.reply_text(f"✅ Новость успешно отправлена {count} пользователям.")
    return ConversationHandler.END

async def cancel_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Создание новости отменено.")
    return ConversationHandler.END

news_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_news_broadcast, pattern="^(adm_post_news|st_post_news)$")
    ],
    states={
        WAIT_NEWS_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_news_text)]
    },
    fallbacks=[CommandHandler("cancel", cancel_news)],
    allow_reentry=True
)
