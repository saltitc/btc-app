import math
import telebot
import config
import pydantic_models

bot = telebot.TeleBot(config.bot_token)


@bot.message_handler(commands=['start'])
def start_message(message):
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
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')  # кнопка возврата в меню
    markup.add(btn1)

    balance = 0  # сюда будем получать баланс через API
    text = f'Ваш баланс: {balance}'

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Перевести')
def transaction(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)

    text = f'Введите адрес кошелька куда хотите перевести: '
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='История')
def history(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)

    transactions = ['1', '2', '3']  # будут загружены транзакции
    text = f'Ваши транзакции{transactions}'

    bot.send_message(message.chat.id, text, reply_markup=markup)


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


users = config.fake_database['users']

# ------- For pagination ------- #
all_pages = math.ceil(len(users) / 4)  # количество страниц
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
        inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
                                                             callback_data=f"user_{user['id']}"))
    current = 4
    bot.send_message(message.chat.id, text,
                     reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global all_pages
    global page
    global current

    query_type = call.data.split('_')[0]  # получаем тип запроса

    # запрос информации по пользователю
    if query_type == 'user':
        user_id = call.data.split('_')[1]  # получаем id пользователя

        inline_markup = telebot.types.InlineKeyboardMarkup()

        for user in users[current - 4:current]:
            # поиск пользователя по id из списка пользователей на странице
            if str(user['id']) == user_id:
                inline_markup.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data='current'),
                                  telebot.types.InlineKeyboardButton(text="Удалить юзера",
                                                                     callback_data=f'delete_user_{user_id}'))
                bot.edit_message_text(text=f'Данные по юзеру:\n'
                                           f'ID: {user["id"]}\n'
                                           f'Имя: {user["name"]}\n'
                                           f'Ник: {user["nick"]}\n'
                                           f'Баланс: {user["balance"]}',
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
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
                                                                 callback_data=f"user_{user['id']}"))

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
        user_id = int(call.data.split('_')[2])  # получаем и превращаем id в число
        for i, user in enumerate(users):
            if user['id'] == user_id:
                print(f'Удален Юзер: {users[i]}')
                users.pop(i)
        inline_markup = telebot.types.InlineKeyboardMarkup()
        for user in users:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Юзер: {user["name"]}',
                                                                 callback_data=f"user_{user['id']}"))
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

    balance = 0
    for user in users:
        balance += user['balance']

    text = f'Общий баланс: {balance}'
    bot.send_message(message.chat.id, text, reply_markup=markup)


bot.infinity_polling()
