TOKEN = '5433331912:AAE-bWSDpWyYnZB0Sv8NVUqi1FGXVDUdkww'  # bot token from @BotFather


def act_dialog():
    ans = ['Введите ФИО руководителя', "Введите первое ФИО сотрудника", "Введите второе ФИО сотрудника",
           "Введите третье ФИО сотрудника", '']
    yield from ans
