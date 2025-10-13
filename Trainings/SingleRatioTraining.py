from typing import Dict
from Events.LeverStateChangedEvent import LeverStateChangedEvent
from SingleLeverTraining import SingleLeverTraining
import time
from LeverBase import LeverBase
import csv
from datetime import datetime
import os


class SingleRatioTraining(SingleLeverTraining):
    def __init__(self, lever1: LeverBase, params_yaml_path: str, global_params_yaml_path: str) -> None:
        super().__init__(lever1, params_yaml_path, global_params_yaml_path)

        # press count only for one lever
        self.press_count: int = 0

        # holds the row being built for the current press/release
        self.cur_data: list = []

        self.last_reset_time: float = 0
        self.start_time: float = 0
        self.should_end: bool = False
        self.last_lever_press_time: float = time.time()

        # single lever params
        self.lever_params = {
            "ratio": self.get_param("Lev1_StartingRatio"),
            "base_ratio": self.get_param("Lev1_StartingRatio"),
            "step": self.get_param("Lev1_Iteration"),
            "schedule": self.get_param("Lev1_Schedule"),
            "iti": self.get_param("Lev1_ITI"),
            "timeout": self.get_param("Lev1_Timeout"),
        }

        # If schedule is fixed, ratio = step
        if self.lever_params["schedule"] == "Fixed":
            self.lever_params["ratio"] = self.lever_params["step"]

        self.output_data_file = (
            f"OutputData/{self.get_global_param('Subject')}_SingleRatioTraining_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

    def create_timestamped_csv(self):
        if not os.path.exists("OutputData"):
            os.makedirs("OutputData")

        header = [
            "Response (LP cumulative)", "Lever Name", "Duration", "IRT",
            "Cumulative time from start", "TO interval", "ITI",
            "Rewarded (0/1)", "Schedule"
        ]
        with open(self.output_data_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
        print(f"CSV file '{self.output_data_file}' created successfully.")

    def write_row_with_index(self, filename, row_data):
        index = 0
        file_exists = os.path.exists(filename)
        if file_exists:
            with open(filename, 'r', newline='') as f:
                index = sum(1 for _ in f) - 1

        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists or os.stat(filename).st_size == 0:
                raise Exception("Invalid file name!")
            row_with_index = [index] + row_data
            writer.writerow(row_with_index)

    def _on_lever_state_changed(self, lever: LeverBase, new_state: int, time_since_last_change: float):
        if not lever.active:
            return

        lever_name = lever.name
        cfg = self.lever_params

        print(f"Lever {lever_name} state changed to {new_state} after {time_since_last_change:.3f} seconds")

        if new_state == 1:  # pressed down
            self.last_lever_press_time = time.time()
            self.press_count += 1

            row = [
                lever_name,                # Lever name
                "-",                       # Duration (filled on release)
                time_since_last_change,    # IRT
                time.time() - self.start_time,  # cumulative time
                0,                         # TO interval placeholder
                cfg["iti"],                # ITI
                0,                         # Reward flag
                cfg["schedule"],           # schedule type
            ]
            self.cur_data = row
            print(f"{lever_name} Count: {self.press_count}")

        elif new_state == 0:  # released
            self.last_lever_press_time = time.time()
            reward_flag = 0

            if self.press_count >= cfg["ratio"]:
                reward_flag = 1
                self.press_count = 0
                lever.set_is_active(False)
                self.last_reset_time = time.time()
                print(f"Cooldown for Lever {lever_name} for {cfg['iti']} seconds")

            if self.cur_data:
                self.cur_data[1] = time_since_last_change
                self.cur_data[-2] = reward_flag
                self.write_row_with_index(self.output_data_file, self.cur_data)
                self.cur_data = []

    def start_event(self):
        self.create_timestamped_csv()

        if self.get_param("Lev1_Active", True):
            self.lever1.set_is_active(True)
            self.lever1.add_event(
                LeverStateChangedEvent("lever1_press", self.lever1, self._on_lever_state_changed)
            )
        else:
            self.lever1.set_is_active(False)

        self.start_time = time.time()

    def stop_event(self):
        self.lever1.events.clear()

    def update(self):
        super().update()
        now = time.time()

        # if lever is inactive, check for ITI cooldown
        if not self.lever1.active:
            elapsed = now - self.last_reset_time
            if elapsed > self.lever_params["iti"]:
                if self.get_param("Lev1_Active", True):
                    self.lever1.set_is_active(True)
                self.last_lever_press_time = time.time()

                # update ratio if needed
                cfg = self.lever_params
                if cfg["schedule"] == "Fixed":
                    cfg["ratio"] = cfg["step"]
                elif cfg["schedule"] == "Progressive":
                    cfg["ratio"] += cfg["step"]
                elif cfg["schedule"] == "Geometric":
                    cfg["ratio"] *= cfg["step"]

                print("Resumed lever after ITI")

        else:
            # timeout check
            timeout = self.lever_params["timeout"]
            if (now - self.last_lever_press_time) > timeout and self.lever1.get_state() != 1:
                self.should_end = True
                self.press_count = 0

    def should_end_traning(self) -> bool:
        if self.should_end:
            print("Timed out!")
        return self.should_end or super().should_end_traning()
