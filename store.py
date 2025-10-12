import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate('accessibilitron-firebase-adminsdk-fbsvc-0bcf4b2f8e.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://accessibilitron-default-rtdb.firebaseio.com/'
})

class Accessibilitron:

    def __init__(self):
        self.is_hearing_aid_on: bool = False

        self.latest_firebase_data = None
        pass

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




Accessibilitron().get_data_from_firebase()




