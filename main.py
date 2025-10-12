# !/usr/bin/env python
import datetime
import time
import typing

import firebase_admin
import serial
from firebase_admin import credentials
from gpiozero import LED
from firebase_admin import db

from app.ancs_notification import ANCSNotification


class Accessibilitron:

    def __init__(self):
        #   ANCS
        self.serial = None
        self.has_completed_setup: bool = False
        self.active_notifications: typing.List[ANCSNotification] = []
        self.setup()

    def setup(self):
        self.set_serial()

    #   ANCS
    def set_serial(self):
        self.serial = serial.Serial(
            port='/dev/ttyS0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

    def setup_active_notifications(self):
        if self.has_completed_setup:
            return
        print("Setting up active notifications.")
        self.serial.write("AT".encode())
        self.has_completed_setup = True

    def find_details_of_active_ancs_notifications(self):
        notifications_to_detail = [x for x in self.active_notifications if not x.has_details()]
        if len(notifications_to_detail) == 0:
            return
        notification_to_detail = notifications_to_detail[0]
        print(f"SENDING: AT+ANCS{notification_to_detail.event_id}000")
        self.serial.write(f"AT+ANCS{notification_to_detail.event_id}000".encode())

    def process_ancs_notification(self, ancs_notification_string: str):
        ancs_notification_string = ancs_notification_string[1:]
        ancs_message_object = ANCSNotification.set_from_message_string(ancs_notification_string)
        if ancs_message_object.action == 'ADDED':
            self.active_notifications.append(ancs_message_object)
        else:
            self.active_notifications = [
                x for x in self.active_notifications
                if x.event_id == ancs_message_object.event_id
            ]

    def process_ok_ancs_line_from_list(self, ok_ancs_line: str):
        if len(ok_ancs_line) == 0:
            return
        elif ok_ancs_line.startswith('8'):
            self.process_ancs_notification(ok_ancs_line)

    def process_ancs_w_line(self, raw_ancs_w_line):
        if not raw_ancs_w_line.startswith('OK+'):
            return
        split_ancs_w_line = raw_ancs_w_line.split('OK+ANCS')
        if len(split_ancs_w_line) != 4:
            return
        if split_ancs_w_line[1] != 'W':
            return
        event_id = split_ancs_w_line[0][3:7]
        detail = ''.join([x[3:] for x in split_ancs_w_line[2:]])

        for active_notification in self.active_notifications:
            if active_notification.event_id == event_id:
                active_notification.add_detail(detail)
                print(active_notification)

    def process_line_from_hm_10(self, raw_hm_10_bits):
        raw_hm_10_str: str = raw_hm_10_bits.decode('utf-8')
        if raw_hm_10_str == '':
            return

        #   Documentation suggests this should be "AT+ANCS,"
        #   but it comes out at "OK+ANCS"

        #   This is identifying a notification.
        if 'OK+ANCSW' in raw_hm_10_str:
            self.process_ancs_w_line(raw_hm_10_str)
        elif 'OK+ANCS8' in raw_hm_10_str:
            ok_ancs_as_list: typing.List[str] = raw_hm_10_str.split('OK+ANCS')
            for ok_ancs_str in ok_ancs_as_list:
                self.process_ok_ancs_line_from_list(ok_ancs_str)
        else:
            print(raw_hm_10_str)

    def run(self):
        try:
            self.setup_active_notifications()
            while True:
                ancs_message = self.serial.readline()
                self.process_line_from_hm_10(ancs_message)
                time.sleep(0.05)
                self.find_details_of_active_ancs_notifications()
        except KeyboardInterrupt as ke:
            pass
        finally:
            self.serial.close()


Accessibilitron().run()
