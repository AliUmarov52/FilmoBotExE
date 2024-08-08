import sqlite3
from telebot import TeleBot, types
import random

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
bot = TeleBot('YOUR_CODE')

def create_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY
    )
    ''')
    conn.commit()
    conn.close()  # Закрываем соединение

# Добавление пользователя в базу данных
def add_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()  # Закрываем соединение

answers = "Перепроверь ещё раз свой запрос"  # Сообщение в случае неправильной команды

menu = "Вот вы и в главном меню"

@bot.message_handler(commands=["start"])
def welcome(message):                       # Функция welcome и главные кнопки меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) # Какая-то фишка для работы кнопок                
    button1 = types.KeyboardButton('Поиск по жанрам')
    button2 = types.KeyboardButton('Поиск по коду')
    button3 = types.KeyboardButton('ТГК с фильмами')
    button5 = types.KeyboardButton('Настройки')           # Вывод кнопок на экран пользователю
    markup.row(button1, button2, button3)
    markup.row(button5)
    user_id = message.from_user.id
    add_user(user_id)

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nМеня зовут ФИЛЬМОБОТ и я твой проводник в мир кино и сериалов :)\nДля начала выбери способ поиска фильма в меню ниже: ', reply_markup=markup)
    
@bot.message_handler(func=lambda message: message.text == 'Главное меню')
def return_to_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Поиск по жанрам')
    button2 = types.KeyboardButton('Поиск по коду')
    button3 = types.KeyboardButton('ТГК с фильмами')
    button5 = types.KeyboardButton('Настройки')

    markup.row(button1, button2, button3)
    markup.row(button5)  # Главные кнопки меню

    bot.send_message(message.chat.id, 'Вы вернулись в главное меню. Пожалуйста, выберите опцию ниже:', reply_markup=markup)

@bot.message_handler(commands=['users_admin'])
def list_users(message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users')
    users = cursor.fetchall()
    conn.close()  # Закрываем соединение
    user_ids = [str(user[0]) for user in users]
    bot.send_message(message.chat.id, "Список пользователей:\n" + "\n".join(user_ids))


@bot.message_handler()
def info(message):
    if message.text == 'Поиск по коду':
        bot.send_message(message.chat.id, "Введите номер фильма:")
        bot.register_next_step_handler(message, search)
    elif message.text == 'ТГК с фильмами':
        tgk(message)  # Регистрируем следующий шаг
    elif message.text == 'Настройки':
        settings(message)
    elif message.text == 'Поиск по жанрам':
        bot.send_message(message.chat.id, "Введите жанр фильма:\n\nP.s Вводите жанр правильно\n\nДоступные жанры: Драма, Ужасы, Фантастика, Комедия, Романтика")
        bot.register_next_step_handler(message, searchGenre)
    elif message.text == '↩️ Назад в меню':
        return_to_main_menu(message)
    else:
        bot.send_message(message.chat.id, answers)


my_dict = {
    1: {
        "Название": "Интерстеллар",
        "Описание": "Космическая одиссея о группе астронавтов, которые исследуют червоточину в поисках нового дома для человечества.",
        "Ссылка": "https://www.imdb.com/title/tt0816692/",
        "Жанр": "Фантастика"
    },
    2: {
        "Название": "Начало",
        "Описание": "Вор, специализирующийся на краже идей, получает задание внедриться в сознание человека и изменить его мысли.",
        "Ссылка": "https://www.imdb.com/title/tt1375666/",
        "Жанр": "Фантастика"
    },
    3: {
        "Название": "Матрица",
        "Описание": "Программист Нейо узнает о правде о своей реальности и о том, что он может изменить мир.",
        "Ссылка": "https://www.imdb.com/title/tt0133093/",
        "Жанр": "Фантастика"
    },
    4: {
        "Название": "Побег из Шоушенка",
        "Описание": "История о дружбе двух заключенных, которые пытаются сбежать из тюрьмы Шоушенк.",
        "Ссылка": "https://www.imdb.com/title/tt0111161/",
        "Жанр": "Драма"
    },
    5: {
        "Название": "Сияние",
        "Описание": "Писатель с семьей становится смотрителем у отеля, где начинают происходить странные события.",
        "Ссылка": "https://www.imdb.com/title/tt0081505/",
        "Жанр": "Ужасы"
    }, 
    6: {
        "Название": "Тупой и еще тупее",
        "Описание": "После того, как женщина оставляет портфель в терминале аэропорта, тупой водитель лимузина и его еще более тупой друг отправляются в веселую поездку по пересеченной местности в Аспен, чтобы вернуть его.",
        "Ссылка": "https://www.imdb.com/title/tt0109686/?ref_=ls_t_1",
        "Жанр" : "Комедия"
    },
    7: {
        "Название": "Красавица и чудовище",
        "Описание": "Принц, обреченный провести свои дни в образе отвратительного монстра, намеревается вернуть себе человечность, завоевав любовь молодой женщины.",
        "Ссылка": "https://www.imdb.com/title/tt0101414/?ref_=ls_t_5",
        "Жанр": "Романтика"
    },
    8: {
        "Название": "Звонок",
        "Описание": "Журналист должен расследовать загадочную видеозапись, которая, по-видимому, может стать причиной смерти любого человека через неделю или день после ее просмотра.",
        "Ссылка": "https://www.imdb.com/title/tt0298130/",
        "Жанр": "Ужасы"
    },
    9: {"Название": "Кошмар на улице Вязов",
        "Описание": "Подростку Нэнси Томпсон предстоит раскрыть темную правду, которую скрывают ее родители, после того, как она и ее друзья во сне становятся мишенью для духа серийного убийцы с перчаткой с лезвиями, в котором, если они умрут, он убьет их в реальной жизни.",
        "Ссылка": "https://www.imdb.com/title/tt0087800/?ref_=nv_sr_srsg_0_tt_8_nm_0_in_0_q_%25D0%259A%25D0%25BE%25D1%2588%25D0%25BC%25D0%25B0%25D1%2580%2520%25D0%25BD%25",
        "Жанр": "Ужасы"
    },
    10: {"Название": "Крик",
        "Описание": "Через год после убийства своей матери девочка-подросток подвергается террору со стороны убийцы в маске, который нападает на нее и ее друзей, используя устрашающие действия как часть смертельной игры.",
        "Ссылка": "https://www.imdb.com/title/tt0117571/?ref_=nv_sr_srsg_0_tt_8_nm_0_in_0_q_%25D0%259A%25D1%2580%25D0%25B8%25D0%25BA",
        "Жанр": "Ужасы"
    },
    11: {"Название": "Шпион по соседству",
        "Описание": "Бывший агент ЦРУ, Боб Хо, берется за самое сложное на сегодняшний день задание: присматривать за тремя детьми своей девушки, но все меняется, когда русский террорист нацеливается на семью",
        "Ссылка": "https://www.imdb.com/title/tt1273678/?ref_=nv_sr_srsg_0_tt_2_nm_0_in_0_q_%25D0%25A8%25D0%25BF%25D0%25B8%25D0%25BE%25D0%25BD%2520%25D0%25BF%25D0%25BE%25",
        "Жанр": "Комедия"
    },
    12: {"Название": "Полтора шпиона",
        "Описание": "После того, как он восстановил связь с неловким приятелем из старшей школы через Facebook, скромный бухгалтер оказывается втянутым в мир международного шпионажа.",
        "Ссылка": "https://www.imdb.com/title/tt1489889/?ref_=nv_sr_srsg_0_tt_1_nm_0_in_0_q_%25D0%25BF%25D0%25BE%25D0%25BB%25D1%2582%25D0%25BE%25D1%2580%25D0%25B0%2520%25",
        "Жанр": "Комедия"
    },
    13: {"Название": "Не грози южному централу, попивая сок у себя в квартале",
        "Описание": " Парень по кличке Пепельница переезжает в Южный Централ к своему отцу, чтобы стать настоящим мужчиной. Правда, папа младше сына на два года. Вскоре к «Пепельнице» приходит его кузен-гангстер Лок Дог — он учит героя основам жизни на улице.",
        "Ссылка": "https://www.imdb.com/title/tt0116126/",
        "Жанр": "Комедия"
    },
    14: {"Название": "Один дома",
        "Описание": "Многодетная семья МакКалистеров улетает на Рождество в Париж без восьмилетнего сына Кевина — забыли про него в суматохе. Мальчик остается один в пустом доме и начинает наслаждаться жизнью без контроля родителей. Однако в этот дом задумали проникнуть грабители.",
        "Ссылка": "https://www.imdb.com/title/tt0099785/",
        "Жанр": "Комедия"
    },
    15: {"Название": "Большой Лебовски",
        "Описание": "Однажды в дом Джеффа «Чувака» Лебовски вламываются гангстеры. Они принимают героя за миллионера-однофамильца, угрозами требуют вернуть долг и портят ковер. Настоящий миллионер Лебовски отказывается компенсировать потери Чувака, но просит об одолжении — передать выкуп похитителям его жены.",
        "Ссылка": "https://www.imdb.com/title/tt0118715/?ref_=fn_al_tt_1",
        "Жанр": "Комедия"
    },
    16: {"Название": "1+1",
        "Описание": "После того, как он стал полностью парализованным из-за несчастного случая во время полета на параплане, аристократ нанимает человека из пригорода в качестве своего опекуна.",
        "Ссылка": "https://www.imdb.com/title/tt1675434/",
        "Жанр": "Драма"
    },
    17: {"Название": "Джанго освобожденный",
        "Описание": "С помощью немецкого охотника за головами освобожденный раб отправляется спасти свою жену от жестокого владельца плантации в Миссисипи.",
        "Ссылка": "https://www.imdb.com/title/tt1853728/",
        "Жанр": "Вестерн"
    }
}
def search(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('↩️ Назад в меню')
    markup.row(button1)
    
    try:
        n = int(message.text)  # Получаем число из сообщения
        
        if n in my_dict:
            movie = my_dict[n]
            response = f"Название: {movie['Название']}\n\nОписание: {movie['Описание']}\n\nСсылка: {movie['Ссылка']}"
            bot.send_message(message.chat.id, response, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Фильм не найден. Пожалуйста, попробуйте другой номер.", reply_markup=markup)

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное числовое значение.")

def searchGenre(message): 
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('↩️ Назад в меню')
    markup.row(button1)

    # Маппинг жанров на их названия
    genre_map = {
        'Фантастика': "Фантастика",
        'Драма': "Драма",
        'Ужасы': "Ужасы",
        'Комедия': "Комедия",
        'Романтика': "Романтика",
        'Вестерн': "Вестерн"
    }

    genre_key = message.text.capitalize()  # Приводим текст сообщения к корректному формату
    response = ""

    if genre_key in genre_map:
        genre_name = genre_map[genre_key]
        response += f"Фильмы в жанре '{genre_name}':\n"
        found = False
        random_film = False     #Флажок, проверяющий, что рандомный фильм выбрался 
        
        while not random_film:
            random_value = random.randint(0, 5)
            for movie in my_dict.values():
                if movie["Жанр"] == genre_name and random_value == 5:
                    response += f"- {movie['Название']}: {movie['Описание']}\n\nСсылка: {movie['Ссылка']}\n"
                    found = True
                    random_film = True
        
        # Проверяем, были ли найдены фильмы
        if not found:
            response = f"Фильмы в жанре '{genre_name}' не найдены."

    else:
        response = "Пожалуйста, выберите другой жанр."

    bot.send_message(message.chat.id, response, reply_markup=markup)



def tgk(message):
    # Тут оставим ссылку на наш приватный тг канал
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("↩️ Назад в меню")
    markup.row(button1)

    bot.send_message(message.chat.id, 'Подпишись -> https://t.me/+DJTaOu_I6q9jMGVi', reply_markup=markup)


def settings(message):
    # Если хочешь, то дополни настройки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("↩️ Назад в меню")
    markup.row(button1)
    bot.send_message(message.chat.id, 'О проблемах писать -> @jansavitskiy', reply_markup=markup)

# Создаем базу данных при запуске бота
create_database()

# Запуск бота
bot.polling(none_stop=True)
