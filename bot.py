from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers.about import get_about
from utils.config import settings, messages
from handlers.start import start
from handlers.schedule import (
    get_current_lesson_handler, 
    get_next_lesson_handler, 
    get_today_schedule_handler, 
    get_tomorrow_schedule_handler,
    select_day_handler,
    day_selection_callback
)
from telegram.ext import CallbackQueryHandler

import logging
import asyncio
from utils.database import init_db

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application):
    await init_db()
    logger.info("База данных инициализирована и готова к работе.")

from handlers.admin import set_starosta, add_group_handler, admin_panel, admin_callback_handler, set_group_handler
from handlers.starosta import starosta_panel, starosta_callback_handler
from handlers.news import news_handler

if __name__ == '__main__':
    logger.info("Запуск бота...")
    application = ApplicationBuilder().token(settings.bot_token).post_init(post_init).build()
    
    # Регистрация диалога новостей должна быть ПЕРЕД обычными callback-хендлерами
    application.add_handler(news_handler)
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('set_starosta', set_starosta))
    application.add_handler(CommandHandler('add_group', add_group_handler))
    application.add_handler(CommandHandler('set_group', set_group_handler))
    application.add_handler(CommandHandler('starosta', starosta_panel))
    application.add_handler(CommandHandler('admin', admin_panel))
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(day_selection_callback, pattern="^day_"))
    application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^adm_"))
    application.add_handler(CallbackQueryHandler(starosta_callback_handler, pattern="^st_"))

    application.add_handler(MessageHandler(
        filters.Text(messages.schedule_today), get_today_schedule_handler
    ))
    application.add_handler(MessageHandler(
        filters.Text(messages.schedule_tomorrow), get_tomorrow_schedule_handler
    ))
    application.add_handler(MessageHandler(
        filters.Text(messages.choose_day), select_day_handler
    ))
    
    application.add_handler(MessageHandler(
        filters.Text(messages.other), get_about
    ))
    
    application.add_handler(MessageHandler(
        filters.Text(messages.current_lesson), get_current_lesson_handler
    ))
    application.add_handler(MessageHandler(
        filters.Text(messages.next_lesson), get_next_lesson_handler
    ))

    application.run_polling()