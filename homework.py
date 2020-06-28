import os
import time

import logging
from logging.handlers import RotatingFileHandler
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PRACTICUM_API = 'https://praktikum.yandex.ru/api/'
BOT = telegram.Bot(token=TELEGRAM_TOKEN)

logger = logging.getLogger("Botlog")
logger.setLevel(logging.INFO)
if os.environ.get('IS_HEROKU') is not None:
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)
else:
    file_handler = RotatingFileHandler("Botlog.log", maxBytes=1024 * 1024,
                                       backupCount=2)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_homework_status(homework):
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    statuses_types = {
        'approved': 'Ревьюеру всё понравилось, можно приступать к '
                    'следующему уроку.',
        'rejected': 'К сожалению в работе нашлись ошибки.'
    }
    verdict = statuses_types.get(status)
    if verdict is None or homework_name is None:
        return 'Неизвестная структура ответа сервера.'
    # if status == 'approved':
    #     verdict = statuses_types['approved']
    # elif status == 'rejected':
    #     verdict = statuses_types['rejected']
    # else:
    #     verdict = f'Неизвестный статус домашнего задания: {status}'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}' \
           f'\n\n{os.environ.get("IS_HEROKU")}' \
           f'\n\n{os.environ.get("THEANSWERTOEVERYTHINGEVER")}'


def get_homework_statuses(current_timestamp):
    params = {
        'from_date': 0
    }
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    method = 'user_api/homework_statuses/'
    try:
        response = requests.get(f'{URL_PRACTICUM_API}{method}',
                                headers=headers, params=params)
        homework_statuses = response.json()
    except requests.exceptions.RequestException:
        logger.exception('Произошла ошибка при запросе данных с сервера:')
        empty_dict = {}
        return empty_dict
        # raise Exception(f'requests.get: {e}')
    except ValueError:
        logger.exception('Ответ сервера не в формате JSON:')
        empty_dict = {}
        return empty_dict
        # raise ValueError(f'.json(): {e}')
    return homework_statuses


def send_message(message):
    return BOT.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    logger.info('Бот запущен.')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('current_date') is None:
                current_timestamp = int(time.time())
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]))
                logger.info('Сообщение успешно отправлено.')
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
