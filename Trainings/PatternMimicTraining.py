from Training import Training
from LeverBase import LeverBase, STATE_PRESSED, STATE_UNPRESSED
import random
import time
from datetime import datetime
import csv
import os

class PatternMimicTraining(Training):
    def __init__(self, lever1: LeverBase, lever2: LeverBase, yaml_path: str, global_param_file: str):
        super().__init__(lever1, lever2, yaml_path, global_param_file)
        self.pattern_length = self.get_param("PatternLength", 5)
        self.pattern = [random.choice([0, 1]) for _ in range(self.pattern_length)]
        self.current_index = 0
        self.start_time = time.time()
        self.should_end = False
        self.timeout_time = self.get_param("Timeout", 10)
        self.display_time = self.get_param("DisplayTime", 2)  # seconds
        self.last_lever_press_time = time.time()
        self.active_levers = [self.lever1.name, self.lever2.name]
        self.displaying_pattern = False
        self.entered_pattern = []
        self.attempt_start_time = time.time()
        self.output_data_file = f"OutputData/PatternMimic_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        self._create_csv()
    def _create_csv(self):
        import os, csv
        if not os.path.exists("OutputData"):
            os.makedirs("OutputData")
        header = ["Pattern", "EnteredPattern", "TimeTaken", "Correct"]
        with open(self.output_data_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

    def start_event(self):
        self._display_pattern()
        self.start_time = time.time()
        from Events.LeverStateChangedEvent import LeverStateChangedEvent
        self.lever1.add_event(LeverStateChangedEvent("lever1_press", self.lever1, lambda lever, new_state, time_since_last_change: self._on_lever_state_changed(0, new_state, time_since_last_change)))
        self.lever2.add_event(LeverStateChangedEvent("lever2_press", self.lever2, lambda lever, new_state, time_since_last_change: self._on_lever_state_changed(1, new_state, time_since_last_change)))
        self.lever1.set_is_active(True)
        self.lever2.set_is_active(True)
        
    def _display_pattern(self):
        print(f"Pattern to mimic: {self.pattern}")
        self.lever1.set_is_active(False)
        self.lever2.set_is_active(False)
        self.displaying_pattern = True
        self.display_start_time = time.time()

    def _on_lever_state_changed(self, lever_value, new_state, time_since_last_change):
        now = time.time()
        # Only count as a press when new_state == 0
        if new_state != 0:
            return
        print(f"Lever {lever_value} state changed after {time_since_last_change:.3f} seconds")
        # Timeout logic
        if now - self.last_lever_press_time > self.timeout_time:
            print("Timed out! Generating new pattern.")
            self._store_attempt(correct=False, timed_out=True)
            self._reset_pattern()
            return
        expected = self.pattern[self.current_index]
        self.entered_pattern.append(lever_value)
        if lever_value == expected:
            self.current_index += 1
            self.last_lever_press_time = now
            if self.current_index >= self.pattern_length:
                print("Pattern complete! Generating new pattern.")
                self._store_attempt(correct=True, timed_out=False)
                self._reset_pattern()
        else:
            print(f"Pattern wrong at step {self.current_index+1}! Expected {expected}, got {lever_value}. Generating new pattern.")
            self._store_attempt(correct=False, timed_out=False)
            self._reset_pattern()
    def _store_attempt(self, correct, timed_out):
        import csv
        time_taken = time.time() - self.attempt_start_time
        pattern_str = ''.join(str(x) for x in self.pattern)
        entered_str = ''.join(str(x) for x in self.entered_pattern)
        with open(self.output_data_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([pattern_str, entered_str, time_taken, correct and not timed_out])
        self.entered_pattern = []
        self.attempt_start_time = time.time()

    def _reset_pattern(self):
        self.pattern = [random.choice([0, 1]) for _ in range(self.pattern_length)]
        self.current_index = 0
        self.last_lever_press_time = time.time()
        self.entered_pattern = []
        self.attempt_start_time = time.time()
        self._display_pattern()

    def stop_event(self):
        pass

    def update(self):
        now = time.time()
        # Handle display time for pattern
        if self.displaying_pattern:
            if now - self.display_start_time >= self.display_time:
                self.lever1.set_is_active(True)
                self.lever2.set_is_active(True)
                self.displaying_pattern = False
                print("Levers are now active. You may begin mimicking the pattern.")
            else:
                return
        # No data collection, just lever event system and timeout
        if now - self.last_lever_press_time > self.timeout_time:
            print("Timed out! Generating new pattern.")
            self._reset_pattern()

    def should_end_traning(self) -> bool:
        return False
