import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)
import datetime
import pytz
import uuid
import json

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load env vars
TOKEN = os.getenv(7994298291:AAELA0EndHVZT6k7lnbt7ujBvchJfuyxuuA)
GROUP_CHAT_ID = os.getenv('-1002413876809')
WEBHOOK_URL = os.getenv('https://telegram-bot-reminder-ga10.onrender.com')  # E.g., https://yourapp.onrender.com

scheduled_events = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Open Reminder WebApp", web_app=WebAppInfo(url="https://www.uzeluz.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('👋 Welcome! Click the button below to set a reminder:', reply_markup=reply_markup)


async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
        reminder_text = data.get('text')
        reminder_time = data.get('time')

        event_datetime = datetime.datetime.fromisoformat(reminder_time)
        ny_zone = pytz.timezone('America/New_York')
        event_datetime_ny = ny_zone.localize(event_datetime)
        event_datetime_utc = event_datetime_ny.astimezone(pytz.utc)

        event_id = str(uuid.uuid4())

        async def job_callback(job_context: ContextTypes.DEFAULT_TYPE):
            try:
                message = scheduled_events.get(event_id, {}).get('message', 'No message found.')
                await job_context.bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=f"🔔 **Scheduled Reminder:** {message}\n🕒 **Time:** {event_datetime_ny.strftime('%Y-%m-%d %I:%M:%S %p')} EST"
                )
            except Exception as e:
                logger.error(f"❌ Error sending reminder {event_id}: {str(e)}")

        job_queue = context.application.job_queue
        job = job_queue.run_once(job_callback, when=event_datetime_utc)

        scheduled_events[event_id] = {
            'job': job,
            'datetime': event_datetime_ny,
            'message': reminder_text
        }

        await update.message.reply_text(
            f"✅ **Reminder scheduled for:** {event_datetime_ny.strftime('%Y-%m-%d %I:%M:%S %p')} (EST)"
        )

    except Exception as e:
        logger.error(f"🚨 Error processing WebApp data: {str(e)}")
        await update.message.reply_text("❌ Failed to set reminder. Please try again.")


async def post_init(application: Application):
    await application.bot.set_webhook(url=WEBHOOK_URL)


def main() -> None:
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))

    logger.info("🤖 Starting bot with webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 8080)),
        webhook_url=WEBHOOK_URL
    )


if __name__ == '__main__':
    main()
