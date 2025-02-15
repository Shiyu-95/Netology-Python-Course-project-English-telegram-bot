Для ввода токена используйте файл конфигурации или просто вставьте свой токен в переменную bot вместо config.TOKEN
Бот первый раз приветствует безлично, со второго раза по имени из телеграмма
Изначально запускается список из всех слов, после добавления хоть одного слова можно перейти в режим повторения добавленных слов, из этого режима можно выйти обратно в режим всех слов
Слова можно добавить в личный словарь и удалить, в режиме словаря добавлять нельзя

**English Teacher Bot**
**Описание**
English Teacher Bot — это бот, созданный для обучения английскому языку с использованием карточек слов.

**Основные функции**
Добавление слов и их переводов в базу данных.
Показ случайных слов для перевода.
Проверка знаний пользователя.

**Архитектура**
**Бот использует:**
SQLAlchemy для работы с базой данных.
Telebot для работы с Telegram API.
Структура проекта
main.py: основной файл с логикой бота.
database.py: модуль для работы с базой данных.
models.py: модели базы данных.

**Взаимодействие с ботом
Команды**
/start: Запускает бота и приветствует пользователя.
"Add the word ➕": Начинает процесс добавления нового слова.
"Next ⏭": Переходит к следующему слову.
"Repeat words from personal dictionary 🕐": Повторяет слова из личного словаря пользователя.
"Delete the word 🗑": Удаляет текущее слово из личного словаря.

**Порядок действий пользователя**
Запустите бота, отправив команду /start.
Выберите опцию для добавления слова или другую команду.
Следуйте инструкциям бота для выполнения операций.

**Использование**
Убедитесь, что у вас установлены необходимые библиотеки:
pip install sqlalchemy telebot
Запустите main.py для старта бота.
