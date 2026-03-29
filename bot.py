from telegram.ext import ApplicationBuilder
from utils.config import settings

if __name__ == "__main__":
    app = ApplicationBuilder().token(settings.bot_token).build()

    app.run_polling()