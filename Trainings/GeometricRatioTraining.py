from typing import Dict
import time
from LeverBase import LeverBase, STATE_PRESSED
from datetime import datetime
from Trainings.FixedRatioTraining import FixedRatioTraining
from ADU200 import ADU200

class GeometricRatioTraining(FixedRatioTraining):
    def __init__(
        self,
        lever1: LeverBase,
        lever2: LeverBase,
        params: Dict[str, int] = {}
    ) -> None:
        super().__init__(lever1, lever2, params)
        self.current_ratio: float = self.get_param("GR")
        self.geometric_ratio: float = self.get_param("GR")
        self.output_data_file: str = "OutputData/GR{}_data_{}.csv".format(
            self.current_ratio, datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            )
        
    
    def update(self):
        now: float = time.time()
        
        if not self.lever1.active and not self.lever2.active:
            elapsed: float = now - self.last_reset_time
            if elapsed > self.ITI:
                self.lever1.set_is_active(True)
                self.lever2.set_is_active(True)
                self.current_ratio = int(self.current_ratio*self.geometric_ratio)
                self.last_lever_press_time = time.time()
                ADU200.get_instance().set_relay(0, False)
                print("Resume! new ratio is: "+str(self.current_ratio))
        else:
            #timeout logic - program will only timeout if any lever hasn't been pressed in the past [Timeout] seconds
            #will not timeout if monkey is holding lever for an extended amount of time, also the ITI cooldown is not counted in the timeout
            flag = True
            #print(now - self.last_lever_press_time)
            if now - self.last_lever_press_time <= self.timeout_time:
                flag = False
            if self.lever1.get_state() != 1 and self.lever2.get_state() != 1:
                self.should_end = flag