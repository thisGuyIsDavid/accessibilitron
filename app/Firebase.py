# !/usr/bin/env python
import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from gpiozero import LED

#   Initialize Firebase
firebase_admin.initialize_app(
    credentials.Certificate('accessibilitron-firebase-adminsdk-fbsvc-0bcf4b2f8e.json'),
    {
        'databaseURL': 'https://accessibilitron-default-rtdb.firebaseio.com/'
    }
)

FIREBASE_REFRESH_SECONDS = 15
HEARING_AID_PIN = 21

class Firebase:

    def __init__(self):
        #   FIREBASE
        self.last_refresh_time: datetime.datetime = None
        self.latest_firebase_data = None

        #   HEARING AID
        self.is_hearing_aid_on: bool = False
        self.hearing_aid_led = LED(HEARING_AID_PIN)

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
