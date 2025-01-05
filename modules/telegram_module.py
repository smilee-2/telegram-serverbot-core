import telebot
import threading
import random
from modules.random_word import ListWord
from modules import gimage
from modules import gpt
import time
from pathlib import Path
import modules.db_bots as db
from queue import Queue

cwd = Path.cwd()
queue_gpt = Queue()

'''
Класс для создания Ботов

'''


class TelegramBot:
    instance_list = []

    def __init__(self,
                 api: str,
                 number: int,
                 request: str = 'Напиши интересный факт из культуры японии',
                 chat_id_bot: str = None,
                 time_post: int = 60
                 ):

        self.api = api
        self.number = number
        self.chat_id_bot = chat_id_bot
        self.time_post = time_post * 60
        self.request = request

        TelegramBot.instance_list.append(self)

        self.words = ListWord(number)
        self.bot = telebot.TeleBot(api, skip_pending=True)
        self.stop_event = threading.Event()


        # Функция генерации постов
        @self.bot.message_handler(commands=['generate'])
        def generate_post(message: telebot.types.Message) -> None:
            print("Проверка запроса на администратора")
            if str(message.from_user.id) not in ['466788660', '863047444']:
                self.bot.send_message(message.chat.id, "Вы не являетесь администратором!")
                return
            print("Проверка завершена")
            if self.chat_id_bot:
                threading.Thread(target=self.generate_post_new_threading, args=(message,), daemon=True).start()


        # Функция добавления слова
        @self.bot.message_handler(commands=['word'])
        def new_word(message: telebot.types.Message) -> None:
            if str(message.from_user.id) not in ['466788660', '863047444']:
                self.bot.send_message(message.chat.id, "Вы не являетесь администратором!")
                return
            msg = self.bot.send_message(message.chat.id, "Напиши слово, которое хочешь добавить")
            self.bot.register_next_step_handler(msg, self.add_new_word_txt)


        # Функция удаления слова
        @self.bot.message_handler(commands=['delete'])
        def delete_word(message: telebot.types.Message) -> None:
            if str(message.from_user.id) not in ['466788660', '863047444']:
                self.bot.send_message(message.chat.id, "Вы не являетесь администратором!")
                return
            self.bot.send_message(message.chat.id, "Слово удалено")
            self.words.delete_last_word()


        # Функция вывода всех слов
        @self.bot.message_handler(commands=['list'])
        def list_words(message: telebot.types.Message) -> None:
            if str(message.from_user.id) not in ['466788660', '863047444']:
                self.bot.send_message(message.chat.id, "Вы не являетесь администратором!")
                return
            temp = self.words.return_list_words()
            self.bot.send_message(message.chat.id, f'{[f'{x + 1} ' + f'{temp[x][:-1]}' for x in range(len(temp))]}')


        @self.bot.message_handler(commands=['delbot'])
        def delete_bot_bd(message: telebot.types.Message) -> None:
            db.delete_bot(-1)
            self.bot.send_message(message.chat.id, 'Бот удален')


        # Функция запроса gpt
        @self.bot.message_handler()
        def generate_answer(message: telebot.types.Message) -> None:
            if str(message.from_user.id) not in ['466788660', '863047444']:
                self.bot.send_message(message.chat.id, "Вы не являетесь администратором!")
                return
            queue_gpt.put(message.text)
            try:
                self.bot.send_message(message.chat.id, f'{gpt.request(queue_gpt.get())}')
            except Exception as error:
                self.bot.send_message(message.chat.id, f'Что-то сломалось( {error}')


    # Функция запускает генерацию постов с частотой self.time в отдельном потоке
    def generate_post_new_threading(self, message: telebot.types.Message) -> None:
        while not self.stop_event.is_set():

            array_photo = []
            media_group = []

            self.bot.send_message(message.chat.id, "Создаю посты")

            print("Начало генерации изображений")

            num_photo = random.randint(3, 5)

            print("Число фото: ", num_photo - 1)

            word = self.words.choice_random_word()
            text = gpt.request(f"{self.request} об {word}")

            for i in range(1, num_photo):
                gimage.generate_image(text, i, self.number)
                array_photo.append(f"images/ImageGen{i}.png")
                media_group.append(
                    telebot.types.InputMediaPhoto(open(cwd / f"images/ImageBot{self.number}/ImageGen{i}.png", 'rb'),
                                                  caption=text if i == 1 else ''))
                print(f"Генерация {i} заверешна!")

            print("Отправка медиа-группы в канал")
            self.bot.send_media_group(chat_id=self.chat_id_bot, media=media_group)
            time.sleep(self.time_post)


    # Запускает бота в отдельном потоке
    def run(self) -> None:
        print(f'{self.number} запустился')
        threading.Thread(target=self.bot.polling, kwargs={'non_stop': True}, daemon=True).start()


    # Добавляет слово в БД
    def add_new_word_txt(self, message: telebot.types.Message) -> None:
        temp = self.words.add_word(message.text)
        if temp == -1:
            self.bot.send_message(message.chat.id, "Такое слово уже есть")
        else:
            self.bot.send_message(message.chat.id, "Слово добавлено")


    # Останавливает генерацию и бота
    def stop_event_func(self) -> None:
        self.bot.stop_polling()
        self.stop_event.set()
