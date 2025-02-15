from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Words, Users, WordsAndUsers


class Database:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)


    def get_session(self):
        return self.Session()


    def add_initial_words(self, words_list):
            session = self.Session()
            session.add_all(words_list)
            session.commit()
            session.close()

    def add_word(self, name, translation):
        session = self.Session()
        new_word = Words(name=name, translation=translation)
        session.add(new_word)
        session.commit()
        session.refresh(new_word)
        session.close()
        return new_word

    def add_user(self, user_id, name):
        session = self.Session()
        new_user = Users(user_id=str(user_id), name=name)  # Приведение user_id к строке
        session.add(new_user)
        session.commit()
        session.close()


    def get_random_word(self):
        session = self.Session()
        word = session.query(Words).order_by(func.random()).first()  # Извлечение случайного слова
        session.close()
        return word

    def get_user_id(self, tg_user_id):
        session = self.Session()
        user = session.query(Users).filter(Users.user_id == tg_user_id).one_or_none()
        session.close()
        return user.id

    def count_user_words(self, user_id):
        session = self.Session()
        count = session.query(Words).join(WordsAndUsers).filter(WordsAndUsers.id_user == user_id,
                                                                WordsAndUsers.deleted == False).count()
        session.close()
        return count

    def get_user_words(self, user_id, target_word):
        session = self.Session()
        words = session.query(Words).join(WordsAndUsers).filter(WordsAndUsers.id_user == user_id,
                                                                WordsAndUsers.deleted == False,
                                                                Words.name == target_word).one_or_none()
        session.close()
        return words

    def get_user(self, user_id):
        session = self.Session()
        user_id_str = str(user_id)
        user = session.query(Users).filter_by(user_id=user_id_str).first()
        session.close()
        return user

    def get_random_word_from_user(self, user_id):
        session = self.Session()
        word = session.query(Words).join(WordsAndUsers).filter(WordsAndUsers.id_user == user_id,
                                                               WordsAndUsers.deleted == False).order_by(
            func.random()).limit(1).one_or_none()
        session.close()
        return word

    def get_random_words(self, limit=3):
        session = self.Session()
        words = session.query(Words).order_by(func.random()).limit(limit).all()
        session.close()
        return words

    def delete_word(self, word_id, user_id):
        session = self.Session()
        existing_word = session.query(WordsAndUsers).filter(WordsAndUsers.id_word == word_id,
                                                            WordsAndUsers.id_user == user_id).one_or_none()
        if existing_word:
            existing_word.deleted = True
            session.commit()
        session.close()

    def restore_word(self, word_id, user_id):
        session = self.Session()
        existing_word = session.query(WordsAndUsers).filter(WordsAndUsers.id_word == word_id,
                                                            WordsAndUsers.id_user == user_id).one_or_none()
        if existing_word:
            existing_word.deleted = False
            session.commit()
        session.close()

    def add_user_word(self, word_id, user_id):
        session = self.Session()
        existing_users_word = session.query(WordsAndUsers).filter(
            WordsAndUsers.id_word == word_id,
            WordsAndUsers.id_user == user_id).one_or_none()

        if existing_users_word is None:
            new_users_word = WordsAndUsers(
                id_word=word_id,
                id_user=user_id,
                deleted=False
            )
            session.add(new_users_word)
            session.commit()
            session.close()
            return True, None  # Успешно добавлено новое слово
        elif existing_users_word.deleted:
            existing_users_word.deleted = False
            session.commit()
            session.close()
            return True, existing_users_word  # Слово восстановлено
        else:
            session.close()
            return False, existing_users_word  # Слово уже существует
