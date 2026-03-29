from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers.about import get_about
from utils.config import settings
from handlers.start import start
from handlers.schedule import get_today_schedule, get_tomorrow_schedule

if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.bot_token).build()
    
    application.add_handler(CommandHandler('start', start))
    
    application.add_handler(MessageHandler(
        filters.Text("📅 Расписание на сегодня"), get_today_schedule
    ))
    application.add_handler(MessageHandler(
        filters.Text("🗓 На завтра"), get_tomorrow_schedule
    ))

    application.add_handler(MessageHandler(
        filters.Text("О нас"), get_about
    ))
    
    print("schedule bot started")
    application.run_polling()