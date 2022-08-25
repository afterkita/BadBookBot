import os
import telebot
import config
from use_db import make_user, get_book, get_books, get_my_books, get_users
from create_report import make_template_report
from create_act import make_template
from update_db import update_db
from multiprocessing import *
import time

bot = telebot.TeleBot(config.TOKEN)
users = {}

BAD_BOOKS = get_books()

MARCUP = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
find_button = telebot.types.KeyboardButton("Поиск")
check_button = telebot.types.KeyboardButton("Анализ")
report_button = telebot.types.KeyboardButton("Обращение")
info_button = telebot.types.KeyboardButton("Инфо")
education_button = telebot.types.KeyboardButton("Просвещение")
defense_button = telebot.types.KeyboardButton("Защита прав")
MARCUP.add(find_button, check_button, report_button, info_button, education_button, defense_button)

EmptyMarcup = telebot.types.ReplyKeyboardMarkup()


def proc_start():
    p_to_start = Process(target=start_schedule, args=(id,))
    p_to_start.start()
    return p_to_start


def start_schedule(id):
    while True:
        status = update_db()
        if status:
            for i in get_users():
                bot.send_message(i, "Реестр обновился, проведите анализ библиотеки!")
        time.sleep(60 * 60 * 24)


@bot.message_handler(commands=['start'])
def start_dialog(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    organization_button = telebot.types.KeyboardButton('Организация')
    user_button = telebot.types.KeyboardButton('Личное пользование')
    markup.add(organization_button, user_button)

    make_user(message.chat.id, message.from_user.username)

    bot.send_message(message.chat.id,
                     'Привет, я телеграм-бот BadBookBot, который проверяет различные материалы на наличие их в Федеральном реестре экстремистских материалов',
                     reply_markup=markup)
    bot.send_message(message.chat.id,
                     'Для мониторинга наличия экстремистских книг в фонде библиотеки - нажмите Организация.\nДля '
                     'поиска информации в реестре в личных или коммерческих целях - нажмите Личное пользование',
                     reply_markup=markup)


def act_choose(message):
    if message.text.split()[0].lower() == "нет":
        users[message.chat.id] = [config.act_dialog(), []]
        bot.register_next_step_handler(bot.send_message(message.chat.id,
                                                        "Пришлите текстовый файл с перечнем литературы, содержащейся в фонде вашей библиотеке",
                                                        reply_markup=telebot.types.ReplyKeyboardRemove()), get_doc)
    elif message.text.split()[0].lower() == "да":
        users[message.chat.id][1].append(message.chat.id)
        src = make_template(*users[message.chat.id][1])

        with open(src, 'rb') as f:
            bot.send_message(message.chat.id,
                             "Для вас подготовлен акт о наличии в фонде библиотеки экстремистских материалов. Поместите указанный документ в отдельное помещение или шкаф с замком, специально выделенное помещение для хранения подобных документов.")
            bot.send_document(message.chat.id, document=f, reply_markup=MARCUP)
            f.close()
            os.remove(src)
        return
    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, "Выберите Да или Нет"), act_choose)


def make_act(message):
    w = next(users[message.chat.id][0])
    users[message.chat.id][1].append(message.text)
    if w == '':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        yes_button = telebot.types.KeyboardButton("Да")
        no_button = telebot.types.KeyboardButton("Нет")
        markup.add(yes_button, no_button)

        bot.send_message(message.chat.id, "Проверка данных:")

        bot.send_message(message.chat.id, "\nФИО руководителя - {}\nФИО первого сотрудника - {}\nФИО второго "
                                          "сотрудника - {}\nФИО третьего сотрудника - {}".format(
            users[message.chat.id][1][1], users[message.chat.id][1][2], users[message.chat.id][1][3],
            users[message.chat.id][1][4]))

        bot.send_message(message.chat.id, "Все правильно?", reply_markup=markup)
        bot.register_next_step_handler(message, act_choose)

    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, w), make_act)


def get_education_information(message):
    bot.send_message(message.chat.id,
                     "<b>Ответственность за хранение экстремистских материалов</b>\nЗа хранение экстремистских "
                     "материалов в целях массового распространения "
                     "существует административная ответственность, для граждан штраф от 1 до 3 тысяч "
                     "рублей или арест на срок до 15 суток. Для юридических лиц штраф от ста тысяч до "
                     "одного миллиона рублей или приостановление деятельности на срок до девяноста "
                     "суток (ст. 20.29 КоАП РФ).", parse_mode="HTML")
    bot.send_message(message.chat.id,
                     "\n<b>Что понимают под экстремистскими материалами</b>\nПод экстремистскими материалами "
                     "понимаются "
                     "предназначенные для обнародования\n- документы либо информация на иных "
                     "носителях, призывающие к осуществлению экстремистской деятельности либо "
                     "обосновывающие или оправдывающие необходимость осуществления такой "
                     "деятельност\n- труды руководителей национал-социалистической рабочей партии "
                     "Германии, фашистской партии Италии,\n- публикации, обосновывающие либо "
                     "оправдывающие национальное и (или) расовое превосходство либо оправдывающие "
                     "практику совершения военных или иных преступлений, направленных на полное или "
                     "частичное уничтожение какой-либо этнической, социальной, расовой, национальной "
                     "или религиозной группы\n", parse_mode="HTML")
    bot.send_message(message.chat.id,
                     "<b>Как литература становится экстремистским материалом</b>\nЛитературу признают экстремистским материалом "
                     "федеральным судом по месту их обнаружения, распространения или нахождения "
                     "организации, осуществившей производство таких материалов, на основании "
                     "заявления прокурора или при производстве по соответствующему делу об "
                     "административном правонарушении, гражданскому или уголовному делу. Одновременно "
                     "с решением о признании информационных материалов экстремистскими судом "
                     "принимается решение об их конфискации. Копия вступившего в законную силу "
                     "решения о признании информационных материалов экстремистскими направляется "
                     "судом в трехдневный срок в Минюст. Минюст добавляет информацию в Федеральный "
                     "список экстремистских материалов\nПо данным Судебного Департамента при "
                     "Верховном Суде Российской Федерации судами общей юрисдикции за 2021 год "
                     "рассмотрено 1519 дел по ст. 20.29 КоАП РФ «Производство и распространение "
                     "экстремистских материалов», назначено наказание 1319 лицам (6 юридическим "
                     "лицам, 15 должностным лицам, 1 292 физическим лицам)\n", parse_mode="HTML")
    bot.send_message(message.chat.id, "<b>Правила работы с экстремистскими материалами</b>\nЕсли Вы обнаружили в "
                                      "библиотечном фонде экстремистский материал, то Вам необходимо:\n1. Маркировать "
                                      "издание. Наклейте на обложку этикетку с восклицательным знаком или любой другой "
                                      "символикой, которая будет указывать на запрет распространения данного "
                                      "документа. Важно, чтобы эту маркировку знали и понимали все сотрудники "
                                      "библиотеки.\n2. Составить Акт о наличии в библиотеке издания, включенного в "
                                      "федеральный список экстремистских материалов.\n3. Выделить для хранения "
                                      "специальное место. Это может быть отдельное помещение, закрытый стеллаж, "
                                      "шкаф с замком, где будут размещаться документы, включенные в Список.\n4. "
                                      "Назначить ответственного за хранение и движение этих документов приказом по "
                                      "библиотеке.\n5. Запретить доступ к фонду экстремистских материалов всем, "
                                      "кто в этом приказе не упомянут.\n6. Составить опись документов, хранящихся в "
                                      "выделенном фонде, и проверять, на месте ли они, один раз в год.",
                     parse_mode="HTML")


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
            bot.send_message(message.chat.id, "Найдены совпадения. Начинаю составлять акт о наличии в библиотеке "
                                              "издания, включенного в ФСЭМ, в соответствии с пунктом 3.1 Рекомендаций "
                                              "по работе библиотек с документами \"УТВ. МИНКУЛЬТ РФ от 12.09.2017 "
                                              "г.\" Мне необходимо будет знать ФИО вашего руководителя и трёх сотрудников, включая вас, которые будут подписывать акт")
            users[message.chat.id][1].append(bad_books_in_my_collection)

            bot.register_next_step_handler(
                bot.send_message(message.chat.id, next(users[message.chat.id][0])), make_act)
        else:
            bot.send_message(message.chat.id,
                             "Совпадения не обнаружены. В вашем фонде отсутствуют экстремистские материалы. Не забудьте провести новую проверку после получения уведомления о включении новых книг в реестр",
                             reply_markup=MARCUP)
    except Exception:
        bot.send_message(message.from_user.id, "Не получилось открыть данный файл", reply_markup=MARCUP)


def report_choose(message):
    if message.text.split()[0].lower() == "нет":
        bot.send_message(message.chat.id, "Начнём заново", reply_markup=telebot.types.ReplyKeyboardRemove())
        users[message.chat.id] = [config.act_dialog_report(), []]
        bot.register_next_step_handler(bot.send_message(message.chat.id, next(users[message.chat.id][0])), make_report)
    elif message.text.split()[0].lower() == "да":
        users[message.chat.id][1].append(message.chat.id)
        src = make_template_report(*users[message.chat.id][1])

        with open(src, 'rb') as f:
            bot.send_message(message.chat.id,
                             "Пожалуйста, распечатайте прикреплённый файл, в шапке обращения укажите ФИО прокурора города и не забудьте поставить свою подпись")
            bot.send_document(message.chat.id, document=f, reply_markup=MARCUP)
            f.close()
            os.remove(src)
        return
    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, "Выберите: Да или Нет"), report_choose)


def make_report(message):
    w = next(users[message.chat.id][0])
    users[message.chat.id][1].append(message.text)
    if w == '':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        yes_button = telebot.types.KeyboardButton("Да")
        no_button = telebot.types.KeyboardButton("Нет")
        markup.add(yes_button, no_button)

        bot.send_message(message.chat.id, "Проверка данных:")
        bot.send_message(message.chat.id, "\nваше ФИО это {}\nваш адрес - {}\nваш номер телефона - {}\nваша почта - {}"
                                          "\nНазвание книги - {}\nФИО автора книги - {}".format(
            *users[message.chat.id][1]))

        bot.send_message(message.chat.id, "Все правильно?", reply_markup=markup)
        bot.register_next_step_handler(message, report_choose)

    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, w), make_report)


def defense(message):
    keybord = telebot.types.InlineKeyboardMarkup()
    url = telebot.types.InlineKeyboardButton('Url', url="http://hack.botman.one/player/kant2022-team2/question")
    keybord.add(url)
    bot.send_message(message.chat.id, "Если в отношении Вас вынесено постановление о привлечении к "
                                      "административной ответственности или составлен протокол об "
                                      "административном правонарушении, то Вы можете воспользоваться нашим "
                                      "сервисом для защиты своих прав. С Вами свяжутся специалисты юридической "
                                      "фирмы «It-бебан».", reply_markup=keybord)


def find_material(message):
    result = get_book(message.text.strip())
    if result:
        bot.send_message(message.chat.id, result, reply_markup=MARCUP)
    else:
        bot.send_message(message.chat.id,
                         "В Федеральном реестре экстремистских материалов информация об этом источнике отсутствует",
                         reply_markup=MARCUP)


@bot.message_handler(commands=['defense'])
def get_botman(message):
    defense(message)


@bot.message_handler(commands=['find'])
def find_handler(message):
    if len(message.text.split()) == 1:
        bot.send_message(message.chat.id, "Отправьте название книги")
        bot.register_next_step_handler(message, find_material)
        return
    name = message.text.strip()[6:]
    result = get_book(name)
    if result:
        bot.send_message(message.chat.id, result, reply_markup=MARCUP)
    else:
        bot.send_message(message.chat.id, "В Федеральном реестре экстремистских материалов информация об этом источнике отсутствует", reply_markup=MARCUP)


@bot.message_handler(commands=['check'])
def check_handler(message):
    users[message.chat.id] = [config.act_dialog(), []]
    # проведена проверка и вызов функции формировании акта

    bot.register_next_step_handler(bot.send_message(message.chat.id,
                                                    "Пришлите текстовый файл с перечнем литературы, содержащейся в фонде вашей библиотеке",
                                                    reply_markup=telebot.types.ReplyKeyboardRemove()), get_doc)


@bot.message_handler(commands=['report'])
def report_handler(message):
    users[message.chat.id] = [config.act_dialog_report(), []]
    bot.register_next_step_handler(bot.send_message(message.chat.id, next(users[message.chat.id][0])), make_report)


@bot.message_handler(commands=['info'])
def information_bot(message):
    bot.send_message(message.chat.id, "Привет, я <b>BadBookBot</b>, первый телеграм-бот, помогающий с проблемными книгами.",parse_mode="HTML")
    bot.send_message(message.chat.id,
                     "Я лëгок в использовании и позволяю автоматизировать нудную работу по поиску книг в федеральный список экстремистских материалов")
    bot.send_message(message.chat.id,"\n<b>Весь список команд:</b>\n1) Получить информацию о боте - /info "
                     "\n2) Проверка материала на наличие в реестре запрещённых материалов - /find [name]"
                     "\n3) Проверка списка материалов в реестре на наличие запрещённой литературы - /check"
                     "\n4) Отправить жалобу на материал - /report"
                     "\n5) Обжалование постановлений о назначении административного штрафа или протокола о привлечении к административной ответственности - /defense"
                     "\n6) Просвещение - /education",parse_mode="HTML")
    bot.send_message(message.chat.id, "Моя работа как чат-бота построена на следующей правовой базе:"
                                      "\nФедеральный закон от 25.07.2002 № 114-ФЗ \"О противодействии экстремистской деятельности\""
                                      "\nФедеральный закон от 29 декабря 1994 г. № 78-ФЗ \"О библиотечном деле\" Кодекс Российской Федерации об административных правонарушениях от 30.12.2001 № 195-ФЗ (ред. от 14.07.2022)\""
                                      "\nУказ Президента Российской Федерации от 29.05.2020 г. № 344 «Об утверждении Стратегии противодействия экстремизму в Российской Федерации до 2025 года»"
                                      "\nПриказ Минюста России от 11.12.2015 № 289 (ред. от 24.11.2016) \"О порядке ведения федерального списка экстремистских материалов\""
                                      "\nРекомендации по работе библиотек с документами, включенными в федеральный список экстремистских материалов (утв. Минкультуры России 12.09.2017)")


@bot.message_handler(commands=['education'])
def education(message):
    bot.register_next_step_handler(message, get_education_information)


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id,
                     "Список команд:\n1) Получить информацию о боте - /info "
                     "\n2) Проверка материала на наличие в реестре запрещённых материалов - /find [name]"
                     "\n3) Проверка списка материалов в реестре на наличие запрещённой литературы - /check"
                     "\n4) Отправить жалобу на материал - /report"
                     "\n5) Обжалование постановлений о назначении административного штрафа или протокола о привлечении к административной ответственности - /defense"
                     "\n6) Просвещение - /education",
                     reply_markup=MARCUP)


@bot.message_handler(content_types=["text"])
def work(message):
    if message.text == "Организация":
        bot.send_message(message.chat.id,
                         "Список команд:\n1) Проверка конкретной книги на наличие её в Федеральном реестре экстремистских материалов - /find ["
                         "name]\n2) "
                         "Выявление экстремистских материалов в фонде библиотеки и составление акта об обнаружении - /check",
                         reply_markup=MARCUP)
    elif message.text == "Личное пользование":
        bot.send_message(message.chat.id,
                         "Список команд:\n1) Проверка конкретной книги на наличие её в Федеральном реестре экстремистских материалов - /find ["
                         "name]\n2) Составление обращения в органы прокуратуры о проверке книги на наличие экстремистского материала - /report"
                         "\n3) Обжалование постановлений о назначении административного штрафа или протокола о привлечении к административной ответственности - /defense",
                         reply_markup=MARCUP)
    elif message.text == "Поиск":
        bot.send_message(message.chat.id, "Отправьте название", reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, find_material)
    elif message.text == "Анализ":
        check_handler(message)
    elif message.text == "Обращение":
        bot.send_message(message.chat.id, "Начинаю составлять обращение. Мне нужно немного больше информации")
        users[message.chat.id] = [config.act_dialog_report(), []]
        bot.register_next_step_handler(bot.send_message(message.chat.id, next(users[message.chat.id][0]),
                                                        reply_markup=telebot.types.ReplyKeyboardRemove()), make_report)
    elif message.text == "Инфо":
        information_bot(message)
    elif message.text == "Просвещение":
        get_education_information(message)
    elif message.text == "Защита прав":
        defense(message)
    else:
        bot.send_message(message.chat.id, "Непонятная команда. Используйте /help",
                         reply_markup=MARCUP)


if __name__ == '__main__':
    while True:
        pr = proc_start()
        try:
            bot.polling(none_stop=True)
        except Exception:
            pass
