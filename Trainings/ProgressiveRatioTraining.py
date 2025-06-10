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
        self.output_data_file = f"OutputData/PR{self.progressive_ratio}_data_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv"

    def update(self):
        now: float = time.time()
        
        if not self.lever1.active and not self.lever2.active:
            elapsed: float = now - self.last_reset_time
            if elapsed > self.ITI:
                self.lever1.set_is_active(True)
                self.lever2.set_is_active(True)
                self.current_ratio += self.progressive_ratio
        else:
            flag = True
            for key in self.durations:
                print(self.durations[key])
                if now - self.start_time - self.durations[key] <= self.timeout_time:
                    flag = False
                    break
            self.should_end = flag
                


        
    
    