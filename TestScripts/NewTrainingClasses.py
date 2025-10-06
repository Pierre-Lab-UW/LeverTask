from LeverBase import LeverBase
from Training import Training
import yaml
import time
import importlib
import sys
from typing import Dict

#create a abstract training classs similar to the one above but it only has one lever and not two
class SingleLeverTraining():
    def __init__(self, lever1: LeverBase, params_yaml_path: str, global_params_yaml_path: str):
        self.lever1: LeverBase = lever1
        self.start_time: float = 0.0    
        # Load parameters from YAML file
        with open(params_yaml_path, 'r') as f:  
            yaml_data = yaml.safe_load(f)
            # Use 'actual' value if present, else 'default'
            self.params = {k: v.get('actual', v.get('default')) for k, v in yaml_data['parameters'].items()}
            with open(global_params_yaml_path, 'r') as f:
                yaml_data = yaml.safe_load(f)
                # Use 'actual' value if present, else 'default'
                self.global_params = {k: v.get('actual', v.get('default')) for k, v in yaml_data['parameters'].items()} 
    def start_event(self):
        """
        This method gets called at the start of the event. 
        """
        pass            
    def stop_event(self):
        """
        This method gets called when the event is stopped. 
        """ 
        pass
    def update(self):
        """Called in a while loop. Should be overidden."""
        self.lever1.update()
    def should_end_traning(self) -> bool:
        '''Signals if the program should end or not. Checked in the main loop.
           
           Returns:
                Whether or not the program should end.
        '''
        return (time.time() - self.start_time) > self.get_global_param("SessionLength", 60)*60

    def get_param(self, param_name, default=None):
       '''Gets the value of a parameter.
           
         Parameters
         ----------
             param_name : str 
             The name of the param we want.
             default : any
             The default value to return if param is not found.

         Returns:
             The value of the specified parameter for this training, or default if not found.
       '''
       return self.params.get(param_name, default)

    def get_global_param(self, param_name, default=None):
        '''Gets the value of a global parameter.

         Parameters
         ----------
             param_name : str
             The name of the global param we want.
             default : any
             The default value to return if param is not found.

         Returns:
             The value of the specified global parameter for this training, or default if not found.
       '''
        return self.global_params.get(param_name, default)

class MultiLeverTraining(Training):
    def __init__(self, lever1: LeverBase, lever2: LeverBase, params_yaml_path: str, global_params_yaml_path: str, training_left: str, training_right: str, training_left_params: str, training_right_params: str):
        super().__init__(lever1, lever2, params_yaml_path, global_params_yaml_path)
        try:
            training_module = importlib.import_module(f"Trainings.{training_left}")
            TrainingClassLeft = getattr(training_module, training_left)
            if not issubclass(TrainingClassLeft, SingleLeverTraining):  
                print(f"{training_left} is not a subclass of SingleLeverTraining")
                sys.exit(1)
            self.training_left = TrainingClassLeft(lever1, training_left_params, global_params_yaml_path)
        except Exception as e:
            print(f"Error when loading training class '{training_left}': {e}")
            sys.exit(1)

        try:
            training_module = importlib.import_module(f"Trainings.{training_right}")
            TrainingClassRight = getattr(training_module, training_right)
            if not issubclass(TrainingClassRight, SingleLeverTraining):
                print(f"{training_right} is not a subclass of SingleLeverTraining")
                sys.exit(1)
            self.training_right = TrainingClassRight(lever2, training_right_params, global_params_yaml_path)
        except Exception as e:
            print(f"Error when loading training class '{training_right}': {e}")
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
    