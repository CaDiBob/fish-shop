#!/usr/bin/env python
from unicodedata import name
import redis
import telegram
from environs import Env
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    Filters,
    MessageHandler,
    Updater,
)

from moltin import (
    create_cart,
    create_customer,
    get_products,
    get_moltin_access_token,
    get_product_detail,
    get_product_info,
    get_cart_products,
    get_cart_info_products,
    get_cart_sum,
    get_img,
    put_product_to_cart,
    remove_cart_item,
)


HANDLE_MENU, HANDLE_DESCRIPTION, HANDLE_CART, WAITING_EMAIL = range(4)


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
    keyboard = [
        [InlineKeyboardButton(
            product['name'], callback_data=product['id']) for product in products['data']],
        [InlineKeyboardButton('Корзина', callback_data='Корзина')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        text='Добро пожаловать в наш магазин "Вкусная рыбка"',
        chat_id=user_id,
        reply_markup=reply_markup,
    )
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
        [InlineKeyboardButton('Корзина', callback_data='Корзина')],
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


def cart_info(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    access_token = context.bot_data['access_token']
    cart_id = context.user_data['cart_id']
    cart_products = get_cart_products(access_token, cart_id)
    cart_info = get_cart_info_products(cart_products)
    cart_sum = get_cart_sum(access_token, cart_id)
    keyboard = list()
    for product in cart_products:
        title = product['name']
        context.user_data['title'] = title
        product_id = product['id']
        keyboard.append(
            [
                InlineKeyboardButton(
                    f'Удалить из корзины {title}',
                    callback_data=product_id,
                )
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                'В меню',
                callback_data='В меню',
            ),

            InlineKeyboardButton(
                'Оплатить',
                callback_data='Оплатить'
            )
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        text=f'{cart_info}\n{cart_sum}',
        chat_id=user_id,
        reply_markup=reply_markup,
    )
    return HANDLE_CART


def remove_item(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    access_token = context.bot_data['access_token']
    cart_id = context.user_data['cart_id']
    product_id = update.callback_query.data
    title = context.user_data['title']
    keyboard = [
        [InlineKeyboardButton('Корзина', callback_data='Корзина')]
    ]
    remove_cart_item(access_token, cart_id, product_id)
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        text=f'Товар {title} удален из корзины',
        chat_id=user_id,
        reply_markup=reply_markup,
    )
    return HANDLE_CART


def waiting_email(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    keyboard = [
        [InlineKeyboardButton('Корзина', callback_data='Корзина')],
        [InlineKeyboardButton('В меню', callback_data='В меню')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        text='''
        Введите ваш email наш специалист свяжется с вами
        ''',
        chat_id=user_id,
        reply_markup=reply_markup,
    )
    return WAITING_EMAIL


def check_email(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    email = update.message.text
    context.user_data['email'] = email
    keyboard = [
        [InlineKeyboardButton('Верно', callback_data='Верно')],
        [InlineKeyboardButton('Ввести снова', callback_data='Ввести снова')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        text=f'Вы ввели: {email}',
        chat_id=user_id,
        reply_markup=reply_markup,
    )
    WAITING_EMAIL


def save_customer(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    access_token = context.bot_data['access_token']
    db = context.bot_data['db']
    email = context.user_data['email']
    keyboard = [
        [InlineKeyboardButton('В меню', callback_data='В меню')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if not db.get(email):
        customer_id = create_customer(access_token, email)['id']
        db.set(email, customer_id)
    bot.send_message(
        text='Спасибо! Мы скоро свяжемся с вами.',
        chat_id=user_id,
        reply_markup=reply_markup,
    )
    return HANDLE_MENU


def cancel(update, context):
    update.message.reply_text(
        'До свиданья! Мы всегда рады вам.'
    )
    return ConversationHandler.END


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
                CallbackQueryHandler(cart_info, pattern=r'Корзина'),
                CallbackQueryHandler(handle_menu, pattern=r'Назад'),
                CallbackQueryHandler(add_product_to_cart, pattern=r'[0-9]'),
                CallbackQueryHandler(hendle_description),
            ],
            HANDLE_CART: [
                CallbackQueryHandler(cart_info, pattern=r'Корзина'),
                CallbackQueryHandler(waiting_email, pattern=r'Оплатить'),
                CallbackQueryHandler(handle_menu, pattern=r'В меню'),
                CallbackQueryHandler(remove_item),
            ],
            WAITING_EMAIL: [
                MessageHandler(Filters.text & ~Filters.command, check_email),
                CallbackQueryHandler(waiting_email, pattern=r'Ввести снова'),
                CallbackQueryHandler(save_customer, pattern=r'Верно'),
                CallbackQueryHandler(cart_info, pattern=r'Корзина'),
                CallbackQueryHandler(handle_menu, pattern=r'В меню'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
