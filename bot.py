#!/usr/bin/env python
import redis
import telegram
from environs import Env
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Updater,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
)

from moltin import (
    put_product_to_cart,
    create_cart,
    get_products,
    get_moltin_access_token,
    get_product_detail,
    get_product_info,
    get_cart_info,
    get_img,
)


HANDLE_MENU, HANDLE_DESCRIPTION = range(2)


def test(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    keyboard = [
        [InlineKeyboardButton('Назад', callback_data='Назад')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        text='Test',
        chat_id=user_id,
        reply_markup=reply_markup,
    )
    return HANDLE_DESCRIPTION


def handle_menu(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    products = context.bot_data['products']
    access_token = context.bot_data['access_token']
    db = context.bot_data['db']
    if not db.get(user_id):
        cart_id = create_cart(access_token, user_id)
        db.set(user_id, cart_id)
    cart_id = db.get(user_id)
    context.user_data['cart_id'] = cart_id
    keyboard = [[InlineKeyboardButton(
        product['name'], callback_data=product['id']) for product in products['data']]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        text=cart_id,
        chat_id=user_id,
        reply_markup=reply_markup)
    return HANDLE_DESCRIPTION


def hendle_description(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    access_token = context.bot_data['access_token']
    product_id = update.callback_query.data
    context.user_data['product_id'] = product_id
    product_detail = get_product_detail(access_token, product_id)
    product_info = get_product_info(product_detail)
    url_img = get_img(access_token, product_detail)
    keyboard = [
        [
            InlineKeyboardButton('1 kg', callback_data='1'),
            InlineKeyboardButton('5 kg', callback_data='5'),
            InlineKeyboardButton('10 kg', callback_data='10'),
        ],
        [InlineKeyboardButton('Назад', callback_data='Назад')],
        [InlineKeyboardButton('Test', callback_data='Test')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_photo(
        photo=url_img,
        caption=product_info,
        chat_id=user_id,
        reply_markup=reply_markup,
    )
    bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
    )
    return HANDLE_DESCRIPTION


def add_product_to_cart(update, context):
    access_token = context.bot_data['access_token']
    cart_id = context.user_data['cart_id']
    product_id = context.user_data['product_id']
    quantity = int(update.callback_query.data)
    put_product_to_cart(access_token, cart_id, product_id, quantity)
    return HANDLE_DESCRIPTION


def button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option: {query.data}")


def main() -> None:
    env = Env()
    env.read_env()
    db = redis.Redis(
        host=env('REDIS_HOST'),
        password=env('REDIS_PASSWORD'),
        port=env('REDIS_PORT'),
        decode_responses=True,
    )
    tg_token = env('TG_TOKEN')
    moltin_client_token = env('MOLTIN_CLIENT_ID')
    access_token = get_moltin_access_token(moltin_client_token)
    products = get_products(access_token)
    bot = telegram.Bot(tg_token)
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['access_token'] = access_token
    dispatcher.bot_data['products'] = products
    dispatcher.bot_data['db'] = db
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handle_menu)],
        states={
            HANDLE_MENU: [
                CallbackQueryHandler(handle_menu),
            ],
            HANDLE_DESCRIPTION: [
                CallbackQueryHandler(test, pattern=r'Test'),
                CallbackQueryHandler(handle_menu, pattern=r'Назад'),
                CallbackQueryHandler(add_product_to_cart, pattern=r'[0-9]'),
                CallbackQueryHandler(hendle_description),
            ]
        },
        fallbacks=[],
        # name="my_conversation",
        # persistent=True,
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
