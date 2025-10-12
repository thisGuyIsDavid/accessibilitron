# !/usr/bin/env python

import time
import typing
import serial
from ancs_message import ANCSMessage


class Accessibilitron:

    def __init__(self):
        #   ANCS
        self.serial = None

        self.has_completed_setup: bool = False

        self.active_ancs_notifications: typing.List[ANCSMessage] = []

        self.active_ancs_notification_to_detail: ANCSMessage = ANCSMessage | None

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

    def setup_active_alerts(self):
        if self.has_completed_setup:
            return
        print("Setting up active alerts.")
        self.serial.write("AT".encode())
        self.has_completed_setup = True

    def find_details_of_active_ancs_notifications(self):
        for active_ancs_notification in self.active_ancs_notifications:
            if active_ancs_notification.details_found:
                continue
            self.find_details_of_active_ancs_notification(active_ancs_notification)

    def find_details_of_active_ancs_notification(self, ancs_notification):
        self.active_ancs_notification_to_detail = ancs_notification

        print(f"AT+ANCS{ancs_notification.event_id}000")
        self.serial.write(f"AT+ANCS{ancs_notification.event_id}000".encode())

    def process_ancs_alert(self, ancs_alert_string: str):
        ancs_alert_string = ancs_alert_string[1:]
        ancs_message_object = ANCSMessage.set_from_message_string(ancs_alert_string)

        if ancs_message_object.action == 'ADDED':
            self.active_ancs_notifications.append(ancs_message_object)
        else:
            self.active_ancs_notifications = [
                x for x in self.active_ancs_notifications if x.event_id == ancs_message_object.event_id
            ]

    def process_ok_ancs_line_from_list(self, ok_ancs_line: str):
        if len(ok_ancs_line) == 0:
            return
        if ok_ancs_line.startswith('8'):
            self.process_ancs_alert(ok_ancs_line)
        else:
            print(ok_ancs_line)
        pass

    def process_line_from_hm_10(self, raw_hm_10_bits):
        raw_hm_10_str: str = raw_hm_10_bits.decode('utf-8')
        if raw_hm_10_str == '':
            return
        #   Documentation suggests this should be "AT+ANCS,"
        #   but it comes out at "OK+ANCS"
        ok_ancs_as_list: typing.List[str] = raw_hm_10_str.split('OK+ANCS')
        for ok_ancs_str in ok_ancs_as_list:
            self.process_ok_ancs_line_from_list(ok_ancs_str)

    def run(self):
        try:
            self.setup_active_alerts()
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
