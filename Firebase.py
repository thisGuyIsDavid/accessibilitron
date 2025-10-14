# !/usr/bin/env python
import datetime
from app import real_time_database

FIREBASE_REFRESH_SECONDS = 15
HEARING_AID_PIN = 21


class Firebase:

    def __init__(self):
        #   FIREBASE
        self.latest_firebase_data = None

        #   HEARING AID
        self.is_hearing_aid_on: bool = False

    def get_data_from_firebase(self):
        # Get a database reference to our posts
        self.latest_firebase_data = real_time_database.reference().get()
        print(self.latest_firebase_data)
        self.set_hearing_aid_status()
        self.latest_firebase_data = None

    def set_hearing_aid_status(self):
        if 'hearing_aid' not in self.latest_firebase_data:
            self.is_hearing_aid_on = False
            return
        self.is_hearing_aid_on = self.latest_firebase_data.get('hearing_aid').get('status') == 'ON'

    def listener(self, event):
        self.get_data_from_firebase()
        print(event)

    def run(self):
        database_reference = real_time_database.reference()
        database_reference.listen(self.listener)
        pass

Firebase().run()