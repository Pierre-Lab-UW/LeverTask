import importlib
import sys
import os
from typing import Any
import yaml

from ADU200 import ADU200
import LeverBase

class TrainingRunnerBase:
    def __init__(self, input_args: list[str]):
        self.global_params: dict[str, any] = {}
        self.training_params: dict[str, any] = {}
        self.parse_input_file(input_args)

    def parse_input_file(self, args: list[str]):
        if len(args) < 2:
            print("Usage: python main.py <GlobalParamFile>")
            sys.exit(1)
        
        param_file: str = args[1]

        if not os.path.exists(param_file):
            print(f"❌ Error: File not found -> {param_file}")
            sys.exit(1)
        
        #load in global and training params from yaml file
        with open(param_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
            # Use 'actual' value if present, else 'default'
            if not 'parameters_global' in yaml_data:
                raise KeyError(f"'parameters_global' key not found in {param_file}")
            #load in the global parameters fromt the file
            self.global_params = {k: v.get('actual', v.get('default')) for k, v in yaml_data['parameters_global'].items()}
            
            #get the parameter string that can be used to index the parameter file for the Current Training Params
            param_key = 'parameters_' + self.global_params.get('TaskName', None)
            if param_key is None:
                raise KeyError(f"'ParamsToLoad' key not found in global parameters of {param_file}")
            if not param_key in yaml_data:
                raise KeyError(f"'{param_key}' key not found in {param_file}")

            self.training_params = {k: v.get('actual', v.get('default')) for k, v in yaml_data[param_key].items()}

    def get_training_class_instance(self) -> Any:
        training_class_name: str = self.global_params.get('TaskName', {})
        TrainingClass = None
        try:
            training_module = importlib.import_module(f"Trainings.{training_class_name}")
            TrainingClass = getattr(training_module, training_class_name)
        except (ModuleNotFoundError, AttributeError):
            print(f"Could not find training class '{training_class_name}' in Trainings/{training_class_name}.py")
            sys.exit(1)
            return None
        return TrainingClass

    def run(self):
        ADU200.get_instance()

    def on_finish(self):
        print("Training finished. Performing cleanup...")
        ADU200.get_instance().disconnect()