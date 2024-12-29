import flet as ft
from modules.telegram_module import TelegramBot
from modules import db_bots as db


def main(page: ft.Page):
    # Настройки окна
    page.title = "CoreBot"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = 'light'
    page.window.width = 800
    page.window.height = 600
    page.window.resizable = False
    page.window.maximizable = False

    # Страница с запуском ботов
    def page_home(e):
        page.clean()
        page.add(
            start_generate_btn,
            stop_bot_btn,
        )
        page.update()

    # Страница с созданием нового бота
    def page_settings(e):
        page.clean()
        page.add(
            field_bots,
            create_bot_btn,
        )
        page.update()

    # Страница со всеми ботами
    def page_bots(e):
        page.clean()
        dd_delete_bot.options = [ft.dropdown.Option(str(idx)) for idx in range(1, len(db.get_all_bots()) + 1)]
        db_table_bots.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(word)) for word in lines.split('|')]) for lines in
                              db.get_all_bots()]
        page.add(
            ft.Column([ft.Row([db_table_bots], scroll=ft.ScrollMode.ALWAYS, expand=True)], scroll=ft.ScrollMode.ALWAYS,
                      expand=True),
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.ElevatedButton('Удалить бота', width=160, height=50, on_click=delete_bot),
                            dd_delete_bot
                        ], alignment=ft.MainAxisAlignment.CENTER
                    )
                ]
            )
        )
        page.update()

    # Удаляет ботов из таблицы
    def delete_bot(e):
        try:
            db.delete_bot(int(dd_delete_bot.value) - 1)
            dd_delete_bot.options = [ft.dropdown.Option(str(idx)) for idx in range(1, len(db.get_all_bots()) + 1)]
            db_table_bots.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(word)) for word in lines.split('|')]) for lines in
                                  db.get_all_bots()]
            page.open(dlg_success_delete_bot)
            page.update()
        except:
            page.open(dlg_error_delete_bot)

    # Запускает run функцию для запуском ботов
    def start(e):
        start_generate_btn.disabled = True
        stop_bot_btn.disabled = False
        page.update()
        run_bots(e)
        print("боты запущены")

    #Останавливает потоки для генерация изображений
    def stop(e):
        start_generate_btn.disabled = False
        stop_bot_btn.disabled = True
        page.update()
        stopped_bots(e)
        print("боты остановлены")

    # Запускает ботов в разных потоках
    def run_bots(e):
        bots = db.get_all_bots()
        for i in bots:
            bot = i.split("|")
            try:
                TelegramBot(number=int(bot[0]), api=bot[1], chat_id_bot=bot[2], request=bot[3],
                            time_post=int(bot[4])).run()
            except:
                page.open(dlg_error_start_bots)

    def stopped_bots(e):
        [instance.stop_event_func() for instance in TelegramBot.instance_list]

    # Функция для navigation_bar для переключения между страницами
    def navigation(page_idx: int):
        if page_idx == 0:
            page_home(None)
        elif page_idx == 1:
            page_settings(None)
        elif page_idx == 2:
            page_bots(None)

    # Функция сохранения бота в базу даннх
    def save_bot(e):
        try:
            db.bots_database(
                bot_id_field.value,
                bot_name_field.value,
                bot_api_field.value,
                bot_request_field.value,
                bot_time.value,
            )
            bot_name_field.value = ''
            bot_api_field.value = ''
            bot_id_field.value = ''
            bot_request_field.value = ''
            bot_time.value = ''
            page.open(dlg_create_bot)
            page.update()
        except:
            page.open(dlg_about_error_bot_append)

    # Кнопка для включения ботов
    start_generate_btn = ft.ElevatedButton(
        text="Запустить ботов",
        width=160,
        height=50,
        on_click=start,
    )

    # Кнопка для выключения ботов
    stop_bot_btn = ft.ElevatedButton(
        text="Остановить ботов",
        width=160,
        height=50,
        on_click=stop,
        disabled=True,

    )
    # Таблица ботов
    db_table_bots = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Id_Bot")),
            ft.DataColumn(ft.Text("Api")),
            ft.DataColumn(ft.Text("Id_chat")),
            ft.DataColumn(ft.Text("Request")),
            ft.DataColumn(ft.Text("Time")),
        ],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text(word)) for word in lines.split('|')]) for lines in
            db.get_all_bots()
        ],
    )
    # выпадающий список для удаления
    dd_delete_bot = ft.Dropdown(
        width=150,
        options=[
            ft.dropdown.Option(str(idx)) for idx in range(1, len(db.get_all_bots()) + 1)
        ],
    )

    # Переменная нижнего bar
    navigation_bar_ft = ft.CupertinoNavigationBar(
        bgcolor=ft.Colors.BLACK12,
        inactive_color=ft.Colors.WHITE,
        active_color=ft.Colors.BLUE_600,
        on_change=lambda e: navigation(e.control.selected_index),
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label='Home'),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label='Settings'),
            ft.NavigationBarDestination(icon=ft.Icons.DNS, label='Bots')
        ]
    )
    #переменные dlg вспылающее диалоговое окно
    dlg_about_error_bot_append = ft.AlertDialog(
        title=ft.Text("Одно из полей неправильно введено", size=18),
    )

    dlg_error_start_bots = ft.AlertDialog(
        title=ft.Text("Ошибка запуска ботов", size=18),
    )

    dlg_error_delete_bot = ft.AlertDialog(
        title=ft.Text("Ошибка удаление бота", size=18),
    )

    dlg_success_delete_bot = ft.AlertDialog(
        title=ft.Text("Бот удален", size=18),
    )

    dlg_create_bot = ft.AlertDialog(
        title=ft.Text("Бот создан", size=18),
    )

    # Поля характеристик ботов, id, api, idchanel, request, time_gen
    bot_name_field = ft.TextField(
        label='id Бота',
    )
    bot_api_field = ft.TextField(
        label='Api Token',
    )
    bot_id_field = ft.TextField(
        label='id Канала',
    )
    bot_request_field = ft.TextField(
        label='О чем делать посты',
    )
    bot_time = ft.TextField(
        label='Частота генерации поста в минутах'
    )

    create_bot_btn = ft.ElevatedButton(
        text='Создать бота',
        on_click=save_bot,
        width=160,
        height=50,
    )

    field_bots = ft.Row(
        [
            ft.Column(
                [
                    bot_name_field,
                    bot_api_field,
                    bot_id_field,
                    bot_request_field,
                    bot_time
                ]
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    page.navigation_bar = navigation_bar_ft

    page.add(
        start_generate_btn,
        stop_bot_btn,
    )


if __name__ == "__main__":
    ft.app(target=main)
