from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers.about import get_about
from utils.config import settings, messages
from handlers.start import start
from handlers.schedule import get_current_lesson_handler, get_next_lesson_handler, get_today_schedule_handler, get_tomorrow_schedule_handler

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.bot_token).build()
    
    application.add_handler(CommandHandler('start', start))
    
    application.add_handler(MessageHandler(
        filters.Text(messages.schedule_today), get_today_schedule_handler
    ))
    application.add_handler(MessageHandler(
        filters.Text(messages.schedule_tomorrow), get_tomorrow_schedule_handler
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
    
    print("schedule bot started")
    application.run_polling()