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

# ✅ Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load env vars
TOKEN = os.getenv('BOT_TOKEN')
GROUP_CHAT_ID = int(os.getenv('GROUP_CHAT_ID'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # E.g., https://yourapp.onrender.com


if not all([TOKEN, GROUP_CHAT_ID, WEBHOOK_URL]):
    raise ValueError("❌ Missing environment variables. Ensure BOT_TOKEN, GROUP_CHAT_ID, and WEBHOOK_URL are set.")

# ✅ Store scheduled events
scheduled_events = {}

# 🚀 Start command: shows WebApp button
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Open Reminder WebApp", web_app=WebAppInfo(url="https://www.uzeluz.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('👋 Welcome! Click below to set a reminder:', reply_markup=reply_markup)

# ✅ Handle WebApp data & schedule reminders
async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
        reminder_text = data.get('text')
        reminder_time = data.get('time')
        logger.info(f"📥 Data from WebApp: {data}")  # 🔍 Logs raw data

        # 🚨 Direct Test Message to Confirm Data Flow
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"🧪 **Test Message:** Received reminder: {reminder_text} at {reminder_time}"
        )

        # ⚡ Proceed with scheduling logic after testing
    except Exception as e:
        logger.error(f"🚨 Error processing WebApp data: {str(e)}")
        await update.message.reply_text("❌ Failed to set reminder. Please try again.")


        # ✅ Schedule reminder
        async def job_callback(job_context: ContextTypes.DEFAULT_TYPE):
            try:
                message = scheduled_events.get(event_id, {}).get('message', 'No message found.')
                await job_context.bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=f"🔔 **Scheduled Reminder:** {message}\n🕒 **Time:** {event_datetime_ny.strftime('%Y-%m-%d %I:%M:%S %p')} EST"
                )
                logger.info(f"✅ Reminder {event_id} sent successfully.")
            except Exception as e:
                logger.error(f"❌ Error sending reminder {event_id}: {str(e)}")

        job_queue = context.application.job_queue
        job = job_queue.run_once(job_callback, when=event_datetime_utc)

        scheduled_events[event_id] = {
            'job': job,
            'datetime': event_datetime_ny,
            'message': reminder_text
        }

        # 🔔 Confirmation message
        await update.message.reply_text(
            f"✅ **Reminder scheduled for:** {event_datetime_ny.strftime('%Y-%m-%d %I:%M:%S %p')} (EST)"
        )
        logger.info(f"🔔 Reminder scheduled with ID: {event_id}")

    except Exception as e:
        logger.error(f"🚨 Error processing WebApp data: {str(e)}")
        await update.message.reply_text("❌ Failed to set reminder. Please try again.")

# 🏗 Webhook initialization
async def post_init(application: Application):
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"✅ Webhook set at {WEBHOOK_URL}")

# 🚀 Main function
def main() -> None:
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # ✅ Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))

    # 🌐 Start webhook
    logger.info("🚀 Starting bot with webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 8080)),
        webhook_url=WEBHOOK_URL
    )

if __name__ == '__main__':
    main()
