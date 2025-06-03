from typing import Callable, Optional, Dict
from Events.LeverPressedEvent import LeverPressedEvent
from Training import Training
import time
from LeverBase import LeverBase, STATE_PRESSED


class FixedRatioTraining(Training):
    def __init__(
        self,
        lever1: LeverBase,
        lever2: LeverBase,
        params: Dict[str, int] = {}
    ) -> None:
        super().__init__(lever1, lever2, params)
        self.press_counts: Dict[str, int] = {
            self.lever1.name: 0,
            self.lever2.name: 0
        }
        self.last_reset_times: Dict[str, float] = {
            self.lever1.name: 0.0,
            self.lever2.name: 0.0
        }

    def _on_lever_pressed(self, lever: LeverBase):
        if not lever.active:
            return

        self.press_counts[lever.name] += 1
        print(f"{lever.name} Count: {self.press_counts[lever.name]}")

        if self.press_counts[lever.name] >= self.get_param("lever_presses"):
            print("Pellet dispense!")
            self.press_counts[lever.name] = 0
            lever.set_is_active(False)
            self.last_reset_times[lever.name] = time.time()

    def start_event(self):
        self.lever1.add_event(
            LeverPressedEvent("lever1_press", self.lever1, self._on_lever_pressed)
        )
        self.lever2.add_event(
            LeverPressedEvent("lever2_press", self.lever2, self._on_lever_pressed)
        )

    def stop_event(self):
        self.lever1.events.clear()
        self.lever2.events.clear()

    def update(self):
        now: float = time.time()
        for lever in [self.lever1, self.lever2]:
            if not lever.active:
                elapsed: float = now - self.last_reset_times[lever.name]
                if elapsed > self.get_param("update_interval"):
                    lever.set_is_active(True)

        
    
    