# !/usr/bin/env python

import time
import datetime
import firebase_admin
import serial
from firebase_admin import credentials
from firebase_admin import db
from gpiozero import LED
from ancs_message import ANCSMessage
import typing

#   Initialize Firebase
firebase_admin.initialize_app(
    credentials.Certificate('accessibilitron-firebase-adminsdk-fbsvc-0bcf4b2f8e.json'),
    {
    'databaseURL': 'https://accessibilitron-default-rtdb.firebaseio.com/'
    }
)

FIREBASE_REFRESH_SECONDS = 15
HEARING_AID_PIN = 21



class Accessibilitron:

    def __init__(self):
        #   ANCS
        self.serial = None
        self.ancs_alerts: typing.List[ANCSMessage] = []

        #   FIREBASE
        self.last_refresh_time: datetime.datetime | None = None
        self.latest_firebase_data = None

        #   HEARING AID
        self.is_hearing_aid_on: bool = False
        self.hearing_aid_led = LED(HEARING_AID_PIN)

        self.setup()

    def setup(self):
        self.set_serial()
        print("SENDING \"AT\" to HM-10")
        self.serial.write("AT".encode())

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

    def process_ancs_alert(self, ancs_alert_string: str):
        ancs_alert_string = ancs_alert_string[1:]
        ancs_message_object = ANCSMessage.set_from_message_string(ancs_alert_string)
        self.ancs_alerts.append(ancs_message_object)
        print('ALERT', ancs_message_object)

    def find_details_of_alerts(self):
        for alert in self.ancs_alerts:
            if alert.details_found:
                continue

            print(f"AT+ANCS{alert.event_id}132")
            self.serial.write(f"AT+ANCS{alert.event_id}132".encode())
            alert.details_found = True
            break

    def process_read_line(self, read_line_bits):
        read_line = read_line_bits.decode('utf-8')
        if read_line == '':
            return
        #   Documentation suggests this should be "AT+ANCS,"
        #   but it comes out at "OK+ANCS"
        message_array = read_line.split('OK+ANCS')
        for message in message_array:
            if len(message) == 0:
                continue
            parameter_1 = message[0]

            if parameter_1 == '8':
                self.process_ancs_alert(message)
            else:
                print(parameter_1, message)
            continue
        self.find_details_of_alerts()


    def process_message(self, message: str):
        if not message.startswith('8'):
            return
        #   Strip the eight.
        message = message[1:]
        ancs_message_object = ANCSMessage.set_from_message_string(message)
        self.ancs_alerts.append(ancs_message_object)
        print(f"AT+ANCS{ancs_message_object.event_id}000")
        self.serial.write(f"AT+ANCS{ancs_message_object.event_id}000".encode())

    #   FIREBASE
    def get_data_from_firebase(self):
        # Get a database reference to our posts
        self.latest_firebase_data = db.reference().get()

        self.set_hearing_aid_status()
        self.latest_firebase_data = None

    def set_hearing_aid_status(self):
        if 'hearing_aid' not in self.latest_firebase_data:
            self.is_hearing_aid_on = False
            return
        self.is_hearing_aid_on = self.latest_firebase_data.get('hearing_aid').get('status') == 'ON'

        if self.is_hearing_aid_on:
            self.hearing_aid_led.on()
        else:
            self.hearing_aid_led.off()

    def is_time_for_refresh(self) -> bool:
        current_time = datetime.datetime.now()
        if self.last_refresh_time is None:
            self.last_refresh_time = current_time
            return True
        if (current_time - self.last_refresh_time).seconds >= FIREBASE_REFRESH_SECONDS:
            self.last_refresh_time = current_time
            return True
        return False

    def set_data_from_firebase(self):
        if not self.is_time_for_refresh():
            return
        # Get a database reference to our posts
        self.latest_firebase_data = db.reference().get()

        self.set_hearing_aid_status()
        self.latest_firebase_data = None

    #   PROGRAM.
    def run(self):
        try:
            while True:
                self.set_data_from_firebase()
                ancs_message = self.serial.readline()
                self.process_read_line(ancs_message)
                time.sleep(0.05)
        except KeyboardInterrupt as ke:
            pass
        finally:
            self.serial.close()


Accessibilitron().run()
