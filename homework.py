import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PRACTICUM_API = 'https://praktikum.yandex.ru/api/'
BOT = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    statuses_types = {
        'approved': 'Ревьюеру всё понравилось, можно приступать к '
                    'следующему уроку.',
        'rejected': 'К сожалению в работе нашлись ошибки.'
    }
    if status is None or homework_name is None:
        return 'Неизвестная структура ответа сервера.'
    if status == 'approved':
        verdict = statuses_types['approved']
    elif status == 'rejected':
        verdict = statuses_types['rejected']
    else:
        verdict = f'Неизвестный статус домашнего задания: {status}'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {
        'from_date': current_timestamp
    }
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    method = 'user_api/homework_statuses/'
    try:
        response = requests.get(f'{URL_PRACTICUM_API}{method}',
                                headers=headers, params=params)
    except requests.exceptions.RequestException as e:
        raise Exception(f'requests.get: {e}')
    try:
        homework_statuses = response.json()
    except ValueError as e:
        raise ValueError(f'.json(): {e}')
    return homework_statuses


def send_message(message):
    return BOT.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('current_date') is None:
                current_timestamp = int(time.time())
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
