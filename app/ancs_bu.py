# !/usr/bin/env python
import time
import typing
import datetime
import serial

from Display import Display
from Firebase import Firebase

from config import REFRESH_SECONDS

from app.ANCSNotification import ANCSNotification


class CallNotifier:
    def __init__(self):
        #   META
        self.last_refresh_time: datetime.datetime = None

        #   Firebase
        self.firebase = Firebase()

        #   Display
        self.display = Display()

        #   ANCS
        self.serial = None
        self.active_notifications: typing.List[ANCSNotification] = []

        self.setup()

    def setup(self):
        #   ANCS
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
        print("Setting up active notifications.")
        self.serial.write("AT".encode())

    def find_details_of_active_ancs_notifications(self):
        notifications_to_detail = [
            x for x in self.active_notifications
            if not x.has_details() and not x.has_been_queried
        ]
        if len(notifications_to_detail) == 0:
            return
        notification_to_detail = notifications_to_detail[0]

        query_string = notification_to_detail.get_query_string()
        print(f"SENDING:", query_string)
        self.serial.write(query_string.encode())

    def process_ancs_notification(self, ancs_notification_string: str):
        ancs_notification_string = ancs_notification_string[1:]
        ancs_message_object = ANCSNotification.set_from_message_string(ancs_notification_string)

        if ancs_message_object.action == 'ADDED':
            #   When the phone reconnects, the "old" messages will not get removed.
            #   We must check for events already existing.
            event_ids_in_notifications = set([x.event_id for x in self.active_notifications])
            if ancs_message_object.event_id in event_ids_in_notifications:
                return
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
                print(active_notification, datetime.datetime.now())

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

    #   STATUSES
    def has_missed_calls(self) -> bool:
        missed_call_alerts = [x for x in self.active_notifications if x.category == 'MISSED CALL']
        return len(missed_call_alerts) > 0

    def is_time_for_refresh(self) -> bool:
        current_time = datetime.datetime.now()
        if self.last_refresh_time is None:
            self.last_refresh_time = current_time
            return True
        if (current_time - self.last_refresh_time).seconds >= REFRESH_SECONDS:
            self.last_refresh_time = current_time
            return True
        return False

    def set_display(self):
        self.display.set_hearing_aid_light(
            self.firebase.is_hearing_aid_on
        )
        self.display.set_missed_call_light(
            self.has_missed_calls()
        )

    def run(self):
        try:
            self.setup_active_notifications()
            while True:
                #   ANCS
                ancs_message = self.serial.readline()
                self.process_line_from_hm_10(ancs_message)
                time.sleep(0.05)
        except KeyboardInterrupt as ke:
            pass
        finally:
            self.serial.close()


CallNotifier().run()
