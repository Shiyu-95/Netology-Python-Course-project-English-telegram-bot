import sqlalchemy as sql
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

'''
нужно 3 таблицы: все слова (айди, название, перевод), персональные слова (айди, название, перевод, удалено), 
юзеры (айди, тг айди, имя), слова_и_юзеры(айди юзера, айди слова)

'''


class Words(Base):
    __tablename__ = "words"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(length=60))
    translation = sql.Column(sql.String(length=60))


class Users(Base):
    __tablename__ = "users"

    id = sql.Column(sql.Integer, primary_key=True)
    user_id = sql.Column(sql.VARCHAR(255), unique=True)
    name = sql.Column(sql.String(length=100))


class WordsAndUsers(Base):
    __tablename__ = "words_and_users"

    id = sql.Column(sql.Integer, primary_key=True)
    id_word = sql.Column(sql.Integer, sql.ForeignKey("words.id"), nullable=False)
    id_user = sql.Column(sql.Integer, sql.ForeignKey("users.id"), nullable=False)
    deleted = sql.Column(sql.Boolean, default=False)

    word = relationship(Words, backref="user_words")
    book = relationship(Users, backref="user_words")


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
