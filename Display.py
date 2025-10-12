from gpiozero import LED
from config import HEARING_AID_PIN


class Display:

    def __init__(self):
        self.hearing_aid_light = LED(HEARING_AID_PIN)
        self.missed_call_light = None

    def set_hearing_aid_light(self, is_hearing_aid_on: bool):
        self.hearing_aid_light.on() if is_hearing_aid_on else self.hearing_aid_light.off()

    def set_missed_call_light(self, has_missed_call: bool):
        pass