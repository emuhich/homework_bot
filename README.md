# Telegram-бот для работы с API Яндекс.Практикума.
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

## Описание проекта:
Бот-ассистент , которой периодически проверяет статус домашней работы отправленой в Яндекс.Практикум. Присылает сообщение и актуальный статус если он был обновлен. Настроен подробный лог работы бота.

## Запуск проекта

Клонируйте репозиторий: 
 
``` 
https://github.com/emuhich/homework_bot.git
``` 

Перейдите в папку проекта в командной строке:

``` 
cd homework_bot
``` 

Создайте и активируйте виртуальное окружение:

``` 
python -m venv venv
``` 
``` 
venv/Scripts/activate
``` 

Установите зависимости из файла *requirements.txt*: 
 
``` 
pip install -r requirements.txt
``` 
Запустите сервер:
``` 
python homework.py
``` 
