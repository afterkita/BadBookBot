import os
import telebot
import config
from use_db import make_user, get_book, get_books, get_my_books
from create_report import make_template_report
from create_act import make_template

bot = telebot.TeleBot(config.TOKEN)
users = {}

BAD_BOOKS = get_books()


@bot.message_handler(commands=['start'])
def start_dialog(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    organization_button = telebot.types.KeyboardButton('Организация')
    user_button = telebot.types.KeyboardButton('Личное пользование')
    markup.add(organization_button, user_button)

    make_user(message.chat.id, message.from_user.username)

    bot.send_message(message.chat.id,
                     'Привет, я телеграм-бот Имя, который проверяет различные материалы на наличие их в регистре экстремистских материалов МЮ РФ')
    bot.send_message(message.chat.id,
                     'Если вы собираетесь использовать для отслеживания запрещённых книг в своей библиотеке, то нажмите Организация, иначе нажмите Личное пользование ',
                     reply_markup=markup)


def make_act(message):
    w = next(users[message.chat.id][0])
    users[message.chat.id][1].append(message.text)
    if w == '':
        users[message.chat.id][1].append(message.chat.id)
        src = make_template(*users[message.chat.id][1])

        with open(src, 'rb') as f:
            bot.send_document(message.chat.id, document=f)
            f.close()
            os.remove(src)
        return
    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, w), make_act)


def get_doc(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
            new_file.close()

        my_books = get_my_books(src)
        os.remove(src)
        bad_books_in_my_collection = list(BAD_BOOKS & my_books)

        if bad_books_in_my_collection:
            users[message.chat.id][1].append(bad_books_in_my_collection)

            bot.register_next_step_handler(
                bot.send_message(message.chat.id, next(users[message.chat.id][0]), reply_markup=None), make_act)
        else:
            bot.send_message(message.chat.id, "Совпадения не обнаружены!")
    except Exception as e:
        bot.reply_to(message, e)


def find_material(message):
    result = get_book(message.text)
    if result is not None:
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Отсутствует")


def make_report(message):
    w = next(users[message.chat.id][0])
    users[message.chat.id][1].append(message.text)
    if w == '':
        users[message.chat.id][1].append(message.chat.id)
        src = make_template_report(*users[message.chat.id][1])

        with open(src, 'rb') as f:
            bot.send_document(message.chat.id, document=f)
            f.close()
            os.remove(src)
        return
    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, w), make_report)


@bot.message_handler(commands=['find'])
def find_handler(message):
    name = message.text[6:]
    result = get_book(name)
    if result is not None:
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Отсутствует")


@bot.message_handler(commands=['check'])
def check_handler(message):
    users[message.chat.id] = [config.act_dialog(), []]
    # проведена проверка и вызов функции формировании акта

    bot.register_next_step_handler(bot.send_message(message.chat.id, "Пришлите мне файл с вашей библиотекой"), get_doc)


@bot.message_handler(commands=['report'])
def report_handler(message):
    users[message.chat.id] = [config.act_dialog_report(), []]
    bot.register_next_step_handler(bot.send_message(message.chat.id, next(users[message.chat.id][0])), make_report)


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id,
                     "Список команд:\n1)Проверка материала на наличие в реестре запрещённых материалов - /find ["
                     "name]\n2) "
                     "Проверка списка материалов в реестре на наличие запрещённой литературы - /check"
                     "\n3) Отправить жалобу на материал - /report ")


@bot.message_handler(content_types=["text"])
def work(message):
    if message.text == "Организация":

        organization_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        find_button = telebot.types.KeyboardButton("1)Проверка материала на наличие в реестре запрещённых материалов")
        check_button = telebot.types.KeyboardButton(
            "2)Проверка списка материалов в реестре на наличие запрещённой литературы")

        organization_markup.add(find_button, check_button)
        bot.send_message(message.chat.id,
                         "Список команд:\n1)Проверка материала на наличие в реестре запрещённых материалов - /find ["
                         "name]\n2) "
                         "Проверка списка материалов в реестре на наличие запрещённой литературы - /check",
                         reply_markup=organization_markup)
    elif message.text == "Личное пользование":
        person_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        find_button = telebot.types.KeyboardButton("1)Проверка материала на наличие в реестре запрещённых материалов")
        report_button = telebot.types.KeyboardButton("2)Отправить жалобу на материал")
        person_markup.add(find_button, report_button)
        bot.send_message(message.chat.id,
                         "Список команд:\n1)Проверка материала на наличие в реестре запрещённых материалов - /find ["
                         "name]\n2)Отправить жалобу на материал - /report",
                         reply_markup=person_markup)
    elif message.text == "1)Проверка материала на наличие в реестре запрещённых материалов":
        bot.send_message(message.chat.id, "Отправьте название")
        bot.register_next_step_handler(message, find_material)
    elif message.text == "2)Проверка списка материалов в реестре на наличие запрещённой литературы":
        check_handler(message)
    elif message.text == "2)Отправить жалобу на материал":
        users[message.chat.id] = [config.act_dialog_report(), []]
        bot.register_next_step_handler(bot.send_message(message.chat.id, next(users[message.chat.id][0])), make_report)
    else:
        bot.send_message(message.chat.id, "Непонятная команда /help")


while True:
    try:
        bot.polling(none_stop=True)
    except Exception:
        pass
