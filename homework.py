import logging
import os
import requests
import time
import telegram

from http import HTTPStatus
from dotenv import load_dotenv


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    filename='program.log',
    encoding='utf--8')

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
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Удачная отправка сообщения в телеграмм.')
    except Exception as error:
        logging.error(f'Ошибка отправки сообщения в Telegram: {error}')


def get_api_answer(timestamp):
    """Делает запрос к API Яндекс."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        raise Exception(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != HTTPStatus.OK:
        logging.error('Недоступность эндпоинта https://practicum.yandex.ru')
        raise AssertionError(
            'Недоступность эндпоинта https://practicum.yandex.ru')
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if type(response) is not dict:
        logging.error('Ответ API не является словарем')
        raise TypeError('Ответ API не является словарем')
    if len(response.get('homeworks')) == 0:
        logging.error('Список домашних работ пуст')
        raise IndexError('Список домашних работ пуст')
    homework = response.get('homeworks')
    if type(homework) is not list:
        logging.error('Ответ "homeworks" данные не ввиде списка')
        raise TypeError('Ответ "homeworks" данные не ввиде списка')
    return homework[0]


def parse_status(homework):
    """Извлекает информацию о конкретной домашней работе."""
    if 'homework_name' not in homework:
        logging.error('Отсутствует ключ "homework_name" в ответе API')
        raise KeyError('Отсутствует ключ "homework_name" в ответе API')
    if 'status' not in homework:
        logging.error('Отсутствует ключ "status" в ответе API')
        raise KeyError('Отсутствует ключ "status" в ответе API')
    status_homework = homework.get('status')
    verdict = HOMEWORK_VERDICTS.get(status_homework)
    homework_name = homework.get('homework_name')
    if status_homework not in HOMEWORK_VERDICTS:
        logging.error(f'Неожиданный статус работы: {status_homework}')
        raise Exception(f'Неожиданный статус работы: {status_homework}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    if not check_tokens():
        logging.critical('Отсутствие обязательных переменных')
        raise Exception('Отсутствие обязательных переменных')

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            send_message(bot, message=parse_status(homework))
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            bot.send_message(TELEGRAM_CHAT_ID, message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
