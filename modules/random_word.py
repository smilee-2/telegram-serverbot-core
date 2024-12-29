import random
from http.client import HTTPSConnection
from json import dumps, loads
import os
from  pathlib import Path

cwd = Path.cwd()


API_TOKEN = 'api'

"""
#Класс для создания БД для каждого бота
Методы:
return_list_words - вернет список всех слов
choice_random_word - выберет рандомное слово из списка с помощью api random.org. Если доступ отключен, использует модуль random
add_word - добавит слово в конец БД
delete_last_word - удалит последнее слово из БД
"""
class ListWord:
    def __init__(self, number: int):

        self.number = number
        self._name = cwd / f'data/data{number}.txt'

        with open(f'{self._name}', 'a', encoding='utf-8'):
            pass

    def return_list_words(self):
        with open(f'{self._name}', 'r', encoding='utf-8') as file:
            word = file.readlines()
        return word

    def choice_random_word(self):
        with open(f'{self._name}', 'r', encoding='utf-8') as file:
            word = file.readlines()
            if len(word) < 1:
                raise "base data is zero"
        request_data = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {
            "apiKey": API_TOKEN,
            "n": 1,
            "min": 1,
            "max": len(word)
            },
        "id": 42
        }

        encoded_data = dumps(request_data)

        headers = {
        'Content-Type': 'application/json-rpc',  # Тип запроса
        }
        encoded_headers = dumps(headers)
        try:
            connection = HTTPSConnection('api.random.org')
            connection.request('GET', '/json-rpc/1/invoke', encoded_data, headers)

            response = connection.getresponse()
            response_data = loads(response.read().decode())
        except:
            return random.choices(word)

        return word[response_data['result']['random']['data'][0] - 1]


    def add_word(self, word: str):
        with open(f'{self._name}', 'a+', encoding='utf-8') as file:
            file.seek(0)
            words = file.readlines()
            if word + '\n' in words:
                return -1
            file.seek(2)
            file.writelines(word + '\n')


    def delete_last_word(self):
        with open(f'{self._name}', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            lines = lines[:-1]
        with open(f'{self._name}', 'w', encoding='utf-8') as f:
            f.writelines(lines)



