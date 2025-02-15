from sqlalchemy import func
import logging
import config
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import telebot
from telebot import types, StateMemoryStorage, custom_filters
import random
from database import Database

from models import create_tables, Words, Users, WordsAndUsers

login = "postgres"
password = "1234"
db_name = "english_teacher_bot_db"
DSN = f'postgresql://{login}:{password}@localhost:5432/{db_name}'
engine = sqlalchemy.create_engine(DSN)

session = Database(engine)

create_tables(engine)
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Session = sessionmaker(bind=engine)
# session = Session()

words = [
    Words(name="Sky", translation="Небо"),
    Words(name="Love", translation="Любовь"),
    Words(name="Blue", translation="Голубой"),
    Words(name="Unicorn", translation="Единорог"),
    Words(name="Elephant", translation="Слон"),
    Words(name="Happiness", translation="Счастье"),
    Words(name="Rainbow", translation="Радуга"),
    Words(name="Family", translation="Семья"),
    Words(name="Cat", translation="Кот"),
    Words(name="Firework", translation="Фейерверк")
]
session.add_initial_words(words)

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(config.TOKEN, state_storage=state_storage)

known_users = []
buttons = []
current_dictionary = "personal"


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['russian_word']}"


class Command:
    ADD_WORD = "Add the word ➕"
    DELETE_WORD = "Delete the word 🗑"
    NEXT = "Next ⏭"
    REPEAT = "Repeat words from personal dictionary 🕐"
    RETURN_BACK = "Back to all words 🔙"


@bot.message_handler(commands=["start"])  # функция для старта бота
def start_bot(message):
    chat_id = message.chat.id
    existing_user = session.get_user(message.from_user.id)
    if existing_user is None:  # добавляем в БД если такого юзера нет
        session.add_user(message.from_user.id, f"{message.from_user.first_name} {message.from_user.last_name}")
        bot.send_message(chat_id, "Hello, stranger, let's study English!")
    else:  # а если знаем такого, то приветствуем по имени
        bot.send_message(chat_id, f"Hello, {message.from_user.first_name}! Let's go on with english words!")

    changing_cards_all(message)


def changing_cards_all(message):  # функция для смены карточек всех существующих слов
    markup = types.ReplyKeyboardMarkup(row_width=2)
    global buttons
    buttons = []
    buttons.clear()
    global current_dictionary
    current_dictionary = "all"

    word = session.get_random_word()
    if word:
        target_word = word.name
        russian_word = word.translation
    else:
        target_word = None
        russian_word = None

    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    other_words_query = session.get_random_words()
    other_words_list = [word.name for word in other_words_query if word.name != target_word]
    if not other_words_list:  # если список почему-то пуст, то захардкодим три слова
        other_words_list = ["Red", "Rabbit", "Queen"]
    other_words_buttons = [types.KeyboardButton(word) for word in
                           other_words_list]

    buttons = [target_word_btn] + other_words_buttons
    random.shuffle(buttons)

    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    repeat_dict = types.KeyboardButton(Command.REPEAT)
    buttons.extend([next_btn, add_word_btn, repeat_dict])

    markup.add(*buttons)

    bot.send_message(message.chat.id, f"Translate the word '{russian_word}'", reply_markup=markup)

    bot.set_state(message.from_user.id, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['already_guessed'] = False
        data['target_word'] = target_word
        data['russian_word'] = russian_word
        data['other_words_list'] = other_words_list
        print(f"changing_cards_all: {data['target_word']}, {data['russian_word']}")


def changing_cards_personal(message):  # функция для смены карточек из личного словаря
    markup = types.ReplyKeyboardMarkup(row_width=2)
    global buttons
    buttons = []
    buttons.clear()
    global current_dictionary
    current_dictionary = "personal"
    current_tg_user_id = str(message.from_user.id)
    user_id = session.get_user_id(current_tg_user_id)
    count_of_words = session.count_user_words(user_id)
    bot.send_message(message.chat.id, f"Count of words is {count_of_words}")
    if count_of_words != 0:
        word = session.get_random_word_from_user(user_id)
        if word:
            target_word = word.name
            russian_word = word.translation
    else:
        bot.send_message(message.chat.id, "Personal dictionary is empty, return to all words and add any")
        return

    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    other_words_query = session.get_random_words()
    while target_word in other_words_query:
        other_words_query = session.get_random_words()
        other_words = [word.name for word in other_words_query if word.name != target_word]
    other_words = other_words_query
    other_words_list = [word.name for word in other_words if word.name != target_word]
    if not other_words_list:  # если список почему-то пуст, то захардкодим три слова
        other_words_list = ["Red", "Rabbit", "Queen"]
    other_words_buttons = [types.KeyboardButton(word) for word in
                           other_words_list]

    buttons = [target_word_btn] + other_words_buttons
    random.shuffle(buttons)

    next_btn = types.KeyboardButton(Command.NEXT)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    return_to_all = types.KeyboardButton(Command.RETURN_BACK)
    buttons.extend([next_btn, delete_word_btn, return_to_all])

    markup.add(*buttons)

    bot.send_message(message.chat.id, f"Translate the word '{russian_word}'", reply_markup=markup)

    bot.set_state(message.from_user.id, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['already_guessed'] = False
        data['target_word'] = target_word
        data['russian_word'] = russian_word
        data['other_words_list'] = other_words
        print(f"changing_cards_personal: {data['target_word']}, {data['russian_word']}")


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    if current_dictionary == "personal":
        changing_cards_personal(message)
    else:
        changing_cards_all(message)


@bot.message_handler(func=lambda message: message.text == Command.REPEAT)
def repeat(message):
    changing_cards_personal(message)


@bot.message_handler(func=lambda message: message.text == Command.RETURN_BACK)
def return_back(message):
    changing_cards_all(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        translation = data['russian_word']
        tg_user_id = str(message.from_user.id)
        user_id = session.get_user_id(tg_user_id)
        print(f"User ID: {user_id}")
        word = session.get_user_words(user_id, target_word=target_word)
        print(word)
        # word_id = word.id
        # existing_users_word = session.delete_word()
        if word:
            print(234254)
            print(f'111, {user_id}')
            print(423456)
            print(f'333, {word.id}')
            session.delete_word(word.id, user_id)
            print(222)
            bot.send_message(message.chat.id, f"The word '{target_word}' deleted.")
        else:
            bot.send_message(message.chat.id, "The word is not inside the dictionary.")


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        print(f"Target word: {target_word}")
        translation = data['russian_word']
        word = session.get_session().query(Words).filter(Words.name == target_word).one_or_none()
        tg_user_id = str(message.from_user.id)
        user_id = session.get_user_id(tg_user_id)
        success, existing_users_word = session.add_user_word(word.id, user_id)

        if success:
            if existing_users_word is None:
                bot.send_message(message.chat.id, f"The word '{word.name}' put inside your personal dictionary! 🎉")
            else:
                bot.send_message(message.chat.id, f"The word '{word.name}' was restored in your dictionary! 🎉")
        else:
            bot.send_message(message.chat.id, f"The word '{word.name}' already exists in your dictionary.")


@bot.message_handler(func=lambda message: True, content_types=["text"])
def message_reply(message):
    hint = "Unknown answer"
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        russian_word = data['russian_word']
        print(f"message_reply123: {data['target_word']}, {data['russian_word']}, {text}")
        if text == Command.ADD_WORD:
            add_word(message)
        elif text == Command.DELETE_WORD:
            delete_word(message)
        if text.lower() == target_word.lower():
            if data.get('already_guessed', True):
                bot.send_message(message.chat.id, "You have already guessed the word. Click 'Next' to change the word.")
                return
            hint = show_target(data)
            hint_text = ["Awesome!❤", hint]
            hint = show_hint(*hint_text)
            data['already_guessed'] = True
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '✅'

        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
            hint = show_hint("Wrong answer!",
                             f"Try again to remember the word 🇷🇺{russian_word}")
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


if __name__ == "__main__":
    print("bot is running!")
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling(skip_pending=True)
