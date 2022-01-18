import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception:
        raise Exception('Сбой при отправке сообщения в Telegram:')


def get_api_answer(current_timestamp):
    """Api запрос к практикуму."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception:
        raise Exception('любые другие сбои при запросе к эндпоинту')
    if homework.status_code != 200:
        raise Exception(
            'недоступность эндпоинта '
            'https://practicum.yandex.ru/api/user_api/homework_statuses/'
        )
    return homework.json()


def check_response(response):
    """Проверка вернувшегося ответа от практикума."""
    if type(response) == list:
        response = response[0]

    homework = response.get('homeworks')

    if len(homework) == 0:
        raise Exception('Список с домашкой пуст')
    if type(homework) != list:
        raise Exception("homework не является словарем")

    return homework[0]


def parse_status(homework):
    """Достаем из домашки нужную информацию."""
    if 'status' not in homework:
        raise KeyError('Пустое значение status')
    elif 'homework_name' not in homework:
        raise KeyError('Пустое значение homework_name')
    elif homework['status'] not in HOMEWORK_STATUSES:
        raise Exception('недокументированный статус домашней работы, '
                        'обнаруженный в ответе API'
                        )
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка токенов."""
    if not PRACTICUM_TOKEN:
        logging.critical('Отсутствует обязательная переменная окружения: '
                         'PRACTICUM_TOKEN\n'
                         'Программа принудительно остановлена.')
        return False
    elif not TELEGRAM_TOKEN:
        logging.critical('Отсутствует обязательная переменная окружения: '
                         'TELEGRAM_TOKEN\n'
                         'Программа принудительно остановлена.')
        return False
    elif not TELEGRAM_CHAT_ID:
        logging.critical('Отсутствует обязательная переменная окружения: '
                         'TELEGRAM_CHAT_ID\n'
                         'Программа принудительно остановлена.')
        return False

    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    status = ''
    while True:
        try:
            current_timestamp = int(time.time())
            if not check_tokens():
                break
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            if status != message:
                logging.info('Сообщение о новом статусе проверки отправлено')
                send_message(bot, message)
            logging.debug('отсутствие в ответе новых статусов')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logging.info('Сообщение о ошибке отправлено')
            logging.exception('Ошибка:')
            time.sleep(RETRY_TIME)
        else:
            status = message


if __name__ == '__main__':
    main()
