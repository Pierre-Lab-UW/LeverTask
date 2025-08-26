from Training import Training
from LeverBase import LeverBase
import time
from datetime import datetime
import csv
import os

class DefaultTraining(Training):
    def __init__(self, lever1: LeverBase, lever2: LeverBase, yaml_path: str = None):
        super().__init__(lever1, lever2, yaml_path)
        self.output_data_file = f"OutputData/DefaultTraining_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        self._create_csv()

    def _create_csv(self):
        if not os.path.exists("OutputData"):
            os.makedirs("OutputData")
        header = ["Timestamp", "Lever", "PressDuration"]
        with open(self.output_data_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

    def start_event(self):
        from Events.LeverStateChangedEvent import LeverStateChangedEvent
        self.lever1.add_event(LeverStateChangedEvent(
            "lever1_event", self.lever1,
            lambda lever, new_state, t: self._on_lever_state_changed(lever, new_state, t)
        ))
        self.lever2.add_event(LeverStateChangedEvent(
            "lever2_event", self.lever2,
            lambda lever, new_state, t: self._on_lever_state_changed(lever, new_state, t)
        ))
        self.lever1.set_is_active(True)
        self.lever2.set_is_active(True)
        print("This is the Default training. Use this to test if the levers are functional.")

    def _on_lever_state_changed(self, lever: LeverBase, new_state: int, time_since_last_change: float):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if new_state == 1:  # pressed
            print(f"[{timestamp}] {lever.name} pressed.")
        else:  # released
            print(f"[{timestamp}] {lever.name} released after {time_since_last_change:.3f} seconds.")
            self._log_press(timestamp, lever.name, time_since_last_change)

    def _log_press(self, timestamp: str, lever_name: str, duration: float):
        with open(self.output_data_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, lever_name, f"{duration:.3f}"])

    def stop_event(self):
        print("Default training stopped.")

    def update(self):
        # Nothing to update in this simple training
        pass

    def should_end_traning(self) -> bool:
        return False
