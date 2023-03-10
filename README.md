# Telegram-бот для работы с API Yandex Practicum

### Описание
Telegram-бот обращается к API сервису Я.Практикум.Домашка и узнает статус домашнего задания. Есть три статуса:

- Работа взята на проверку ревьюером,
- Работа проверена: у ревьюера есть замечания,
- Работа проверена: ревьюеру всё понравилось. Ура!

### Что делает бот?

- каждые 10 минут бот отправляет запрос к API-сервису Я.Практикум.Домашка и получает статус отправленного на проверку домашнего задания;
- при обновлении статуса, бот анализирует ответ API и отправляет соответствующее уведомление в ваш Telegram-чат;
- бот логирует свою работу и информирует вас о важных проблемах сообщением в ваш Telegram-чат.

### Куда отправляются запросы?

- Я.Практикум.Домашка - https://practicum.yandex.ru/api/user_api/homework_statuses/ (доступ только по токену)

### Шаблон для файла .env

- PRACTICUM_TOKEN: секретный токен для доступа к Я.Практикуму, который есть только у студентов;
- TELEGRAM_TOKEN: секретный токен вашего Telegram-бота;
- TELEGRAM_CHAT_ID: идентификатор чата, в который вы хотите переслать сообщение о статусе домашнего задания.

### Где можно найти TELEGRAM_CHAT_ID и TELEGRAM_TOKEN?

- TELEGRAM_CHAT_ID: в Telegram найдите @userinfobot, отправьте любое сообщение (или перешлите чье-либо сообщение) и бот ответит вам chat_id;
- TELEGRAM_TOKEN: в Telegram найдите @BotFather, следуя инструкциям создайте собственного бота и запросите секретный токен вашего бота.
## Установка

- Клонировать репозиторий:

   ```python
   git clone https://github.com/JUSTUCKER/Telegram_bot_for_homework.git
   ```

- Перейти в папку с проектом:

   ```python
   cd telegram_bot_for_homework/
   ```

- Создать виртуальное окружение (требуется версия Python >= 3.7):

   ```python
   python -m venv venv
   ```

- Активировать виртуальное окружение:

   ```python
   # для OS Lunix и MacOS
   source venv/bin/activate
   ```

   ```python 
   # для OS Windows
   source venv/Scripts/activate
   ```

- Установить зависимости из файла requirements.txt:

   ```python
   python3 -m pip install --upgrade pip
   ```

   ```python
   pip install -r requirements.txt
   ```

- Зарегистрировать чат-бота в Telegram.

- Создать в корневой директории файл .env для хранения переменных окружения:

   ```python
   PRAKTIKUM_TOKEN = 'xxx'
   TELEGRAM_TOKEN = 'xxx'
   TELEGRAM_CHAT_ID = 'xxx'
   ```

- Запустить проект:

   ```python
   # для OS Lunix и MacOS
   python homework.py
   ```
   ```python
   # для OS Windows
   python3 homework.py
   ```

## Авторы

- [@JUSTUCKER](https://github.com/JUSTUCKER) при помощи [@yandex-praktikum](https://github.com/yandex-praktikum)
