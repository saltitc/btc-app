import telebot
import config
import pydantic_models
import client
import json
import math
from datetime import datetime
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

bot = telebot.TeleBot(config.bot_token)


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        client.create_user({"tg_ID": message.from_user.id, "nick": message.from_user.username})
    except Exception as Ex:
        # bot.send_message(message.chat.id, f'Возникла ошибка: {Ex.args}')
        pass

    # объект для работы с кнопками
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    # buttons
    btn1 = telebot.types.KeyboardButton('Кошелек')
    btn2 = telebot.types.KeyboardButton('Перевести')
    btn3 = telebot.types.KeyboardButton('История')

    # добавляем кнопки
    markup.add(btn1, btn2, btn3)

    # сообщение
    text = f'Привет {message.from_user.full_name}, я твой бот-криптокошелек, \n' \
           'у меня ты можешь хранить и отправлять биткоины'

    # отправка сообщения с кнопками к reply_markup
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Кошелек')
def wallet(message):
    wallet = client.get_user_wallet_by_tg_id(message.from_user.id)

    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')  # кнопка возврата в меню
    markup.add(btn1)

    text = f'Ваш баланс: {wallet["balance"] / 100000000} BTC\n' \
           f'Адрес вашего кошелька:\n{wallet["address"]}'

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='История')
def history(message):
    inline_markup = telebot.types.InlineKeyboardMarkup()

    transactions = client.get_user_transactions(client.get_user_by_tg_id(message.from_user.id)['id'])
    for n, tr in enumerate(transactions):
        tx_date = datetime.strptime(tr['date_of_transaction'], '%Y-%m-%dT%X.%f')
        inline_markup.add(telebot.types.InlineKeyboardButton(
            text=f'Дата: {tx_date.strftime("%d.%m.%Y")} ({round(tr["amount_btc_without_fee"] / 3391, 2)} USD)',
            callback_data=f"tx_{n}"
        ))

    text = f"История ваших транзакций:\n"

    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(regexp='Меню')
def menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    btn1 = telebot.types.KeyboardButton('Кошелек')
    btn2 = telebot.types.KeyboardButton('Перевести')
    btn3 = telebot.types.KeyboardButton('История')
    markup.add(btn1, btn2, btn3)

    text = f'Главное меню'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Я в консоли')
def print_me(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    print(message.from_user.to_dict())
    text = f'Ты: {message.from_user.to_dict()}'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Админка")
def admin_panel(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Общий баланс')
    btn2 = telebot.types.KeyboardButton('Все юзеры')
    btn3 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1, btn2, btn3)

    text = f'Админ-панель'
    bot.send_message(message.chat.id, text, reply_markup=markup)


# ------- For pagination ------- #
all_pages = math.ceil(len(client.get_users()) / 4)  # количество страниц
page = 1  # страница
current = 0  # количество пользователей до страницы


# ------- For pagination ------- #


@bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Все юзеры")
def all_users(message):
    global all_pages
    global page
    global current

    current = 0
    page = 1
    text = f'Юзеры:'
    users = client.get_users()
    inline_markup = telebot.types.InlineKeyboardMarkup()  # объект с инлайн-разметкой

    # Если количество пользователей больше 4
    if len(users) > 4:
        inline_markup.add(
            telebot.types.InlineKeyboardButton(text=f'Страница №{page}', callback_data='Страница №1'),
            telebot.types.InlineKeyboardButton(text='Вперед', callback_data='next'))
    else:
        inline_markup.add(telebot.types.InlineKeyboardButton(text='Страница №1', callback_data='Страница №1'))

    # список из 4-х первых пользователей
    for user in users[0:4]:
        inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["tg_ID"]}',
                                                             callback_data=f"user_{user['tg_ID']}"))
    current = 4
    bot.send_message(message.chat.id, text,
                     reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global all_pages
    global page
    global current

    query_type = call.data.split('_')[0]  # получаем тип запроса
    users = client.get_users()

    # запрос информации по транзакции
    if query_type == 'tx':
        tx_id = call.data.split('_')[1]  # получаем id транзакции
        inline_markup = telebot.types.InlineKeyboardMarkup()

        transaction = client.get_user_transactions(client.get_user_by_tg_id(call.from_user.id)['id'])[int(tx_id)]
        inline_markup.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data='txs'))

        tx_date = datetime.strptime(transaction['date_of_transaction'], '%Y-%m-%dT%X.%f')
        transaction_info = f"<b>Адрес получателя</b>: <i>{transaction['receiver_address']}</i>\n" \
                           f"<b>Сумма перевода</b>: <i>{round(transaction['amount_btc_without_fee'] / 3391, 2)} USD</i>\n" \
                           f"<b>Комиссия</b>: <i>{round(transaction['fee'] / 3391, 2)} USD</i>\n" \
                           f"<b>Хеш транзакции</b>: <i>{transaction['tx_hash']}</i>\n" \
                           f"<b>Дата транзакции</b>: <i>{tx_date.strftime('%d.%m.%Y %H:%M:%S')}</i>\n"

        bot.edit_message_text(text=transaction_info,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_markup,
                              parse_mode='HTML')

    if query_type == 'txs':
        inline_markup = telebot.types.InlineKeyboardMarkup()

        transactions = client.get_user_transactions(client.get_user_by_tg_id(call.from_user.id)['id'])
        for n, tr in enumerate(transactions):
            tx_date = datetime.strptime(tr['date_of_transaction'], '%Y-%m-%dT%X.%f')
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Дата: {tx_date.strftime("%d.%m.%Y")}',
                                                                 callback_data=f"tx_{n}"))
        bot.edit_message_text(text="Ваши транзакции:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_markup)

    # запрос информации по пользователю
    if query_type == 'user':
        user_id = call.data.split('_')[1]  # получаем id пользователя

        inline_markup = telebot.types.InlineKeyboardMarkup()

        for user in users[current - 4:current]:
            # поиск пользователя по id из списка пользователей на странице
            if str(user['tg_ID']) == user_id:
                inline_markup.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data='current'),
                                  telebot.types.InlineKeyboardButton(text="Удалить юзера",
                                                                     callback_data=f'delete_user_{user_id}'))
                bot.edit_message_text(text=f'Данные по юзеру:\n'
                                           f'ID: {user["tg_ID"]}\n'
                                           f'Ник: {user.get("nick")}\n'
                                           f'Баланс: {client.get_user_balance_by_id(user["id"]) / 100000000} BTC\n'
                                           f'Кошелек: {client.get_info_about_user(user["id"])["wallet"]["address"]}',
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=inline_markup)
                print(f"Запрошен {user}")
                break

    # следующая страница
    if query_type == 'next':
        inline_markup = telebot.types.InlineKeyboardMarkup()
        page += 1

        # если это не первая и не последняя страница
        if page > 1 and page != all_pages:
            inline_markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back'),
                              telebot.types.InlineKeyboardButton(text=f'Страница №{page}',
                                                                 callback_data=f'Страница №'),
                              telebot.types.InlineKeyboardButton(text='Вперед', callback_data='next'))

        # если это последняя страница
        elif page == all_pages:
            inline_markup.add(
                telebot.types.InlineKeyboardButton(text='Назад', callback_data='back'),
                telebot.types.InlineKeyboardButton(text=f'Страница №{page}',
                                                   callback_data=f'Страница №'))

        for user in users[current:page * 4]:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
                                                                 callback_data=f"user_{user['id']}"))

            bot.edit_message_text(text="Юзеры:",
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=inline_markup)
        current = page * 4

    # возвращает нас на текущую страницу со списком пользователей
    # после нажатия кнопки назад из карточки информации по пользователю
    if query_type == 'current':
        inline_markup = telebot.types.InlineKeyboardMarkup()

        # если это первая страница из нескольких
        if page == 1 and all_pages != 1:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Страница №{page}',
                                                                 callback_data=f'Страница №'),
                              telebot.types.InlineKeyboardButton(text='Вперед', callback_data='next'))
        # если количество страниц равно одному
        elif all_pages == 1:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Страница №{page}',
                                                                 callback_data=f'Страница №'))

        # если это не первая и не последняя страница
        elif page > 1 and page != all_pages:
            inline_markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back'),
                              telebot.types.InlineKeyboardButton(text=f'Страница №{page}',
                                                                 callback_data=f'Страница №'),
                              telebot.types.InlineKeyboardButton(text='Вперед', callback_data='next'))
        # если это последняя страница
        elif page in range(all_pages, all_pages + 1):
            inline_markup.add(
                telebot.types.InlineKeyboardButton(text='Назад', callback_data='back'),
                telebot.types.InlineKeyboardButton(text=f'Страница №{page}',
                                                   callback_data=f'Страница №'))

        for user in users[(page * 4) - 4:page * 4]:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["tg_ID"]}',
                                                                 callback_data=f"user_{user['tg_ID']}"))

            bot.edit_message_text(text="Юзеры:",
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=inline_markup)

    # предыдущая страница
    if query_type == 'back':
        inline_markup = telebot.types.InlineKeyboardMarkup()
        page -= 1
        current = page * 4

        # если это не первая и не последняя страница
        if page > 1 and page != all_pages:
            inline_markup.add(telebot.types.InlineKeyboardButton(text='Назад', callback_data='back'),
                              telebot.types.InlineKeyboardButton(text=f'Страница №{page}',
                                                                 callback_data=f'Страница №'),
                              telebot.types.InlineKeyboardButton(text='Вперед', callback_data='next'))

        # если это первая страница
        elif page == 1:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Страница №{page}',
                                                                 callback_data=f'Страница №'),
                              telebot.types.InlineKeyboardButton(text='Вперед', callback_data='next'))

        for user in users[(page - 1) * 4:current]:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
                                                                 callback_data=f"user_{user['id']}"))
            bot.edit_message_text(text="Юзеры:",
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=inline_markup)

    # удаление пользователя
    if query_type == 'delete' and call.data.split('_')[1] == 'user':

        user_id = int(call.data.split('_')[2])  # получаем и превращаем наш айди в число
        for i, user in enumerate(users):
            if user['tg_ID'] == user_id:
                print(f'Удален Юзер: {users[i]}')
                client.delete_user(users.pop(i)['id'])
        inline_markup = telebot.types.InlineKeyboardMarkup()
        for user in users:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["tg_ID"]}',
                                                                 callback_data=f"user_{user['tg_ID']}"))
        bot.edit_message_text(text="Юзеры:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_markup)


@bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Общий баланс")
def total_balance(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    btn2 = telebot.types.KeyboardButton('Админка')
    markup.add(btn1, btn2)
    balance = client.get_total_balance()

    text = f'Общий баланс: {balance / 100000000} BTC'
    bot.send_message(message.chat.id, text, reply_markup=markup)


# конечный автомат для обработки диалога с отправкой транзакции
states_list = ["ADDRESS", "AMOUNT", "CONFIRM"]
states_of_users = {}


@bot.message_handler(regexp='Перевести')
def start_transaction(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    text = f'Введите адрес кошелька куда хотите перевести: '
    bot.send_message(message.chat.id, text, reply_markup=markup)
    # тут мы даём юзеру состояние при котором ему будет возвращаться следующее сообщение
    states_of_users[message.from_user.id] = {"STATE": "ADDRESS"}


@bot.message_handler(func=lambda message: states_of_users.get(message.from_user.id)["STATE"] == 'ADDRESS')
def get_amount_of_transaction(message):
    if message.text == "Меню":
        del states_of_users[message.from_user.id]
        menu(message)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    text = f'Введите сумму в сатоши (1 BTC = 99978005 SATS), которую хотите перевести: '
    bot.send_message(message.chat.id, text, reply_markup=markup)
    # тут мы даём юзеру состояние при котором ему будет возвращаться следующее сообщение
    states_of_users[message.from_user.id]["STATE"] = "AMOUNT"
    states_of_users[message.from_user.id]["ADDRESS"] = message.text


@bot.message_handler(func=lambda message: states_of_users.get(message.from_user.id)["STATE"] == 'AMOUNT')
def get_confirmation_of_transaction(message):
    if message.text == "Меню":
        del states_of_users[message.from_user.id]
        menu(message)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    if message.text.isdigit():
        text = f'Вы хотите перевести {message.text} сатоши,\n' \
               f'на биткоин-адрес {states_of_users[message.from_user.id]["ADDRESS"]}: '
        confirm = telebot.types.KeyboardButton('Подтверждаю')
        markup.add(confirm)
        bot.send_message(message.chat.id, text, reply_markup=markup)
        # тут мы даём юзеру состояние при котором ему будет возвращаться следующее сообщение
        states_of_users[message.from_user.id]["STATE"] = "CONFIRM"
        states_of_users[message.from_user.id]["AMOUNT"] = int(message.text)
    else:
        text = f'Вы ввели не число, попробуйте заново: '
        bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: states_of_users.get(message.from_user.id)["STATE"] == 'CONFIRM')
def get_hash_of_transaction(message):
    if message.text == "Меню":
        del states_of_users[message.from_user.id]
        menu(message)
    elif message.text == "Подтверждаю":
        transaction = client.create_transaction(
            message.from_user.id,
            states_of_users[message.from_user.id]['ADDRESS'],
            states_of_users[message.from_user.id]['AMOUNT']
        )
        tx_date = datetime.strptime(transaction['date_of_transaction'], '%Y-%m-%dT%X.%f')
        bot.send_message(message.chat.id, f"Транзакция прошла успешно.\n\nИнформация о транзакции:\n"
                                          f"<b>Адрес отправителя</b>: <i>{transaction['sender_address']}</i>\n"
                                          f"<b>Адрес получателя</b>: <i>{transaction['receiver_address']}</i>\n"
                                          f"<b>Сумма перевода</b>: <i>{transaction['amount_btc_without_fee']} SATS "
                                          f"({round(transaction['amount_btc_without_fee'] / 3391, 2)} USD)</i>\n"
                                          f"<b>Комиссия</b>: <i>{transaction['fee']} SATS "
                                          f"({round(transaction['fee'] / 3391, 2)} USD)</i>\n"
                                          f"<b>Дата транзакции</b>: <i>{tx_date.strftime('%d.%m.%Y %H:%M:%S')}</i>\n"
                                          f"<b>Хеш транзакции</b>: <i>{transaction['tx_hash']}</i>\n",
                         parse_mode='HTML')

        del states_of_users[message.from_user.id]
        menu(message)

# запуск бота
bot.infinity_polling()
