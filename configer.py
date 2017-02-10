#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Только для Python 3.X
Создан для начальной конфигурации бота и последующих изменений конфигурации
Без telegram интерфейса.
Поскольку модель config.py была заменена на более практичный вариант
- работа с библиотекой pickle, теперь нет возможности вручную изменять
config.
"""

import dumploader


def start():
    config = []
    adminid = []
    config.append(input('Bot TOKKEN:'))
    #while auth != True:
    config.append((input('Bot EMAIL (GMAIL ONLY): \n').strip()))
    config.append((input('Bot PASSWORD: \n')).strip())
    #добавить проверочную авторизацию
    config.append((input('Receiver EMAIL: \n')).strip())
    adminid.append((input('You ID in Telegram: \n').strip()))
    print("Save? (y/n)")
    confirm = input()
    if confirm == 'y' or confirm == 'Y':
        dumploader.dumper("config", config)
        dumploader.dumper("admins", adminid)
        print('Config was set\n')
    else:
        start()

if __name__ == "__main__":
    start()
