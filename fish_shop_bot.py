import requests
import redis

import os
from pathlib import Path

from utils import download_pictures

from environs import Env

from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

_database = None


def get_database_connection():

    global _database
    if _database is None:
        host = env.str('ALLOWED_HOSTS', 'localhost')
        decode_responses = env.bool('DECODE_RESPONSES', True)
        port = env.str('PORT', '6379')
        db = env.str('DB', '0')
        _database = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)
    return _database


def create_a_customer(name, email):

    access_token = env.str('ACCESS_TOKEN')
    create_customer = f'https://useast.api.elasticpath.com/v2/customers'
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "data": {
            "type": 'customer',
            "name": name,
            "email": email,
        }
    }
    response = requests.post(
        create_customer,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()


def add_to_cart(quantity, product_id, cart_id):

    access_token = env.str('ACCESS_TOKEN')
    add_to_cart = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items'
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": quantity,
        }
    }
    response = requests.post(
        add_to_cart,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()


def delete_from_cart(product_id, cart_id):

    access_token = env.str('ACCESS_TOKEN')
    delete_from_cart = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items/{product_id}'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.delete(
        delete_from_cart,
        headers=headers,
    )
    response.raise_for_status()


def get_cart(cart_id):

    access_token = env.str('ACCESS_TOKEN')
    get_cart = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {}
    response = requests.get(
        get_cart,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    cart = response.json()

    return cart


def get_cart_message(cart):
    message = ''
    for item in cart['data']:
        message_item = f"""
            Вы выбрали {item['name']}
            В колличестве {item['quantity']}
            Цена данного продукта {item['unit_price']['amount'] / 100} долл.
            Всего данного продукта вы заказали на {item['value']['amount'] / 100} долл.

            """
        message += message_item
    message_total_price = f"Итого {cart['meta']['display_price']['without_discount']['amount'] / 100} долл"
    message = message + message_total_price
    return message


def get_products():

    access_token = env.str('ACCESS_TOKEN')
    get_products = 'https://useast.api.elasticpath.com/pcm/products'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {}
    response = requests.get(
        get_products,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    products = response.json()['data']

    return products


def get_product(product_id):

    access_token = env.str('ACCESS_TOKEN')
    get_product = f'https://useast.api.elasticpath.com/pcm/products/{product_id}'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {}
    response = requests.get(
        get_product,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    product = response.json()['data']

    return product


def get_price(sku):

    access_token = env.str('ACCESS_TOKEN')
    price_book_id = env.str('PRICE_BOOK_ID')
    get_prices = f'https://useast.api.elasticpath.com/pcm/pricebooks/{price_book_id}/prices'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {}
    response = requests.get(
        get_prices,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    prices = response.json()['data']
    for price in prices:
        if price['attributes']['sku'] == sku:
            return price['attributes']['currencies']['USD']['amount'] / 100
    return 'Цена не найдена'


def get_product_photo_link(photo_id):

    access_token = env.str('ACCESS_TOKEN')
    get_product_photo = f'https://useast.api.elasticpath.com/v2/files/{photo_id}'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {}
    response = requests.get(
        get_product_photo,
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    return response.json()['data']['link']['href']


def get_keyboard_main_menu():
    products = get_products()

    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                f"{product['attributes']['name']}", callback_data=f"{product['id']}"
            )
        ])
    keyboard.append(
        [
            InlineKeyboardButton("Корзина", callback_data="корзина")
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def start(update: Update, context: CallbackContext):

    reply_markup = get_keyboard_main_menu()

    context.bot.send_message(
        chat_id=update.message.chat.id,
        text='Привет! Выбери товар.',
        reply_markup=reply_markup,
    )
    return "HANDLE_MENU"


def handle_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'корзина':
        cart_id = query.message.chat_id
        cart = get_cart(cart_id)
        message = get_cart_message(cart)

        keyboard = []
        for item in cart['data']:
            keyboard.append([
                InlineKeyboardButton(
                    f"Удалить из корзины {item['name']}", callback_data=f"{item['id']}"
                )
            ])
        keyboard.append(
            [
                InlineKeyboardButton("В меню", callback_data="меню")
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton("Оплата", callback_data="оплата")
            ]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=message,
            reply_markup=reply_markup,
        )
        return "HANDLE_CART"

    product_id = query.data
    product = get_product(product_id)
    product_name = product['attributes']['name']
    photo_id = product['relationships']['main_image']['data']['id']
    photo_link = get_product_photo_link(photo_id)
    price = get_price(product['attributes']['sku'])

    download_pictures(product_name, photo_link)
    picture_file_path = Path.cwd() / product_name

    message = f"""
            Вы выбрали {product_name}

            Цена данного продукта {price} долл.

            {product['attributes']['description']}
            """

    keyboard = [
        [
            InlineKeyboardButton("1 кг", callback_data=f'1 {product_id}'),
            InlineKeyboardButton("5 кг", callback_data=f'5 {product_id}'),
            InlineKeyboardButton("10 кг", callback_data=f'10 {product_id}'),
        ],

        [
            InlineKeyboardButton("Назад", callback_data='назад'),
        ],
        [
            InlineKeyboardButton("Корзина", callback_data='корзина'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )

    with open(picture_file_path, 'rb') as photo:
        context.bot.send_photo(
            caption=message,
            chat_id=query.message.chat_id,
            photo=photo,
            reply_markup=reply_markup,
        )
    os.remove(picture_file_path)
    return "HANDLE_DESCRIPTION"


def handle_description(update: Update, context: CallbackContext):
    query = update.callback_query
    cart_id = query.message.chat_id
    if query.data == 'назад':

        reply_markup = get_keyboard_main_menu()

        context.bot.send_message(
            chat_id=query.message.chat_id,
            text='Выбери товар.',
            reply_markup=reply_markup,
        )
        return 'HANDLE_MENU'
    elif query.data == 'корзина':
        cart = get_cart(cart_id)
        message = get_cart_message(cart)

        keyboard = []
        for item in cart['data']:
            keyboard.append([
                InlineKeyboardButton(
                    f"Удалить из корзины {item['name']}", callback_data=f"{item['id']}"
                )
            ])
        keyboard.append(
            [
                InlineKeyboardButton("В меню", callback_data="меню")
            ],
        )
        keyboard.append(
            [
                InlineKeyboardButton("Оплата", callback_data="оплата")
            ],
        )
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=message,
            reply_markup=reply_markup,
        )
        return "HANDLE_CART"

    quantity, product_id = query.data.split()
    add_to_cart(int(quantity), product_id, cart_id)

    return "HANDLE_DESCRIPTION"


def handle_cart(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'меню':

        reply_markup = get_keyboard_main_menu()

        context.bot.send_message(
            chat_id=query.message.chat_id,
            text='Выбери товар.',
            reply_markup=reply_markup,
        )
        return 'HANDLE_MENU'
    elif query.data == 'оплата':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text='Пришлите, пожалуйста, ваш email',
        )
        return 'WAITING_EMAIL'

    cart_id = query.message.chat_id
    product_id = query.data

    delete_from_cart(product_id, cart_id)

    context.bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )

    cart = get_cart(cart_id)
    message = get_cart_message(cart)

    keyboard = []
    for item in cart['data']:
        keyboard.append([
            InlineKeyboardButton(
                f"Удалить из корзины {item['name']}", callback_data=f"{item['id']}"
            )
        ])
    keyboard.append(
        [
            InlineKeyboardButton("В меню", callback_data="меню")
        ],
    )
    keyboard.append(
        [
            InlineKeyboardButton("Оплата", callback_data="оплата")
        ],
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=message,
        reply_markup=reply_markup,
    )
    return "HANDLE_CART"


def handle_waiting_email(update: Update, context: CallbackContext):
    message = update.message
    customer_name = message.chat.first_name
    customer_email = message.text
    context.bot.send_message(
        chat_id=message.chat.id,
        text=f'Вы прислали: {customer_email}',
    )
    create_a_customer(customer_name, customer_email)

    return "WAITING_EMAIL"


def handle_users_reply(update: Update, context: CallbackContext):
    message = update.message
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id)

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        "HANDLE_DESCRIPTION": handle_description,
        "HANDLE_CART": handle_cart,
        "WAITING_EMAIL": handle_waiting_email,
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
    except requests.exceptions.HTTPError as err:
        if '422 Client Error' in str(err):
            context.bot.send_message(
                chat_id=message.chat.id,
                text=f'Проверьте email',
            )
    except Exception as err:
        print(err)


def main():

    tg_token = env.str('TG_BOT_TOKEN')
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    main()
