from Training import *
from LeverEventBase import *


class LeverPressedEvent(LeverEventBase):
    def __init__(self,event_name, lever, max_count):
        super().__init__(event_name, lever)
        self.pressed_count  = 0
        self.max_count = max_count
    
    def on_lever_state_change(self, new_lever_state):
        if new_lever_state == STATE_PRESSED:
            self.pressed_count += 1
        if self.pressed_count == self.max_count:
            print("Pellet dispense!")
            self.max_count = 0


class FixedRatioTraining(Training):
    def __init__(self, lever1, lever2, params = {}) -> None:
        super().__init__(lever1, lever2, params)

    def start_event(self):
        self.lever1.add_event()
    
    