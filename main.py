# !/usr/bin/env python

import time

import firebase_admin
import serial
from firebase_admin import credentials
from firebase_admin import db
import datetime

# Fetch the service account key JSON file contents
cred = credentials.Certificate('accessibilitron-firebase-adminsdk-fbsvc-0bcf4b2f8e.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://accessibilitron-default-rtdb.firebaseio.com/'
})

FIREBASE_REFRESH_SECONDS = 15

class Accessibilitron:

    def __init__(self):
        self.serial = None
        self.is_hearing_aid_on: bool = False
        self.latest_firebase_data = None

        self.last_refresh_time: datetime.datetime | None = None

        self.setup()

    def setup(self):
        self.set_serial()
        # start up command to check if HM-10 is working.
        print("SENDING \"AT\" to HM-10")
        self.serial.write("AT".encode())

        self.last_refresh_time = datetime.datetime.now()

    def set_serial(self):
        self.serial = serial.Serial(
            port='/dev/ttyS0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

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

    def is_time_for_refresh(self) -> bool:
        current_time = datetime.datetime.now()
        if (current_time - self.last_refresh_time).seconds >= FIREBASE_REFRESH_SECONDS:
            self.last_refresh_time = current_time
            return True
        return False

    def set_data_from_firebase(self):
        if not self.is_time_for_refresh():
            return

    def process_read_line(self, read_line):
        read_line = read_line.decode('utf-8')
        message_array = read_line.split('OK+ANCS')
        for message in message_array:
            # messages must be nine characters long to analyze.
            if len(message) == 9:
                print(message)

    def run(self):
        while True:
            self.set_data_from_firebase()

            message = self.serial.readline()
            if message != "":
                print(message)
                self.process_read_line(message)

            time.sleep(0.05)

Accessibilitron().run()




