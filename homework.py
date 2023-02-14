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

BASE_DIR = os.path.dirname(__file__)
LOG_PATH = os.path.join(BASE_DIR, 'program.log')

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
    TOKENS = (
        ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
        ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
        ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID),
    )
    checked_tokens = True
    for token, value in TOKENS:
        if not value:
            logging.critical(
                'Отсутствуют переменные окружения: {}'.format(token)
            )
            checked_tokens = False
    return checked_tokens


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logging.debug(f'Попытка отправки сообщения: {message}')
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except telegram.error.TelegramError as error:
        logging.error(f'Не удалось отправить сообщение: {error}')
        return False
    else:
        logging.debug(f'Отправлено сообщение: {message}')
        return True


def get_api_answer(timestamp):
    """Запрос к API."""
    response_params = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp},
    }
    try:
        logging.debug(
            'Производится запрос к API. Параметры запроса: '
            '{url}, {headers}, {params}.'.format(**response_params)
        )
        response = requests.get(**response_params)
        if response.status_code != HTTPStatus.OK:
            raise exceptions.InvalidResponseCode(
                'Ответ API не равен 200. '
                f'Код ответа: {response.status_code}. '
                f'Причина: {response.reason}. '
                f'Текст: {response.text}.'
            )
        return response.json()
    except Exception as error:
        raise ConnectionError(
            f'Ошибка: {error}. '
            'Запрос к API провален. Параметры запроса: '
            '{url}, {headers}, {params}.'.format(**response_params)
        )


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError(
            f'Полученная структура данных: {type(response)} '
            '- не соответствует типу dict'
        )
    if 'homeworks' not in response:
        raise exceptions.EmptyResponseFromAPI('В ответе нет ключа homeworks')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(
            f'Полученная структура данных ключа homeworks: {type(homeworks)} '
            '- не соответствует типу list'
        )
    return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('В ответе нет ключа homework_name')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неожиданный статус работы - {homework_status}')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise KeyError('Отсутствуют необходимые переменные окружения')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0
    current_report = {
        'name': '',
        'output': ''
    }
    prev_report = current_report.copy()
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                homework = homeworks[0]
                message = parse_status(homework)
                current_report['name'] = homework.get('homework_name')
                current_report['output'] = message
            else:
                current_report['output'] = 'Нет новых статусов'
            if current_report != prev_report:
                if send_message(bot, message):
                    prev_report = current_report.copy()
                    timestamp = response.get('current_date', timestamp)
            else:
                logging.debug('Нет новых статусов')
        except exceptions.EmptyResponseFromAPI as error:
            logging.error(f'Пустой ответ от API: {error}')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            current_report['output'] = message
            logging.exception(message)
            if current_report != prev_report:
                send_message(bot, message)
                prev_report = current_report.copy()
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format=(
            '%(asctime)s, %(levelname)s, %(pathname)s, %(filename)s '
            '%(funcName)s, %(lineno)d, %(message)s'
        ),
        handlers=[
            logging.FileHandler(filename=LOG_PATH, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    main()
