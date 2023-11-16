from Training import *
from LeverEventBase import LeverEventBase
from LeverBase import STATE_PRESSED, STATE_UNPRESSED


class LeverPressedEvent(LeverEventBase):
    def __init__(self,event_name, lever, max_count):
        super().__init__(event_name, lever)
        self.pressed_count  = 0
        self.max_count = max_count

    def on_lever_state_change(self, new_lever_state):
        if new_lever_state == STATE_PRESSED:
            self.pressed_count += 1
            print("Count: "+str(self.pressed_count))
        if self.pressed_count == self.max_count:
            print("Pellet dispense!")
            self.pressed_count = 0
            self.lever.set_is_availiable(False)
    
    #def on_lever_update(self):
        

#finish implementing cooldowns and showing the lever after some time
class FixedRatioTraining(Training):
    def __init__(self, lever1, lever2, params = {}) -> None:
        super().__init__(lever1, lever2, params)

    def start_event(self):
        self.lever1.add_event(LeverPressedEvent("lever_press", self.lever1, 5))
        self.lever2.add_event(LeverPressedEvent("lever_press", self.lever2, 5))

    def stop_event(self):
        self.lever1.events.clear()
        self.lever2.events.clear()
        
        
    
    