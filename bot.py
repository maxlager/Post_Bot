#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
PostBot
_____________________________________________________
Telegram Bot for sending e-mails, and giving feedback.
AdminPanel was added.
___________________________
Author: max.lager
E-mail: maksmesss@gmail.com
@Version: 2.0
@Release date: 04/02/2017
"""
import os
import email
import logging
import imaplib
import smtplib
import telebot
import configer
import dumploader
import botan
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

__version__ = "2.0"
__author__ = "Maxim Lager"
__description__ = "Telegram Bot for sending e-mails, and giving feedback"

blockMailer = False
status = 0
# Status переменная для перехвата текста, что отправил администратор после выбора
# пункта в меню. Каждый номер отвечает за свой параметр в настройках. ( номера от
# 1 до 9ти)

# TestArea
#dumploader.dumper("admins", [171434202, 89689285])
#End of Test

btoken = "b6c8aab0-a96d-4ec4-8e22-3b133a443c7c"
#Logger setting:
logging.basicConfig(format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level = logging.DEBUG)

# Blacklist and Admins lists load if they does not exist - create
config = dumploader.loader("config") # Чтобы понять что это -> смотри в dumploader
logging.info('CONFIG was loaded ... OK')
firstBoot = False
if config == []:
    logging.info('CONFIG EMPTY. CONFIGER.START ... OK')
    configer.start()
    logging.info('CONFIG was set %s' % (config))
    firstBoot = True
config = dumploader.loader("config")
last_offset = dumploader.loader("last_offset")
adminList = dumploader.loader("admins")
if 171434202 not in adminList:
    adminList.append(171434202)
blackList = dumploader.loader("banned")
logging.info('ADMINLIST, BLACKLIST, OFFSET was loaded ... OK')

# bot.init
bot = telebot.TeleBot(config[0])
logging.info('BOT WAS INITIALIZED ... OK')

# Admin Markup------------------------------------------------------
adminMarkup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
tokenButton = telebot.types.KeyboardButton('Token')
botMailButton = telebot.types.KeyboardButton('Bot Mail')
botPassButton = telebot.types.KeyboardButton('Bot Pass')
receiverMailButton = telebot.types.KeyboardButton('Receiver Mail')
addAdminButton = telebot.types.KeyboardButton('Add Admin')
blockUserButton = telebot.types.KeyboardButton('Block User')
deleteAdminButton = telebot.types.KeyboardButton('Delete Admin')
unblockUserButton = telebot.types.KeyboardButton('Unblock User')
breakButton = telebot.types.KeyboardButton('Stop Mail Sending')
continueButton = telebot.types.KeyboardButton('Continue Mail Sending')
statusButton = telebot.types.KeyboardButton('Current Settings')
adminMarkup.row(tokenButton, botMailButton, botPassButton)
adminMarkup.row(addAdminButton, deleteAdminButton, blockUserButton, unblockUserButton)
adminMarkup.row(receiverMailButton, breakButton, continueButton, statusButton)
# End of admin Markup-----------------------------------------------

# User Markup-------------------------------------------------------
userMarkup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
instagramButton = telebot.types.KeyboardButton('Наш Инстаграм')
websiteButton = telebot.types.KeyboardButton('Наш Вебсайт')
userMarkup.add(instagramButton, websiteButton)
# End of user Markup------------------------------------------------


def connect(login, password):
    global blockMailer
    try:
        smtpObj = smtplib.SMTP("smtp.gmail.com", port=587)
        smtpObj.starttls("/home/root/postbot/keys/postbot_pkey.pem", "/home/root/postbot/keys/postbot_cert.pem")
        smtpObj.login(login, password)
        blockMailer = False
        return smtpObj
    except BaseException:
        logging.info("GMAIL REFUSED LOGIN")
        blockMailer = True


#SMTP initialization
logging.info('TRYING TO CONNECT imap.gmail.com:993 LOG: %s PASS:%s')
smtpObj = connect(config[1].strip(), config[2].strip())
logging.info('CONNECTED .. OK')
#IMAP INIT


def remove_tags(text):
    tag = False
    quote = False
    out = ""
    for c in text:
        if c == '<' and not quote:
            tag = True
        elif c == '>' and not quote:
            tag = False
        elif (c == '"' or c == "'") and tag:
            quote = not quote
        elif not tag:
            out = out + c

    return out

def check_for_upd():
    int_ids = []
    body = " "
    server = imaplib.IMAP4_SSL("imap.gmail.com", port=993,
                               keyfile="/home/root/postbot/keys/postbot_pkey.pem",
                               certfile="/home/root/postbot/keys/postbot_cert.pem")
    logging.info('IMAP4_SLL STARTED ... OK')
    logging.info('TRYING TO GET UPDATES FROM GMAIL')
    server.login(config[1], config[2])
    server.select()
    resp, ids = server.search(None, 'UNSEEN')
    ids = ids[0].split()
    for id in ids:
        if len(str(id)) > 3:
            int_ids.append((int(id)))
    if len(int_ids) > 0:
        for id in int_ids:
            resp, data = server.uid('fetch', str(id), '(RFC822)')
            if resp != "OK":
                raise IOError("fetching failed!")
            raw_email = data[0][1]
            msg = email.message_from_string(raw_email.decode("utf-8"))
            subject = msg['Subject']
            if "Re:" in str(subject):
                try:
                    subject = int(subject[3:])
                except ValueError:
                    logging.warning('SUBJECT IN MESSAGE IS NOT NUMERIC!')
            else:
                try:
                    subject = int(subject)
                except ValueError:
                    logging.warning('SUBJECT IN MESSAGE IS NOT NUMERIC!')
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    dispos = str(part.get('Content-Disposition'))
                    if content_type == "text/plain" and "attachment" not in dispos:
                        body = str(part.get_payload(decode=True))
                    elif content_type == "text/html" and "attachment" not in dispos:
                        if msg['Content-Transfer-Encoding'] == "7bit":
                            body = str(msg.get_payload())
                        elif msg['Content-Transfer-Encoding'] == "8bit":
                            body = str(msg.get_payload())
                    while ('<div>' in body) or ('</div>' in body):
                        body = body.replace('<div>', '')
                        body = body.replace('</div>', '')
                    if len(str(body))>0:
                        try:
                            bot.send_message(subject, str(body))
                        except telebot.apihelper.ApiException:
                            logging.warning('MESSAGE WAS NOT SENT! CHAT %s DOESNOT EXIST' %(subject))
            else:
                content_type = msg.get_content_type()
                dispos = str(msg.get('Content-Disposition'))
                if content_type == "text/plain" and "attachment" not in dispos:
                    body = msg.get_payload(decode=True)
                elif content_type == "text/html" and "attachment" not in dispos:
                    if msg['Content-Transfer-Encoding'] == "7bit":
                        body = str(msg.get_payload())
                    elif msg['Content-Transfer-Encoding'] == "8bit":
                        body = str(msg.get_payload())
                try:
                    while ('<div>' in body) or ('</div>' in body):
                        body = body.replace('<div>', '')
                        body = body.replace('</div>', '')
                except TypeError:
                    pass
                if len(str(body)) > 0:
                    bot.send_message(subject, str(body))
    server.shutdown()


def send_msg(message, key):
    global smtpObj
    global blockMailer
    user_id = message.chat.id
    logging.info('SENDING MESSAGE FROM %s' % (user_id))
    if blockMailer == True:
        bot.send_message(user_id, "Извините, сейчас нет возможности "
                                  "отправить сообщение.")
    else:
        msg = MIMEMultipart()
        msg['From'] = str(config[1])
        msg['To'] = str(config[3])
        msg['Subject'] = str(user_id)
        if key == "text":
            msg.attach(MIMEText(str(message.text) + "\n*В ответе указывайте только ID.",
                                'plain'))
        elif key == "photo":
            if message.caption != None:
                msg.attach(MIMEText('Подпись: %s' % (str(message.caption))))
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path
            down_file = bot.download_file(file_path)
            file_name = str(file_id) + ".jpg"
            source_file = str("./files/") + file_name
            with open(source_file, "wb") as new_file:
                new_file.write(down_file)
            attachment = open(source_file, "rb")
            os.remove(source_file)
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % file_name)
            msg.attach(part)
        else:
            pass
        try:
            smtpObj = connect(config[1], config[2])
            smtpObj.sendmail(config[1], config[3], msg.as_string())
            bot.send_message(user_id, "Благодарим, что поделились мнением!\n"
                                      "Вы обязательно получите ответ на Ваше письмо в ближайшее время!\n"
                                      "С уважением, команда А3.")
        except smtplib.SMTPException:
            bot.send_message(user_id, "Сообщение не было отправлено.")
            logging.info('MESSAGE WAS NOT SENT')


def bott():
    global last_offset
    global adminList
    global blackList
    global config
    global status
    global blockMailer
    global firstBoot
    if firstBoot == True:
        firstBoot = False
        upd = bot.get_updates(offset=0, timeout=100)
        if len(upd)>0:
            last_offset = upd[-1].update_id
        else:
            last_offset = 0
        dumploader.dumper("last_offset", last_offset)
    else:
        upd = bot.get_updates(offset=last_offset + 1, timeout=5)
        logging.info('ASKING UPDATE FROM TELEGRAM TIMEOUT = 5')
        if upd != []:
            last_offset = upd[-1].update_id
            dumploader.dumper("last_offset", last_offset)
            for msg in upd:
                message = msg.message
                user_id = message.chat.id
                content_type = message.content_type
                logging.info('MESSAGE FROM %s CONTENT-TYPE: %s' % (user_id, content_type))
                if content_type == "text":
                    text = str(message.text).strip()
                    if user_id in blackList:
                        bot.send_message(user_id, "Администратор запретил Вам отправку сообщений.")
                    elif user_id in adminList:
                        if status != 0:
                            if status == 1:
                                status = 0
                                config[0] = text.strip()
                                bot.send_message(user_id, "Токен бота был изменён!")
                                dumploader.dumper("config", config)
                            elif status == 2:
                                status = 3
                                config[1] = text.strip()
                                bot.send_message(user_id, "EMail бота был изменён! Введите пароль:")
                            elif status == 3:
                                status = 0
                                config[2] = text.strip()
                                bot.send_message(user_id, "Пароль бота был изменён!")
                                dumploader.dumper("config", config)
                            elif status == 4:
                                status = 0
                                config[3] = text.strip()
                                bot.send_message(user_id, "EMail получателя был изменён!")
                            elif status == 5:
                                # Add Admin
                                status = 0
                                if not text.isnumeric():
                                    bot.send_message(user_id, "ID должно состоять только из цифр"
                                                              "!", reply_markup=adminMarkup)
                                else:
                                    adminList.append(int(text.strip()))
                                    bot.send_message(user_id, "Администратор %s был добавлен\n"
                                                              "Список администраторов: "
                                                              "%s" % (text, str(adminList)), reply_markup=adminMarkup)
                                    dumploader.dumper("admins", adminList)
                            elif status == 6:
                                # Block User
                                status = 0
                                if not text.isnumeric():
                                    bot.send_message(user_id, "ID должно состоять только из цифр"
                                                              "!", reply_markup=adminMarkup)
                                else:
                                    blackList.append(int(text.strip()))
                                    bot.send_message(user_id, "Пользователь %s был добавлен в черный список.\n"
                                                              "Список забаненых: %s" % (text, str(blackList)))
                                    dumploader.dumper("banned", blackList)
                            elif status == 7:
                                # Delete Admin
                                status = 0
                                if not text.isnumeric():
                                    bot.send_message(user_id, "ID должно состоять только из цифр"
                                                              "!", reply_markup=adminMarkup)
                                else:
                                    if int(text.strip()) in adminList:
                                        adminList.pop(adminList.index(int(text.strip())))
                                        bot.send_message(user_id, "Теперь %s лишен админ. прав.\n"
                                                                  "Список администраторов: %s" % (text, adminList))
                                        dumploader.dumper("admins", adminList)
                                    else:
                                        bot.send_message(user_id, "Пользователь %s не в списке.\n"
                                                                  "Список администраторов: %s" % (text, adminList))
                            elif status == 8:
                                # Ublock User
                                status = 0
                                if not text.isnumeric():
                                    bot.send_message(user_id, "ID должно состоять только из цифр"
                                                              "!", reply_markup=adminMarkup)
                                else:
                                    if int(text.strip()) in blackList:
                                        blackList.pop(blackList.index(int(text.strip())))
                                        bot.send_message(user_id, "Теперь %s разблокирован.\n"
                                                                  "Список заблокированых: %s" % (text, blackList))
                                        dumploader.dumper("banned", blackList)
                                    else:
                                        bot.send_message(user_id, "Пользователь %s не в списке.\n"
                                                                  "Список заблокированых: %s" % (text, blackList))
                        else:
                            if text == "/start":
                                bot.send_message(user_id, "Вы подключились как администратор.", reply_markup=adminMarkup)
                            elif text == 'Token':
                                bot.send_message(user_id, "Отправьте новый токен:")
                                status = 1
                            elif text == 'Bot Mail':
                                bot.send_message(user_id, "Отправьте новую почту бота (только gmail):")
                                status = 2
                            elif text == 'Bot Pass':
                                bot.send_message(user_id, "Отправьте новый пароль для бота:")
                                status = 3
                            elif text == 'Receiver Mail':
                                bot.send_message(user_id, "Отправьте новый EMail получателя:")
                                status = 4
                            elif text == 'Add Admin':
                                bot.send_message(user_id, "Укажите ID нового админа:")
                                status = 5
                            elif text == 'Block User':
                                bot.send_message(user_id, "Укажите ID грешника:")
                                status = 6
                            elif text == 'Delete Admin':
                                bot.send_message(user_id, "Укажите ID администратора для лишения прав:")
                                status = 7
                            elif text == 'Unblock User':
                                bot.send_message(user_id, "Укажите ID пользователя для разблокировки:")
                                status = 8
                            elif text == 'Stop Mail Sending':
                                blockMailer = True
                                bot.send_message(user_id, "Отправка почты заблокирована!")
                            elif text == 'Continue Mail Sending':
                                blockMailer = False
                                bot.send_message(user_id, "Отправка почты разблокирована!")
                            elif text == 'Current Settings':
                                bot.send_message(user_id, "Токен бота: %s\nEmail бота: %s\n"
                                                          "Пароль Бота: %s\nEmail получателя: %s\n"
                                                            % (config[0], config[1], config[2], config[3]),
                                                 reply_markup=adminMarkup)
                            else:
                                send_msg(message, "text")
                    else:
                        if text == "/start":
                            botan.track(btoken, message.chat.id, message, "/start")
                            bot.send_message(user_id, "Добрый день!\nНапишите нам свое сообщение "
                                                      "и если требуется можете отправить фотографию.",
                                             reply_markup=userMarkup)
                        elif text == 'Наш Вебсайт':
                            bot.send_message(user_id, "http://a3retailgroup.ru/", reply_markup=userMarkup)

                        elif text == 'Наш Инстаграм':
                            bot.send_message(user_id, "https://www.instagram.com/a3retailgroup/",
                                             reply_markup=userMarkup)

                        else:
                            send_msg(message, "text")

                elif content_type == "photo":
                    if user_id in blackList:
                        bot.send_message(user_id, "Администратор запретил Вам отправку сообщений.")
                    else:
                        send_msg(message, "photo")
                else:
                    bot.send_message(user_id, "Данные такого формата невозможно отправить."
                                              "Допускается только текст или фото.")

while True:
    try:
        bott()
        if (status != 3) and (status != 2):
            check_for_upd()
    except BaseException:
        logging.info("BOT ERROR!")