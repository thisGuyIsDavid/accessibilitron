# !/usr/bin/env python
import time
import typing

import serial

from app.ANCSNotification import ANCSNotification


class ANCS:
    def __init__(self):
        #   ANCS
        self.serial = None
        self.active_notifications: typing.List[ANCSNotification] = []

        self.setup()

    def setup(self):
        self.set_serial()

    #   ANCS
    def set_serial(self):
        self.serial = serial.Serial(
            port='/dev/serial0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

    def setup_active_notifications(self):
        print("Setting up active notifications.")
        self.serial.write("AT".encode())

    def process_added_notification(self, notification: ANCSNotification):
        #   When the phone reconnects, the "old" messages will not get removed.
        #   We must check for events already existing.
        if notification.event_id in [x.event_id for x in self.active_notifications]:
            return
        self.active_notifications.append(notification)

    def process_removed_notification(self, notification: ANCSNotification):
        self.active_notifications = [x for x in self.active_notifications if x.event_id != notification.event_id]

    def process_ancs_notification(self, ancs_notification_string: str):
        message_string = ancs_notification_string[1:]
        ancs_notification = ANCSNotification.set_from_message_string(message_string)

        #   We are only concerned with active calls and missed calls.
        if ancs_notification.category not in ['INCOMING CALL', 'MISSED CALL']:
            return

        if ancs_notification.action == 'ADDED':
            self.process_added_notification(ancs_notification)
            print(ancs_notification)
        else:
            self.process_removed_notification(ancs_notification)

    def process_ok_ancs_line_from_list(self, ok_ancs_line: str):
        if len(ok_ancs_line) == 0 or not ok_ancs_line.startswith('8'):
            return
        self.process_ancs_notification(ok_ancs_line)

    def process_line_from_hm_10(self, raw_hm_10_bits):
        try:
            raw_hm_10_str: str = raw_hm_10_bits.decode('utf-8')
        except UnicodeDecodeError as e:
            print('encoding error', e)
            return
        if raw_hm_10_str == '':
            return
        #   Documentation suggests this should be "AT+ANCS,"
        #   but it comes out at "OK+ANCS"
        if 'OK+ANCS8' not in raw_hm_10_str:
            return

        ok_ancs_as_list: typing.List[str] = raw_hm_10_str.split('OK+ANCS')
        for ok_ancs_str in ok_ancs_as_list:
            print(ok_ancs_str)
            self.process_ok_ancs_line_from_list(ok_ancs_str)


    def run(self):
        try:
            self.setup_active_notifications()
            while True:
                #   ANCS
                ancs_message = self.serial.readline()
                print(ancs_message)
                self.process_line_from_hm_10(ancs_message)
                time.sleep(0.05)
        except KeyboardInterrupt as ke:
            pass
        finally:
            print('closing serial')
            self.serial.close()

