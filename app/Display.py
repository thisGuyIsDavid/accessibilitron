from gpiozero import LED
from config import HEARING_AID_PIN


class Display:

    def __init__(self):
        self.hearing_aid_light = LED(HEARING_AID_PIN)

    def set_hearing_aid_light(self, is_hearing_aid_on: bool):
        if is_hearing_aid_on:
            self.hearing_aid_light.on()
        else:
            self.hearing_aid_light.off()
