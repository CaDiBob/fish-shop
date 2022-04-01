import logging
import redis
from environs import Env

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Filters, Updater
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler

from moltin import get_products, get_moltin_access_token, get_product_detail

HANDLE_MENU = 1

logger = logging.getLogger('bot')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, chat_id, bot):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def button(update, context):

    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'Selected option: {query.data}')


def start(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    context.user_data['user_id'] = user_id
    products = context.bot_data['products']
    keyboard = [[InlineKeyboardButton(product['name'], callback_data=product['id']) for product in products['data']]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(text='Please choose:', chat_id=user_id, reply_markup=reply_markup)
    return HANDLE_MENU


def handle_menu(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    access_token = context.bot_data['access_token']
    product_id = update.callback_query.data
    product_detail = get_product_detail(access_token, product_id)
    bot.send_message(text=product_detail,
                     chat_id=user_id,
                     )
    return HANDLE_MENU


def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться'
        ' Будет скучно - пиши.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def error(update, context):
    logger.error(context.error)


def main():
    env = Env()
    env.read_env()
    db = redis.Redis(
        host=env('REDIS_HOST'),
        port=env('REDIS_PORT'),
        password=env('REDIS_PASSWORD'),
        decode_responses=True,
    )
    client_id = env('MOLTIN_CLIENT_ID')
    tg_token = env('TG_TOKEN')
    tg_chat_id = env('TG_CHAT_ID')
    access_token = get_moltin_access_token(client_id)
    products = get_products(access_token)
    updater = Updater(tg_token)
    bot = telegram.Bot(token=tg_token)
    logger.addHandler(TelegramLogsHandler(tg_chat_id, bot))
    dispatcher = updater.dispatcher
    dispatcher.bot_data['products'] = products
    dispatcher.bot_data['access_token'] = access_token
    shop = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        states={
            HANDLE_MENU: [
                CallbackQueryHandler(handle_menu),
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(shop)

    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
