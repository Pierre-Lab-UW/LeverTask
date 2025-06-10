from typing import Callable, Optional, Dict
from Events.LeverStateChangedEvent import LeverStateChangedEvent
from Training import Training
import time
from LeverBase import LeverBase, STATE_PRESSED
import csv
from datetime import datetime
import os

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

        self.durations: Dict[str, int] = {
            self.lever1.name: 0,
            self.lever2.name: 0
        }
        
        self.lever1_cur_data: list[any] = []
        self.lever2_cur_data: list[any] = []

        self.last_reset_time: int = 0
        self.current_ratio = self.get_param("FR")

        self.output_data_file = f"OutputData/FR{self.current_ratio}_data_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv"
        self.start_time = 0

        self.ITI = self.get_param("ITI")
        self.timeout_time = self.get_param("Timeout")
        self.should_end = False

    def create_timestamped_csv(self):

        if not os.path.exists("OutputData"):
    
            # if the demo_folder directory is not present 
            # then create it.
            os.makedirs("OutputData")


        header=["Response (LP cumulative)","Lever Name", "Duration", "IRT", "Cumulative time from start", "TO interval", "ITI", "Rewarded (0/1)", "Schedule"]
        # Get current time down to the second
        # Write data to CSV
        with open(self.output_data_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            if header:
                writer.writerow(header)

        print(f"CSV file '{self.output_data_file}' created successfully.")

    def write_row_with_index(self, filename, row_data):
        index = 0
        file_exists = os.path.exists(filename)

        if file_exists:
            with open(filename, 'r', newline='') as f:
                index = sum(1 for _ in f) - 1  # header row doesn't count

        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists or os.stat(filename).st_size == 0:
                raise Exception("Invalid file name!")

            # Insert index into the first column ("Response (LP cumulative)")
            row_with_index = [index] + row_data
            writer.writerow(row_with_index)


    def _on_lever_state_changed(self, lever: LeverBase, new_state: int):
        if not lever.active:
            return
        if new_state == 1:        
            self.press_counts[lever.name] += 1
            #record data
            cur_duration:int = time.time() - self.durations[lever.name]
            row = [lever.name, -1, cur_duration, time.time() - self.start_time, 0, self.ITI, 0, self.current_ratio]
            if self.durations[lever.name] == 0:
                row[2] = "-"

            

            if self.lever1.name == lever.name:
                self.lever1_cur_data = row
            elif self.lever2.name == lever.name:
                self.lever2_cur_data = row
            else:
                raise Exception("Lever name doesn't match!")

            self.durations[lever.name] = time.time()
            
            print(f"{lever.name} Count: {self.press_counts[lever.name]}")
            
        else:
            #record button press data
            cur_time:float = time.time()
            button_pressed_dur: int =  cur_time - self.durations[lever.name]
            reward_flag = 0

            if self.press_counts[lever.name] >= self.current_ratio:
                print("Cooldown!")
                self.press_counts[lever.name] = 0
                self.lever1.set_is_active(False)
                self.lever2.set_is_active(False)
                self.last_reset_time = time.time()
                reward_flag = 1

            if lever.name == self.lever1.name:
                self.lever1_cur_data[1] = button_pressed_dur
                self.lever1_cur_data[-2] = reward_flag
                self.write_row_with_index(self.output_data_file, self.lever1_cur_data)
            elif self.lever2.name == lever.name:
                self.lever2_cur_data[1] = button_pressed_dur
                self.lever2_cur_data[-2] = reward_flag
                self.write_row_with_index(self.output_data_file, self.lever2_cur_data)
            else:
                raise Exception("Lever name doesn't match!")

            

    def start_event(self):
        self.create_timestamped_csv()
        self.lever1.add_event(
            LeverStateChangedEvent("lever1_press", self.lever1, self._on_lever_state_changed)
        )
        self.lever2.add_event(
            LeverStateChangedEvent("lever2_press", self.lever2, self._on_lever_state_changed)
        )
        self.start_time = time.time()

    def stop_event(self):
        self.lever1.events.clear()
        self.lever2.events.clear()

    def update(self):
        now: float = time.time()
        if not self.lever1.active and not self.lever2.active:
            elapsed: float = now - self.last_reset_time
            if elapsed > self.ITI:
                self.lever1.set_is_active(True)
                self.lever2.set_is_active(True)
        else:
            flag = True
            for key in self.durations:
                if now - self.start_time - self.durations[key] <= self.timeout_time:
                    flag = False
                    break
            self.should_end = flag
                

    def should_end_traning(self) -> bool:
        if self.should_end:
            print("Timed out!")
        return self.should_end
        
    
    