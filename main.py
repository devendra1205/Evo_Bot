from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os
from dotenv import load_dotenv

from bot.bot import get_response
from utils.chats import load_data, save_data

load_dotenv()  # Load .env file

TOKEN = os.getenv("BOT_TOKEN")  # Load from .env
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", "10000"))

# Load JSON once
data = load_data()
save_data(data)

# In-memory user memory storage (NOT persisted to keep lean)
user_memories = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your bot 🤖, How can I help you?")


async def help(update, context):
    await update.message.reply_text("Available commands:\n/start\n/help\n/game")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I don't recognize that command.")


# 👇 THIS handles normal messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    user_id = str(update.effective_chat.id)

    # Get user's history and memory
    history = data.get(user_id, [])
    user_memory = user_memories.get(user_id, {})

    # Get AI response (returns updated memory too)
    bot_reply, user_memory = get_response(user_text, history, user_memory)
    print(f"[User {user_id}] {user_text}")

    await update.message.reply_text(bot_reply)

    # Update history with new messages in compact format
    history.append({"user": user_text})
    history.append({"assistant": bot_reply})

    # Save back
    data[user_id] = history
    user_memories[user_id] = user_memory

    save_data(data)

def build_app():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("game", unknown_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing in .env")

    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL or RENDER_EXTERNAL_URL is missing in .env")

    app = build_app()
    webhook_full_url = f"{WEBHOOK_URL.rstrip('/')}/{TOKEN}"

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_full_url,
    )


if __name__ == "__main__":
    main()



# user = update.effective_user

# user.id              # unique user ID
# user.first_name      # first name
# user.last_name       # last name (may be None)
# user.username        # @username (may be None)
# user.is_bot          # True/False
# user.language_code   # e.g. 'en', 'hi'

# chat = update.effective_chat

# chat.id        # chat ID (same as user ID in private chat)
# chat.type      # private / group / supergroup / channel
# chat.title     # group name (if group)
# chat.username  # group username (if public)

# msg = update.message

# msg.text           # message text
# msg.date           # timestamp
# msg.message_id     # unique message ID
# msg.reply_to_message  # if replying to something

# msg.photo
# msg.video
# msg.document
# msg.voice
# msg.audio
# msg.location
# msg.contact