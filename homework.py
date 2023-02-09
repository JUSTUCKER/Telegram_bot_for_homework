import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format=(
        '%(asctime)s, %(levelname)s, %(pathname)s, %(filename)s '
        '%(funcName)s, %(lineno)d, %(message)s'
    ),
    handlers=[
        logging.FileHandler('program.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка доступности переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except telegram.error.TelegramError as error:
        error_message = f'Не удалось отправить сообщение: {error}:'
        logging.error(error_message)
        raise exceptions.TelegramError(error_message)
    else:
        logging.debug('Сообщение отправлено')


def get_api_answer(timestamp):
    """Запрос к API-сервису."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except Exception as error:
        message = f'Не удалось подключиться к API: {error}'
        logging.error(message)
        raise exceptions.APIResponseError(message)
    if response.status_code != HTTPStatus.OK:
        message = (
            'ENDPOINT недоступен, '
            f'ошибка: {response.status_code} '
            f'причина: {response.reason}'
        )
        logging.error(message)
        raise ConnectionError(message)
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        message = (
            f'Полученная структура данных: {type(response)} '
            '- не соответствует типу dict'
        )
        logging.error(message)
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'В ответе нет ключа homeworks'
        logging.error(message)
        raise KeyError(message)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        message = (
            f'Полученная структура данных ключа homeworks: {type(homeworks)} '
            '- не соответствует типу list'
        )
        logging.error(message)
        raise TypeError('message')
    return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы."""
    if 'homework_name' not in homework:
        message = 'В ответе нет ключа homework_name'
        logging.error(message)
        raise KeyError(message)
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        message = f'Неожиданный статус работы - {homework_status}'
        logging.error(message)
        raise ValueError(message)
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Отсутствуют обязательные переменные окружения')
        sys.exit('Отсутствуют обязательные переменные окружения.')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_homework_status = ''
    while True:
        try:
            period_timestamp = timestamp - RETRY_PERIOD
            new_homeworks = get_api_answer(period_timestamp)
            verified_homeworks = check_response(new_homeworks)
            if len(new_homeworks['homeworks']) > 0:
                homework = verified_homeworks[0]
                homework_status = parse_status(homework)
                if homework_status != previous_homework_status:
                    previous_homework_status = homework_status
                    send_message(bot, homework_status)
                    logging.debug('Новый статус. Сообщение отправлено')
            else:
                logging.debug('Статус не изменился')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
