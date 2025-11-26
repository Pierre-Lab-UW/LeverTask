from typing import Callable, Optional, Dict
from ADU200 import ADU200
from Events.LeverStateChangedEvent import LeverStateChangedEvent
from Training import Training
import time
from LeverBase import LeverBase
import csv
from datetime import datetime
import os


class RatioTraining(Training):
    def __init__(
        self,
        lever1: LeverBase,
        lever2: LeverBase,
        param_file: str,
        global_param_file: str
    ) -> None:
    
        super().__init__(lever1, lever2, param_file, global_param_file)

        # per-lever press counts
        self.press_counts: Dict[str, int] = {
            self.lever1.name: 0,
            self.lever2.name: 0
        }

        # per-lever current working row
        self.cur_data: Dict[str, list] = {
            self.lever1.name: [],
            self.lever2.name: []
        }

        self.last_reset_time: float = 0
        self.start_time: float = 0
        self.should_end: bool = False
        self.last_lever_press_time: float = time.time()

        #get relay output params and store then in a dictionary, including pulse information, create one dict for each lever
        self.relay_output_params = {
            self.lever1.name: {
                "RelayOutputType": self.get_param("Lev1_RelayOutputType"),
                "RelayOutputPin": self.get_param("Lev1_RelayOutputPin"),
                "OnValue": self.get_param("Lev1_OnValue"),
            },
            self.lever2.name: {
                "RelayOutputType": self.get_param("Lev2_RelayOutputType"),
                "RelayOutputPin": self.get_param("Lev2_RelayOutputPin"),
                "OnValue": self.get_param("Lev2_OnValue"),
            }  
        }   

        # per-lever params
        self.lever_params = {
            self.lever1.name: {
                "ratio": self.get_param("Lev1_StartingRatio"),
                "base_ratio": self.get_param("Lev1_StartingRatio"),
                "step": self.get_param("Lev1_Iteration"),
                "schedule": self.get_param("Lev1_Schedule"),
                "iti": self.get_param("Lev1_ITI"),
                "timeout": self.get_param("Lev1_Timeout"),
                "relay_output_params": self.relay_output_params[self.lever1.name]
            },
            self.lever2.name: {
                "ratio": self.get_param("Lev2_StartingRatio"),
                "base_ratio": self.get_param("Lev2_StartingRatio"),
                "step": self.get_param("Lev2_Iteration"),
                "schedule": self.get_param("Lev2_Schedule"),
                "iti": self.get_param("Lev2_ITI"),
                "timeout": self.get_param("Lev2_Timeout"),
                "relay_output_params": self.relay_output_params[self.lever2.name]
            },
        }

        if self.lever_params[self.lever1.name]["schedule"] == "Fixed":
            self.lever_params[self.lever1.name]["ratio"] = self.lever_params[self.lever1.name]["step"]

        if self.lever_params[self.lever2.name]["schedule"] == "Fixed":
            self.lever_params[self.lever2.name]["ratio"] = self.lever_params[self.lever2.name]["step"]
        self.output_data_file = f"OutputData/{self.get_global_param('Subject')}_RatioTraining_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.lever_to_modify = ''

    def create_timestamped_csv(self):
        if not os.path.exists("OutputData"):
            os.makedirs("OutputData")

        header = [
            "Response (LP cumulative)",
            "Subject",
            "Cage",
            "Date",
            "ID",
            "Housing",
            "obs",
            "PiSystem",
            "RFID",
            "Sex",
            "Site",
            "StudyCode",
            "Lever Name",
            "Duration",
            "IRT",
            "Cumulative time from start", 
            "TO interval", 
            "ITI",
            "Rewarded (0/1)", 
            "RewardType",
            "Schedule"
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
        lever_cfg = self.lever_params[lever_name]

        print(f"Lever {lever_name} state changed to {new_state} after {time_since_last_change:.3f} seconds")

        if new_state == 1:  # pressed down
            self.last_lever_press_time = time.time()
            self.press_counts[lever_name] += 1

            row = [
                self.get_global_param("Subject", 0),  # Subject
                self.get_global_param("Cage", 0),  # Cage
                time.strftime("%Y-%m-%d", time.localtime()),  # current date
                self.get_global_param("ID", 0),  # ID
                self.get_global_param("Housing", 0),  # Housing
                self.get_global_param("obs", 0),  # obs
                self.get_global_param("PiSystem", 0),  # PiSystem
                self.get_global_param("RFID", 0),  # RFID
                self.get_global_param("Sex", 0),  # Sex
                self.get_global_param("Site", 0),  # Site
                self.get_global_param("StudyCode", 0),  # StudyCode
                lever_name,                # Lever name
                "-",                       # Duration (will be filled on release)
                time_since_last_change,    # IRT
                time.time() - self.start_time,  # cumulative time
                0,                         # TO interval placeholder
                lever_cfg["iti"],          # ITI
                0,                         # Reward flag (set later)
                "-",                      # Reward type (set later)
                lever_cfg["schedule"],     # schedule type
            ]
            self.cur_data[lever_name] = row

        elif new_state == 0:  # released
            self.last_lever_press_time = time.time()
            reward_flag = 0

            if self.press_counts[lever_name] >= lever_cfg["ratio"]:
                # ratio requirement met -> reward + cooldown
                reward_flag = 1

                for lever in self.press_counts.keys():    
                    self.press_counts[lever] = 0

                self.lever1.set_is_active(False)
                self.lever2.set_is_active(False)
                self.lever_to_modify = lever_name
                self.last_reset_time = time.time()
                self.set_relay(lever_name, True) # Set relay output to be on for reward
                print(f"Rewarded on {lever_name} press. Starting ITI cooldown.")

            if self.cur_data[lever_name]:
                # fill duration (time_since_last_change gives press duration here)
                self.cur_data[lever_name][12] = time_since_last_change
                self.cur_data[lever_name][-3] = reward_flag
                self.cur_data[lever_name][-2] = lever_cfg["relay_output_params"]["RelayOutputType"] if reward_flag == 1 else "-"
                self.write_row_with_index(self.output_data_file, self.cur_data[lever_name])
                self.cur_data[lever_name] = []
                

            
            

    def start_event(self):
        self.create_timestamped_csv()
        self.set_relay(self.lever1.name, False)
        self.set_relay(self.lever2.name, False)
        if self.get_param("Lev1_Active"):
            self.lever1.set_is_active(True)
            self.lever1.add_event(
                LeverStateChangedEvent("lever1_press", self.lever1, self._on_lever_state_changed)
            )
        else:
            self.lever1.set_is_active(False)

        if self.get_param("Lev2_Active"):
            self.lever2.set_is_active(True)
            self.lever2.add_event(
                LeverStateChangedEvent("lever2_press", self.lever2, self._on_lever_state_changed)
            )
        else:
            self.lever2.set_is_active(False)

        self.start_time = time.time()

    def stop_event(self):
        self.lever1.events.clear()
        self.lever2.events.clear()

    def update(self):
        now = time.time()

        if not self.lever1.active and not self.lever2.active:
            # check ITI cooldown
            elapsed = now - self.last_reset_time
            if elapsed > min(self.lever_params[self.lever1.name]["iti"],
                             self.lever_params[self.lever2.name]["iti"]):
                if self.get_param("Lev1_Active"):
                    self.lever1.set_is_active(True)
                if self.get_param("Lev2_Active"):
                    self.lever2.set_is_active(True)
                self.last_lever_press_time = time.time()
                # update ratios per lever depending on schedule
                for lever_name, cfg in self.lever_params.items():
                    if lever_name != self.lever_to_modify:
                        continue
                    if cfg["schedule"] == "Fixed":
                        cfg["ratio"] = cfg["step"]
                    elif cfg["schedule"] == "Progressive":
                        cfg["ratio"] += cfg["step"]
                    elif cfg["schedule"] == "Geometric":
                        cfg["ratio"] *= cfg["step"]

                print("Resumed levers after ITI")
                self.set_relay(lever_name, False) # Set relay output to be off after ITI period


        else:
            # timeout check
            flag = now - self.last_lever_press_time > max(
                self.lever_params[self.lever1.name]["timeout"],
                self.lever_params[self.lever2.name]["timeout"]
            )
            if self.lever1.get_state() != 1 and self.lever2.get_state() != 1:
                self.should_end = flag
                if flag:
                    # reset counters after timeout
                    self.press_counts[self.lever1.name] = 0
                    self.press_counts[self.lever2.name] = 0
                

    def set_relay(self, lever_name: str, relay_on: bool) -> None:
        params = self.relay_output_params[lever_name]
        adu = ADU200.get_instance()

        if adu is None:
            print("ADU200 instance not available. Cannot set relay.")
            return

        pin = params["RelayOutputPin"]
        if pin is None or not isinstance(pin, int) or pin < 0:
            return
        if relay_on:
            on_value = params["OnValue"]
            adu.set_relay(pin, set_open=(on_value))
        else:
            on_value = params["OnValue"]
            adu.set_relay(pin, set_open=(not on_value))
    
    
    def should_end_traning(self) -> bool:
        if self.should_end:
            print("Timed out!")
        return self.should_end or super().should_end_traning()
