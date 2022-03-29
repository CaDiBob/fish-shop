import logging
import redis
from environs import Env

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CommandHandler, MessageHandler

from moltin import get_products, get_moltin_access_token

_database = None

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
    products = context.bot_data['products']
    keyboard = [[InlineKeyboardButton(product['name'], callback_data=product['id']) for product in products['data']]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

    return "ECHO"


def echo(update, context):
    update.message.reply_text(update.message.text)


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
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo
    ))
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
