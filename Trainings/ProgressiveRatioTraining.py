from typing import Dict
import time
from LeverBase import LeverBase, STATE_PRESSED
from datetime import datetime
from Trainings.FixedRatioTraining import FixedRatioTraining

class ProgressiveRatioTraining(FixedRatioTraining):
    def __init__(
        self,
        lever1: LeverBase,
        lever2: LeverBase,
        params: Dict[str, int] = {}
    ) -> None:
        
        super().__init__(lever1, lever2, params)

        self.progressive_ratio = self.get_param("PR")
        self.output_data_file = "OutputData/PR{}_data_{}.csv".format(
            self.current_ratio, datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            )

    def update(self):
        now: float = time.time()
        
        if not self.lever1.active and not self.lever2.active:
            elapsed: float = now - self.last_reset_time
            if elapsed > self.ITI:
                self.lever1.set_is_active(True)
                self.lever2.set_is_active(True)
                self.current_ratio += self.progressive_ratio
        else:
            #timeout logic - program will only timeout if any lever hasn't been pressed in the past [Timeout] seconds
            #will not timeout if monkey is holding lever for an extended amount of time, also the ITI cooldown is not counted in the timeout
            flag = True
            if now - self.last_lever_press_time <= self.timeout_time:
                flag = False
            if self.lever1.get_state() != 1 and self.lever2.get_state() != 1:
                self.should_end = flag
                


        
    
    