import telebot
import config
from use_db import make_user
from use_db import get_book

bot = telebot.TeleBot(config.TOKEN)


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
    pass


def find_material(message):
    if get_book(message.text):
        bot.send_message(message.chat.id, "Найдена")
    else:
        bot.send_message(message.chat.id, "Отсутствует")



def check_material(message):
    bot.send_message(message.chat.id, "Отправьте файл(список)")
    # запрос


def report_material(message):
    bot.send_message(message.chat.id, message.text)


@bot.message_handler(commands=['find'])
def find_handler(message):
    name = message.text[5:]
    fin


@bot.message_handler(commands=['check'])
def check_handler(message):
    bot.send_message(message.chat.id, message.text)


@bot.message_handler(commands=['report'])
def report_handler(message):
    bot.send_message(message.chat.id, message.text)


@bot.message_handler(content_types=["text"])
def work(message):
    if message.text == "Организация":
        organization_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        find_button = telebot.types.KeyboardButton("1)Проверка материала на наличие в реестре запрещённых материалов")
        check_button = telebot.types.KeyboardButton(
            "2)Проверка списка материалов в реестре на наличие запрещённой литературы")
        make_act_button = telebot.types.KeyboardButton("3)Составление акта")

        organization_markup.add(find_button, check_button, make_act_button)
        bot.send_message(message.chat.id,
                         "Список команд:\n1)Проверка материала на наличие в реестре запрещённых материалов - /find ["
                         "name]\n2) "
                         "Проверка списка материалов в реестре на наличие запрещённой литературы - /check"
                         "\n3)Составление акта",
                         reply_markup=organization_markup)
    elif message.text == "Личное пользование":
        person_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        find_button = telebot.types.KeyboardButton("Проверка материала на наличие в реестре запрещённых материалов")
        report_button = telebot.types.KeyboardButton("Отправить жалобу на материал")
        person_markup.add(find_button, report_button)
        bot.send_message(message.chat.id,
                         "Список команд:\n1)Проверка материала на наличие в реестре запрещённых материалов - /find ["
                         "name]\n2)Отправить жалобу на материал - /report [name]",
                         reply_markup=person_markup)
    elif message.text == "1)Проверка материала на наличие в реестре запрещённых материалов":
        bot.send_message(message.chat.id, "Отправьте название")
        bot.register_next_step_handler(message, find_material)
    elif message.text == "2)Проверка списка материалов в реестре на наличие запрещённой литературы":
        bot.send_message(message.chat.id, "Отправьте название")
        bot.register_next_step_handler(message, check_material)
    elif message.text == "3)Составление акта":

        bot.register_next_step_handler(message, make_act)
    elif message.text == "2)Отправить жалобу на материал":
        bot.send_message(message.chat.id, "пишите вашу проблему")
        # берёт описание проблемы
        bot.register_next_step_handler(message, report_material)
    else:
        bot.send_message(message.chat.id, "Непонятная команда /help")


while True:
    try:
        bot.polling(none_stop=True)
    except Exception:
        pass
