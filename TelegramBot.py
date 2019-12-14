# encoding: UTF-8
import re
import sqlite3
from builtins import print
import os

import telebot
from telebot import apihelper
import asyncio
import time
import datetime
import threading
import requests

from telethon import TelegramClient
from telethon.tl.functions.channels import GetAdminLogRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import ChannelAdminLogEventsFilter, InputChannel
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.channels import GetFullChannelRequest


class OutPutMessages:
    @classmethod
    def __init__(cls):
        cls.fail_send_request = "We can not send it right now.\nYou can try later."
        cls.success_send_response = "We've sent, wait for your teacher response..."
        cls.fail_send_response = "We can not send it right now.\nYou can try later."
        cls.success_send_all_students = "I send your message to all your student.\nsent message : "
        cls.fail_send_all_students = "We can not send it right now.\nYou can try later."
        cls.reply = "some text"
        cls.start_message = "text some"
        cls.help_message = "some text"
        cls.about_us = "some text"
        cls.biologyOrChemistry = "some text"
        cls.teacher2_request = "some text"
        cls.teacher2_request = "som text"
        cls.not_channel_member = "some text"

class CommonService:
    @classmethod
    def send_message_all_types(cls, bot, message, chat_id, reply_to_message_id):
        message_content_type = message.content_type
        if message_content_type == content_types[0]:
            bot.send_message(chat_id=chat_id, text=message.text, reply_to_message_id=reply_to_message_id)
        elif message_content_type == content_types[1]:
            bot.send_audio(chat_id=chat_id, audio=message.audio.file_id, caption=message.caption,
                           reply_to_message_id=reply_to_message_id)
        elif message_content_type == content_types[3]:
            bot.send_photo(chat_id=chat_id, photo=message.photo[0].file_id, caption=message.caption,
                           reply_to_message_id=reply_to_message_id)
        elif message_content_type == content_types[4]:
            bot.send_sticker(chat_id=chat_id, data=message.sticker.file_id,
                             reply_to_message_id=reply_to_message_id)
        elif message_content_type == content_types[5]:
            bot.send_video(chat_id=chat_id, data=message.vide.file_id, caption=message.caption,
                           reply_to_message_id=reply_to_message_id)
        elif message_content_type == content_types[7]:
            bot.send_voice(chat_id=chat_id, voice=message.voice.file_id, caption=message.caption,
                           reply_to_message_id=reply_to_message_id)
        elif message_content_type == content_types[8]:
            # bot.send_location(chat_id=chat_id, data=message.location.file_id,
            #                   reply_to_message_id=reply_to_message_id)
            pass
        elif message_content_type == content_types[9]:
            # bot.send_contact(chat_id=chat_id, data=message.contact.file_id,
            #                  reply_to_message_id=reply_to_message_id)
            pass


class TeacherService(CommonService):
    def __init__(self, out_msg, conf, db_conn):
        self.out_msg = out_msg
        self.conf = conf
        self.db_conn = db_conn

    def update_teacher_chat_ids(self, message):
        if message.from_user.username == self.conf.teacher2_username:
            if self.conf.teacher2_chat_id is None:
                self.conf.teacher2_chat_id = message.chat.id
        elif message.from_user.username == self.conf.teacher2_username:
            if self.conf.teacher2_chat_id is None:
                self.conf.teacher2_chat_id = message.chat.id

    def send_teacher_response(self, bot, message):
        reply_to_message = message.reply_to_message
        bot_chat_id = message.chat.id
        student_message_regex = "@[A-Z|a-z|_|0-9]+ [0-9]+ [0-9]+:.*"
        pattern = re.compile(student_message_regex)
        if reply_to_message is not None and reply_to_message.caption is None:
            reply_to_message.caption = ""
        if reply_to_message is None:  # teacher want to send message to all students that are stored in database
            student_number = 0
            for chat_id, username in self.db_conn.select_chat_ids():
                self.send_message_all_types(bot=bot, message=message, chat_id=chat_id, reply_to_message_id=None)
                student_number += 1
            bot.send_message(chat_id=bot_chat_id,
                             text=self.out_msg.success_send_all_students + " " + str(student_number))
        elif (reply_to_message.text is not None and not re.match(pattern, reply_to_message.text)) and (
                reply_to_message.caption is not None and not re.match(pattern, reply_to_message.caption)):
            # teacher does not replied to student message text
            # teacher can not reply to its own message only in dirty way
            print("in dirty way :-->" + str(message))
            print(reply_to_message.text)
            for chat_id, username in self.db_conn.select_chat_ids():
                reply_to_message.text += self.out_msg.reply
                self.send_message_all_types(bot, reply_to_message, chat_id, reply_to_message_id=None)
                self.send_message_all_types(bot, message, chat_id, reply_to_message_id=None)
            bot.send_message(chat_id=bot_chat_id, text=self.out_msg.success_send_all_students)
        elif reply_to_message.text is None and reply_to_message.caption is None:  # TODO reply to it's own message
            pass
        elif (reply_to_message.text is not None and re.match(pattern, reply_to_message.text)) or (
                reply_to_message.caption is not None and re.match(pattern, reply_to_message.caption)):
            # teacher replied to one of the students message
            print("teacher replied to one of the students message")
            reply_to_message_id = None
            if reply_to_message.text is not None and re.match(pattern, reply_to_message.text):
                to_chat_id = reply_to_message.text.split(" ")[1]
                reply_to_message_id = reply_to_message.text.split(" ")[2].split(":")[0]
            else:
                to_chat_id = reply_to_message.caption.split(" ")[1]
                reply_to_message_id = reply_to_message.caption.split(" ")[2].split(":")[0]

            self.send_message_all_types(bot, message, to_chat_id, reply_to_message_id)
            # bot.forward_message(chat_id=reply_chat_id, from_chat_id=bot_chat_id, message_id=message.message_id)
        else:
            pass
            # TODO some invalid text that i should check out tonight

        return None


class BotConfiguration:
    def __init__(self):
        self.bot_token = BotConfiguration.load_bot_token()
        self.bot = telebot.TeleBot(self.bot_token)
        self.teacher2_chat_id = "<chat id of teacher>"
        self.teacher2_username = "<username of teacher>"

        self.teacher2_chat_id = "<chat id of teacher>"
        self.teacher2_username = "<username of teacher>"
        self.developer_id = "<developer chat id>"
        self.channel_username = "<channel username>"

    @classmethod
    def load_bot_token(cls):
        return "<Bot token>"


class StudentService(CommonService):
    def __init__(self, out_msg, conf):
        self.out_smg = out_msg
        self.conf = conf

    def send_student_request(self, bot, message):
        reply_to_message = message.reply_to_message
        bot_chat_id = message.chat.id
        if message.text is None:
            message.text = ""
        message.text = "@" + message.from_user.username + " " + str(bot_chat_id) + " " + str(
            message.message_id) + ":\n" + message.text
        if message.content_type != 'text':
            message.caption = message.text
        std_user = message.from_user.username
        std_chat_id = message.chat.id
        last_request_type = db_conn.select_user_last_request_type(std_chat_id)
        destination_teacher = None
        if last_request_type == 'chemistry':
            destination_teacher = conf.teacher2_chat_id
        elif last_request_type == 'biology':
            destination_teacher = conf.teacher2_chat_id
        if destination_teacher is not None:

            if destination_teacher == conf.teacher2_chat_id:
                conf.bot.send_message(chat_id=message.chat.id, text=output_msg.teacher2_request)
            elif destination_teacher == conf.teacher2_chat_id:
                conf.bot.send_message(chat_id=message.chat.id, text=output_msg.teacher2_request)
            if reply_to_message is None:
                self.send_message_all_types(bot, message, destination_teacher, reply_to_message_id=None)
            else:  # TODO
                if reply_to_message.text is None:
                    reply_to_message.caption = ""
                    reply_to_message.caption = "@" + std_user + " " + str(
                        std_chat_id) + " " + str(
                        reply_to_message.message_id) + ":\n" + reply_to_message.caption + self.out_smg.reply
                else:
                    if reply_to_message.content_type != "text":
                        reply_to_message.caption = reply_to_message.caption + self.out_smg.reply
                    reply_to_message.text = "@" + std_user + " " + str(
                        std_chat_id) + ":\n" + reply_to_message.text + self.out_smg.reply
                self.send_message_all_types(bot=bot, message=reply_to_message, chat_id=destination_teacher,
                                            reply_to_message_id=None)
                self.send_message_all_types(bot=bot, message=message, chat_id=destination_teacher,
                                            reply_to_message_id=None)
        else:
            conf.bot.send_message(std_chat_id, text="لطفا نوع سوال خود را انتخاب کنید.")

    def send_not_able_for_this_user(self, bot, chat_id, channel_username):
        bot.send_message(chat_id=chat_id, text=self.out_smg.not_channel_member + channel_username)


class DataBaseConnection:
    def __init__(self):
        self.conn = sqlite3.connect("BotDatabase.db", check_same_thread=False)
        self.create_chat_table()

    def create_chat_table(self):
        exc = 0
        cursor = self.conn.cursor()
        try:
            query = """CREATE TABLE CHAT(ID char(20),USERNAME char(20),QuestionSub char(10),PRIMARY KEY (ID))"""
            exc = cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            pass
            print("Error!-->" + str(e))
        finally:
            cursor.close()
        return exc

    def insert_chat(self, chat_id, username):
        exc = 0
        cursor = self.conn.cursor()
        try:
            query = """INSERT INTO CHAT (ID,USERNAME) VALUES (\"""" + str(chat_id) + """\",\"""" + str(
                username) + """\")"""
            exc = cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print("Error!-->" + str(e))
        finally:
            cursor.close()
        return exc

    def select_chat_ids(self):
        result = []
        cursor = self.conn.cursor()
        try:
            query = """SELECT ID,USERNAME FROM CHAT"""
            cursor.execute(query)
            result = cursor.fetchall()
            self.conn.commit()
        except Exception as e:
            print("Error!-->" + str(e))
        finally:
            cursor.close()
        return result

    def delete_chat_id(self, id):
        exc = 0
        cursor = self.conn.cursor()
        try:
            query = """DELETE FROM CHAT WHERE ID=""" + str(id)
            exc = cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print("Error!-->" + str(e))
        finally:
            cursor.close()
        return exc

    def update_user_last_request_type(self, user_id, request_type):
        exc = 0
        cursor = self.conn.cursor()
        try:
            query = """UPDATE CHAT SET QuestionSub=""" + """\"""" + request_type + """\"""" + """ WHERE ID=\"""" + str(
                user_id) + """\""""
            exc = cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print("Error!-->" + str(e))
        finally:
            cursor.close()
        return exc

    def select_user_last_request_type(self, user_id):
        exc = None
        result = None
        cursor = self.conn.cursor()
        try:
            query = """SELECT QuestionSub FROM CHAT WHERE ID=\"""" + str(user_id) + """\""""
            exc = cursor.execute(query)
            result = cursor.fetchall()
            self.conn.commit()
        except Exception as e:
            print("Error!-->" + str(e))
        finally:
            cursor.close()
        return result[0][0]

    def check_user_channel(self, id):
        cursor = self.conn.cursor()
        try:
            query = """SELECT ID,USERNAME FROM CHAT WHERE ID=""" + str(id)
            exc = cursor.execute(query)
            result = cursor.fetchall()
            self.conn.commit()
        except Exception as e:
            print("Error!-->" + str(e))
        finally:
            cursor.close()
        return len(result) >= 1


conf = BotConfiguration()
db_conn = DataBaseConnection()
output_msg = OutPutMessages()
ssrv = StudentService(output_msg, conf)
tsrv = TeacherService(output_msg, conf, db_conn)

content_types = ['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact',
                 'new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
                 'group_chat_created', 'supergroup_chat_created', 'channel_chat_created,' 'migrate_to_chat_id',
                 'migrate_from_chat_id', 'pinned_message']


def send_dev(text):
    conf.bot.send_message(conf.developer_id, text)


async def update(db_conn):
    send_dev("initializing channel check")
    api_id = "<your api id>"  # Your api_id
    api_hash = '<api hash>'  # Your api_hash
    phone_number = 'admin phone number'  # Your phone number
    channel_user_name = "<channel username>"
    client = TelegramClient(phone_number, api_id, api_hash)
    client.session.report_errors = False
    await client.connect()
    c = await client.is_user_authorized()
    if not c:
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input('Enter the code: '))
    offset = 0
    limit = 200
    my_filter = ChannelParticipantsSearch('')
    all_participants = []
    while_condition = True
    #################################
    users = set()
    while while_condition:
        participants = await client(
            GetParticipantsRequest(channel=channel_user_name, filter=my_filter, offset=offset, limit=limit, hash=0))
        all_participants.extend(participants.users)

        for user in participants.users:
            users.add(str(user.id))

        offset += len(participants.users)
        if len(participants.users) < limit:
            while_condition = False
    for id, username in db_conn.select_chat_ids():
        send_dev("database users--> " + str(id) + " " + username)
        if str(id) not in users:
            send_dev("Removed students :" + str(id))
            db_conn.delete_chat_id(id)
    await client.disconnect()
    send_dev("One update occurred and done.")


@conf.bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    conf.bot.send_message(chat_id=chat_id, text=output_msg.start_message)


@conf.bot.message_handler(commands=['about_us'])
def start_message(message):
    chat_id = message.chat.id
    conf.bot.send_message(chat_id=chat_id, text=output_msg.about_us)


@conf.bot.message_handler(commands=['biology'])
def biology(message):
    chat_id = message.chat.id
    exc = db_conn.update_user_last_request_type(chat_id, 'biology')
    conf.bot.send_message(chat_id=chat_id, text=output_msg.biologyOrChemistry)


@conf.bot.message_handler(commands=['chemistry'])
def biology(message):
    chat_id = message.chat.id
    exc = db_conn.update_user_last_request_type(chat_id, 'chemistry')
    conf.bot.send_message(chat_id=chat_id, text=output_msg.biologyOrChemistry)


@conf.bot.message_handler(content_types=content_types)
def answer_std(message):
    print(message.chat.id)
    send_dev(message.from_user.username + "-->" + str(message.text))
    try:
        if message.chat.id == conf.teacher2_chat_id or message.chat.id == conf.teacher2_chat_id:  # this is teacher message
            tsrv.send_teacher_response(conf.bot, message)
            tsrv.update_teacher_chat_ids(message)
        else:  # this is the students message
            exc = db_conn.insert_chat(message.chat.id, message.from_user.username)
            try:
                asyncio.run(update(db_conn))
            except Exception as e:
                send_dev("Error!-->" + str(e))
            if db_conn.check_user_channel(message.from_user.id):
                ssrv.send_student_request(conf.bot, message)
            else:
                ssrv.send_not_able_for_this_user(conf.bot, message.chat.id, conf.channel_username)
                # break
    except Exception as e:
        send_dev("Error!-->" + str(e))


conf.bot.polling(none_stop=True, interval=10, timeout=1000)
