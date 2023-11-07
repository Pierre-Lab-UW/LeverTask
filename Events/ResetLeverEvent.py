from LeverEventBase import *
import time


class ResetLeverEvent(LeverEventBase):
    def __init__(self, event_name, lever, update_duration):
        super().__init__(event_name, lever)
        self.last_state_change = time.time()
        self.time_to_update = update_duration
    
    def on_lever_update(self):
        cur_time = time.time()
        print(cur_time - self.last_state_change)
        print(cur_time - self.last_state_change >= self.time_to_update)
        if (cur_time - self.last_state_change >= self.time_to_update and self.lever.state == 1):
            print('fwfw')
            self.lever.switch_state()
            self.last_state_change = cur_time