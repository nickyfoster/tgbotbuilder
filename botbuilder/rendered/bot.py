import asyncio
from asyncio import Event
from typing import Optional

from telegram import __version__ as TG_VER, InlineKeyboardButton, InlineKeyboardMarkup

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler, Application,
)

INLINE_BUTTON_ROUTES = "inline_button_routes"


class TelegramBot:
    def __init__(self):
        self.start_command_string = "start"
        self.application = self.init_bot()

    def init_bot(self):
        api_key = ""
        application = Application.builder().token(api_key).build()
        application.add_handler(self.get_conv_handler())
        return application

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello!")
        user_data = context.user_data
        await self.block_1(update, context)
        return INLINE_BUTTON_ROUTES

    
    async def block_1(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.callback_query:
            await update.callback_query.answer()
        reply_text = "Block one"
        buttons = [[
            InlineKeyboardButton("Button #1", callback_data="BLOCK_3_PATH"),
            InlineKeyboardButton("Button #2", callback_data="BLOCK_4_PATH"),
            InlineKeyboardButton("Button #3", callback_data="BLOCK_5_PATH"),
            InlineKeyboardButton("Button #4", callback_data="BLOCK_6_PATH"),
        ]]
        keyboard = InlineKeyboardMarkup(buttons)
        if update.callback_query:
            await update.callback_query.edit_message_text(text=reply_text, reply_markup=keyboard)
        else:
            await update.message.reply_text(text=reply_text, reply_markup=keyboard)
        return INLINE_BUTTON_ROUTES
    async def block_3(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="End #1")
        return INLINE_BUTTON_ROUTES
    async def block_4(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="End #2")
        return INLINE_BUTTON_ROUTES
    async def block_5(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="End #3")
        return INLINE_BUTTON_ROUTES
    async def block_6(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.callback_query:
            await update.callback_query.answer()
        reply_text = "Block two"
        buttons = [[
            InlineKeyboardButton("Back to block one", callback_data="BLOCK_1_PATH"),
        ]]
        keyboard = InlineKeyboardMarkup(buttons)
        if update.callback_query:
            await update.callback_query.edit_message_text(text=reply_text, reply_markup=keyboard)
        else:
            await update.message.reply_text(text=reply_text, reply_markup=keyboard)
        return INLINE_BUTTON_ROUTES

    def get_conv_handler(self):
        return ConversationHandler(
            entry_points=[CommandHandler(self.start_command_string, self.start)],
            states={
                INLINE_BUTTON_ROUTES: [
                    CallbackQueryHandler(self.block_1,
                                         pattern="^" + "BLOCK_1_PATH" + "$"),
                    CallbackQueryHandler(self.block_3,
                                         pattern="^" + "BLOCK_3_PATH" + "$"),
                    CallbackQueryHandler(self.block_4,
                                         pattern="^" + "BLOCK_4_PATH" + "$"),
                    CallbackQueryHandler(self.block_5,
                                         pattern="^" + "BLOCK_5_PATH" + "$"),
                    CallbackQueryHandler(self.block_6,
                                         pattern="^" + "BLOCK_6_PATH" + "$"),
                ]
            },
            fallbacks=[CommandHandler(self.start_command_string, self.start)]
        )

    async def run_bot(self, stop_event: Optional[Event] = None):
        async with self.application:
            await self.application.start()
            await self.application.updater.start_polling()
            await stop_event.wait()
            await self.application.updater.stop()
            await self.application.stop()

async def main():
    bot = TelegramBot()
    stop_event = asyncio.Event()
    try:
        await asyncio.create_task(bot.run_bot(stop_event=stop_event))
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == '__main__':
    asyncio.run(main())