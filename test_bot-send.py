from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Initialize the bot with your token
TOKEN = '6992700934:AAHd1u6WZ5kSJtzL25xBONb1rHK1bbeT4DI'

# Create the application instance
application = Application.builder().token(TOKEN).build()

# Define a start command handler
async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello! I'm your bot. How can I help you?\nYour chat ID is: {chat_id}")

# Define a message handler
async def echo(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

# Add handlers to the application
application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Start the bot and run it until you stop it with Ctrl-C
if __name__ == '__main__':
    application.run_polling()
