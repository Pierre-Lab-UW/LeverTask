# ...existing code...
from pathlib import Path
import sys
import importlib
import time
from typing import Dict
import yaml
import os

from LeverBase import LeverBase
from Training import Training
from SingleLeverTraining import SingleLeverTraining

# ensure project root is on sys.path so "Trainings" package is importable
#This is a jank fix, but dont remove this
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
      
class MultiLeverTraining(Training):
    def __init__(self, lever1: LeverBase, lever2: LeverBase, params_yaml_path: str, global_params_yaml_path: str):
        super().__init__(lever1, lever2, params_yaml_path, global_params_yaml_path)

        # read left/right param file paths from this training's YAML
        left_params_path = self.get_param("training_left_params", "")
        right_params_path = self.get_param("training_right_params", "")

        if not left_params_path or not right_params_path:
            print("MultiLeverTraining: 'training_left_params' and 'training_right_params' must be set in parameters")
            sys.exit(1)

        def _read_taskname_from_yaml(path: str) -> str:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Parameter file '{path}' not found")
            with open(path, 'r') as f:
                data = yaml.safe_load(f) or {}
            params = data.get('parameters', {})
            task_entry = params.get('TaskName', {})
            # TaskName in other files uses keys 'actual'/'default' pattern
            if isinstance(task_entry, dict):
                return task_entry.get('actual', task_entry.get('default', "") )
            # fallback if it's a plain string
            return task_entry or ""

        try:
            training_left = _read_taskname_from_yaml(left_params_path)
        except Exception as e:
            print(f"Error reading left training TaskName from '{left_params_path}': {e}")
            sys.exit(1)

        try:
            training_right = _read_taskname_from_yaml(right_params_path)
        except Exception as e:
            print(f"Error reading right training TaskName from '{right_params_path}': {e}")
            sys.exit(1)

        if not training_left or not training_right:
            print("MultiLeverTraining: could not determine TaskName from one of the side YAMLs")
            sys.exit(1)

        # instantiate left training (expecting a SingleLeverTraining subclass)
        try:
            module_left = importlib.import_module(f"Trainings.{training_left}")
            TrainingClassLeft = getattr(module_left, training_left)
            if not issubclass(TrainingClassLeft, SingleLeverTraining):
                print(f"MultiLeverTraining: {training_left} is not a subclass of SingleLeverTraining")
                sys.exit(1)
            self.training_left = TrainingClassLeft(lever1, left_params_path, global_params_yaml_path)
        except Exception as e:
            print(f"Error when loading left training '{training_left}': {e}")
            sys.exit(1)

        # instantiate right training
        try:
            module_right = importlib.import_module(f"Trainings.{training_right}")
            TrainingClassRight = getattr(module_right, training_right)
            if not issubclass(TrainingClassRight, SingleLeverTraining):
                print(f"MultiLeverTraining: {training_right} is not a subclass of SingleLeverTraining")
                sys.exit(1)
            self.training_right = TrainingClassRight(lever2, right_params_path, global_params_yaml_path)
        except Exception as e:
            print(f"Error when loading right training '{training_right}': {e}")
            sys.exit(1)

    def start_event(self):
        """
        This method gets called at the start of the event. 
        """
        super().start_event()
        self.training_left.start_event()
        self.training_right.start_event()

    def stop_event(self):
        """
        This method gets called when the event is stopped. 
        """ 
        super().stop_event()
        self.training_left.stop_event()
        self.training_right.stop_event()
    
    def update(self):
        """Called in a while loop. Should be overidden."""
        super().update()
        self.training_left.update()
        self.training_right.update()
    
    def should_end_traning(self) -> bool:
        '''Signals if the program should end or not. Checked in the main loop.
           
           Returns:
                Whether or not the program should end.
        '''
        return super().should_end_traning() or self.training_left.should_end_traning() or self.training_right.should_end_traning()
# ...existing code...