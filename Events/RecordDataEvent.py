from LeverEventBase import *
import time

class RecordDataEvent(LeverEventBase):
    def __init__(self, event_name, lever):
        super().__init__(event_name, lever)
        self.timestamps = {}
        self.start_time = time.time()
        self.timestamps[0] = lever.get_state()
        
    def on_lever_state_change(self, new_lever_state):
        self.timestamps[time.time()-self.start_time] = new_lever_state
        #print(self.timestamps)