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
    if status is None:
        return 'Сервер не передает статус домашнего задания.'
    elif homework_name is None:
        return 'Сервер не передает название домашнего задания.'
    else:
        if homework.get('status') != 'approved':
            verdict = 'К сожалению в работе нашлись ошибки.'
        else:
            verdict = 'Ревьюеру всё понравилось, ' \
                      'можно приступать к следующему уроку.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {
        'from_date': current_timestamp
    }
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    method = 'user_api/homework_statuses/'
    response = requests.get(f'{URL_PRACTICUM_API}{method}',
                            headers=headers, params=params)
    return response.json()


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
