import logging
import os
import requests
import time
import telegram
import sys

from http import HTTPStatus
from dotenv import load_dotenv


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    item_list = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(item_list)


def send_message(bot, message):
    """Отправление сообщения в Телеграмм."""
    try:
        logger.debug('Удачная отправка сообщения в телеграмм '
                     f'{TELEGRAM_CHAT_ID}: {message}')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Удачная отправка сообщения в телеграмм '
                      f'{TELEGRAM_CHAT_ID}: {message}')
    except Exception as error:
        logging.error(f'Ошибка отправки сообщения в телеграм: {error}')


def get_api_answer(timestamp):
    """Делает запрос к API Яндекс."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except Exception as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != HTTPStatus.OK:
        logger.error('Недоступность эндпоинта https://practicum.yandex.ru')
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        logging.error('Ответ API не является словарем')
        raise TypeError('Ответ API не является словарем')
    if 'homeworks' not in response:
        logging.error('Отсутствует ключ "homeworks" в ответе API')
        raise KeyError('Отсутствует ключ "homeworks" в ответе API')
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        logging.error('Ответ "homeworks" данные не ввиде списка')
        raise TypeError('Ответ "homeworks" данные не ввиде списка')
    return homework[0]


def parse_status(homework):
    """Извлекает информацию о конкретной домашней работе."""
    if 'homework_name' not in homework:
        logging.error('Отсутствует ключ "homework_name" в ответе API')
        raise KeyError('Отсутствует ключ "homework_name" в ответе API')
    homework_name = homework['homework_name']
    if 'status' not in homework:
        logging.error('Отсутствует ключ "status" в ответе API')
        raise KeyError('Отсутствует ключ "status" в ответе API')
    status_homework = homework['status']
    if status_homework not in HOMEWORK_VERDICTS:
        logging.error(f'Неожиданный статус работы: {status_homework}')
        raise KeyError(f'Неожиданный статус работы: {status_homework}')
    verdict = HOMEWORK_VERDICTS[status_homework]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Отсутствие обязательных переменных')
        raise Exception('Отсутствие обязательных переменных')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    MESSAGE_TRY = ''
    MESSAGE_ERROR = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            if message != MESSAGE_TRY:
                send_message(bot, message=message)
                MESSAGE_TRY = message
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message != MESSAGE_ERROR:
                bot.send_message(TELEGRAM_CHAT_ID, message)
                MESSAGE_ERROR = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        filename='program.log',
        encoding='utf--8')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(
        stream=sys.stdout)
    logger.addHandler(handler)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    main()
