import requests as rq
import sqlite3
from time import sleep
from random import randint


class BotHandler:
    def __init__(self, token):
        self.token = token
        # bot link
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates_json(self, offset=None):
        params = {'timeout': 100, 'offset': offset}
        response = rq.get(self.api_url + 'getUpdates', data=params)
        # print(response.json())
        return response.json()

    def get_last_update(self, update):
        get_result = update['result']

        if len(get_result) == 0:
            self.get_last_update(self.get_updates_json())

        if len(get_result) > 0:
            self.chat_id = get_result[-1]['message']['chat']['id']
            return get_result[-1]
        elif len(get_result) == 1:
            self.chat_id = get_result[len(get_result)]['message']['chat']['id']
            return get_result[len(get_result)]

    def send_message(self, text):
        params = {'chat_id': bot.chat_id, 'text': text}
        response = rq.post(self.api_url + 'sendMessage', data=params)
        return response


class Cinema:
    def table_creation(self):
        # connect to db
        # conn = sqlite3.connect("Cinema_list.db")  # подключаемся к файлу базы данных
        # cursor = conn.cursor()  # создаем курсор для исполнения команд

        self.cursor.execute("""CREATE TABLE Users (
                      user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_name text NOT NULL                       
                    );
                    """)

        self.cursor.execute("""CREATE TABLE Lists (
                              list_id INTEGER PRIMARY KEY AUTOINCREMENT,
                              list_name text NOT NULL,
                              user_name text NOT NULL                         
                            );
                            """)

        self.cursor.execute("""CREATE TABLE Cinema (
                              cinema_id INTEGER PRIMARY KEY AUTOINCREMENT,
                              cinema_name text NOT NULL,
                              list_name text NOT NULL                       
                            );
                            """)

        self.cursor.execute("""CREATE TABLE Relate (
                              relate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                              user_id INTEGER NOT NULL,
                              list_id INTEGER NOT NULL,
                              cinema_id INTEGER NOT NULL                        
                            );
                            """)

        # commit changes in db
        self.conn.commit()  # внесение изменений в файл базу данных и сохранение
        return self.conn

    def add_user(self, _user_name, offset):
        new_user = False
        self.cursor.execute("SELECT * from Users where user_name = ?;", (_user_name,))
        if len(self.cursor.fetchall()) == 0:
            bot.send_message("Are you want to Register?")
            new_user = True
            while True:
                last_update = bot.get_last_update(bot.get_updates_json(offset))
                offset = last_update['update_id'] + 1
                if last_update['message']['text'].lower() in ['yes', 'y', 'да']:
                    self.cursor.execute("INSERT INTO Users(user_name) Values (?);", (_user_name,))
                    break
        bot.send_message(f'Hi, {user_name}!')
        self.cursor.execute(f"SELECT * from Users;")
        res = self.cursor.fetchall()
        print(res)

        if new_user:
            offset = self.add_list(_user_name, offset)

        return offset

    def add_list(self, _user_name, offset):
        bot.send_message("Are you want to add new Cinema list?")
        while True:
            last_update = bot.get_last_update(bot.get_updates_json(offset))
            offset = last_update['update_id'] + 1
            if last_update['message']['text'].lower() in ['yes', 'y', 'да']:
                bot.send_message("Enter List name!")
                while True:
                    last_update = bot.get_last_update(bot.get_updates_json(offset))
                    self.cursor.execute("INSERT INTO Lists (list_name, user_name) Values (?, ?);",
                                        (last_update['message']['text'], _user_name,))
                    break
                break
        self.cursor.execute("SELECT * from Lists where user_name = (?) ;",
                            (_user_name,))
        res = self.cursor.fetchall()
        print(res)
        return offset

    def show(self, _user_name, offset):
        self.cursor.execute("SELECT list_name from Lists where user_name = (?) ;",
                            (_user_name,))
        res = self.cursor.fetchall()
        print(res)

        if len(res) == 0:
            bot.send_message("You have no any list. Want to create?")
            offset = self.add_list(_user_name, offset)
        else:
            text = ""
            for i in res:
                text += f"{i[0]}\n"
            bot.send_message(text)
        return offset

    def select_list(self, _user_name, offset):
        self.show(_user_name, offset)
        bot.send_message("Enter list name:")
        while True:
            last_update = bot.get_last_update(bot.get_updates_json(offset))
            offset = last_update['update_id'] + 1
            self.cursor.execute("SELECT list_name from Lists where user_name = (?) ;",
                                (_user_name,))
            res = self.cursor.fetchall()
            print(res)
            user_input = last_update['message']['text'].lower()
            if user_input in [i[0].lower() for i in res]:
                print(user_input)
                return self.add_film(user_input, offset)

    def add_film(self, list_name, offset):
        bot.send_message("Enter Film name!")
        while True:
            last_update = bot.get_last_update(bot.get_updates_json(offset))
            offset = last_update['update_id'] + 1
            self.cursor.execute("INSERT INTO Cinema(cinema_name, list_name) Values (?, ?);",
                                (last_update['message']['text'], list_name,))
            self.cursor.execute("SELECT cinema_id from Cinema where cinema_name = ? and list_name = ?",
                                (last_update['message']['text'], list_name,))
            cinema_id = self.cursor.fetchall()[0][0]
            print(cinema_id)
            self.cursor.execute("SELECT list_id from Lists where user_name = ? and list_name = ?",
                                (last_update['message']['from']['username'], list_name,))
            list_id = self.cursor.fetchall()[0][0]
            print(list_id)
            self.cursor.execute("SELECT * from Users where user_name = ?;",
                                (last_update['message']['from']['username'],))
            user_id = self.cursor.fetchall()[0][0]
            print(user_id)

            self.cursor.execute("INSERT INTO Relate(user_id, list_id, cinema_id) Values (?, ?, ?);",
                                (user_id, list_id, cinema_id,))

            self.cursor.execute(f"SELECT * from Cinema;")
            res = self.cursor.fetchall()
            print("Cinema:\n", res)
            self.cursor.execute(f"SELECT * from Relate;")
            res = self.cursor.fetchall()
            print(res)
            return offset

    def show_random_film(self, _user_name, offset):
        while True:
            last_update = bot.get_last_update(bot.get_updates_json(offset))
            offset = last_update['update_id'] + 1
            self.cursor.execute("SELECT * from Users where user_name = ?;",
                                (last_update['message']['from']['username'],))
            user_id = self.cursor.fetchall()[0][0]
            self.cursor.execute("SELECT cinema_id from Relate where user_id = ? ;",
                                (user_id,))

            res = self.cursor.fetchall()
            print(res)
            if len(res) != 0:
                output = []
                for i in res:
                    self.cursor.execute("SELECT cinema_name from Cinema where cinema_id = ?;",
                                        (i[0],))
                    output.append(self.cursor.fetchall()[0][0])

                bot.send_message(output[randint(0, len(output)-1)])
            else:
                bot.send_message("You have not added a film =(")
            return offset

    def show_films_from_list(self, user_name, new_offset):
        offset = self.show(user_name, new_offset)
        text = ""

        # self.cursor.execute("SELECT list_id from Lists where user_name = ? and list_name = ?",
                            # (user_name, last_update['message']['from']['username'],))

        # list_id = self.cursor.fetchall()[0][0]
        bot.send_message("Enter list name:")
        while True:
            last_update = bot.get_last_update(bot.get_updates_json(offset+1))
            offset = last_update['update_id'] + 2

            print(last_update['message']['text'])
            self.cursor.execute("SELECT cinema_name from Cinema where list_name = ?;",
                                (last_update['message']['text'],))
            print("Films:")
            res = self.cursor.fetchall()
            print(res)
            if len(res) != 0:
                for i in res:
                    text += i[0] + '\n'
                bot.send_message(text)

            return offset

    def help(self, user_name, new_offset):
        bot.send_message(
            "You can use such commands as: \n /start - for registering \n /add_list - for creating a new list \n \
/show_lists - to overview your lists \n /add_film - for adding a new film to your list \n /random_film - \
for choosing a random film from your lists ")
        offset = last_update['update_id'] + 1
        return offset

    def __init__(self):
        self.conn = sqlite3.connect("Cinema_list.db")  # подключаемся к файлу базы данных
        self.cursor = self.conn.cursor()  # создаем курсор для исполнения команд
        # self.table_creation()


if __name__ == '__main__':
    bot = BotHandler('1825110650:AAGSEfszuu0eWNTxwp3rp2pdh4mblW1-_Ag')
    new_offset = 0
    last_update = bot.get_last_update(bot.get_updates_json(new_offset))
    new_session = Cinema()

    while True:
        last_update = bot.get_last_update(bot.get_updates_json(new_offset))

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']

        user_name = last_update['message']['from']['username']
        if last_chat_text == '/start':
            new_offset = new_session.add_user(user_name, new_offset)
        elif last_chat_text == '/add_list':
            new_offset = new_session.add_list(user_name, new_offset)
        elif last_chat_text == '/show_lists':
            new_offset = new_session.show(user_name, new_offset)
        elif last_chat_text == '/add_film':
            new_offset = new_session.select_list(user_name, new_offset)
        elif last_chat_text == '/random_film':
            new_offset = new_session.show_random_film(user_name, new_offset)
        elif last_chat_text == '/help':
            new_offset = new_session.help(user_name, new_offset)
        elif last_chat_text == '/show_films_from_list':
            new_offset = new_session.show_films_from_list(user_name, new_offset)

        print(last_update)
        new_offset = last_update_id + 1
        sleep(1)
