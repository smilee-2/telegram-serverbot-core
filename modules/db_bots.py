from  pathlib import Path

cwd = Path.cwd()

# Декоратор для проверки существует ли бот
def validator(func):
    def check(*args, **kwargs):
        with open(cwd / 'data/db_bots/database_bots.txt', 'a+', encoding='utf-8') as file:
            file.seek(0)
            lines = file.readlines()
        for line in lines:
            for arg in args:
                if arg in line.split():
                    raise 'bot detected'
        else:
            func(*args, **kwargs)

    return check

# Добавления бота в БД
@validator
def bots_database(id_chat: str, name: str, api: str, request: str, time: str) -> None:
    if id_chat == '' or name == '' or api == '' or request == '' or time == '':
        raise "bad data"
    try:
        int(time)
        int(name)
    except:
        raise 'time and id_bot is bad'
    with open(cwd / 'data/db_bots/database_bots.txt', 'a+', encoding='utf-8') as file:
        file.writelines(f'{name}|{api}|{id_chat}|{request}|{time}\n')

# Получить имя бота
def get_name(id_bot: int)  -> str:
    with open(cwd / 'data/db_bots/database_bots.txt', 'r', encoding='utf-8') as file:
        word = file.readlines()
    return word[id_bot].split('|')[0]

#Получить api бота
def get_api(id_bot: int)  -> str:
    with open(cwd / 'data/db_bots/database_bots.txt', 'r', encoding='utf-8') as file:
        word = file.readlines()
    return word[id_bot].split('|')[1]

# Получить ид канала
def get_id_chat(id_bot: int)  -> str:
    with open(cwd / 'data/db_bots/database_bots.txt', 'r', encoding='utf-8') as file:
        word = file.readlines()
    return word[id_bot].split('|')[2]

# Получить запрос на тему генерации
def get_request(id_bot: int)  -> str:
    with open(cwd / 'data/db_bots/database_bots.txt', 'r', encoding='utf-8') as file:
        word = file.readlines()
    return word[id_bot].split('|')[3]

# Получить частоту генерации
def get_time(id_bot: int) -> str:
    with open(cwd / 'data/db_bots/database_bots.txt', 'r', encoding='utf-8') as file:
        word = file.readlines()
    return word[id_bot].split('|')[4]

#Получить всю информацию о боте
def get_all_info_one_bot(id_bot: int) -> str:
    with open(cwd / 'data/db_bots/database_bots.txt', 'r', encoding='utf-8') as file:
        word = file.readlines()
    return word[id_bot]

#Получить информацию о всех ботах
def get_all_bots() -> list[str]:
    with open(cwd / 'data/db_bots/database_bots.txt', 'r', encoding='utf-8') as file:
        word = file.readlines()
    return word

# Удалить бота по индексу
def delete_bot(id_bot: int) -> None:
    with open(cwd / 'data/db_bots/database_bots.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        lines.pop(id_bot)
    with open(cwd / 'data/db_bots/database_bots.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines)

