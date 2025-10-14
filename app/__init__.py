import firebase_admin
from firebase_admin import credentials

#   Initialize Firebase
firebase_admin.initialize_app(
    credentials.Certificate('accessibilitron-firebase-adminsdk-fbsvc-0bcf4b2f8e.json'),
    {
        'databaseURL': 'https://accessibilitron-default-rtdb.firebaseio.com/'
    }
)

from firebase_admin import db as real_time_database
print('here')