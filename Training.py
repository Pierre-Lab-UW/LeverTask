import importlib
import sys
from LeverBase import LeverBase
from typing import Dict
import yaml
import time

class Training:
    '''
    The Training class represents a specific traning event and can be used to implement new events..
    
    Args:
        lever1 (LeverBase): The first lever being used.
        lever2 (LeverBase): The second lever being used.
        params (dict[str, int]): A dictionary of parameters that can be used to create flexibility with the training.
    Attributes:
        Lever1 (LeverBase): The first lever being used.
        Lever2 (LeverBase) The second lever being used..
    '''

    @classmethod
    def from_filepath(cls, lever1: LeverBase, lever2: LeverBase, params_yaml_path: str, global_params_yaml_path: str) -> 'Training':
        """
        Factory method to create a Training instance from YAML file paths.
        """
        # Load parameters from YAML file
        with open(params_yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        # Use 'actual' value if present, else 'default'

        #check if yaml data exists
        if yaml_data is None:
            raise ValueError(f"No data found in {params_yaml_path}")

        #check if 'parameters' key exists in yaml_data to avoid KeyError
        if 'parameters' not in yaml_data:
            raise KeyError(f"'parameters' key not found in {params_yaml_path}")
        training_params = {k: v.get('actual', v.get('default')) for k, v in yaml_data['parameters'].items()}

        with open(global_params_yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        # Use 'actual' value if present, else 'default'
        global_params = {k: v.get('actual', v.get('default')) for k, v in yaml_data['parameters'].items()}
        instance = cls(lever1, lever2, training_params, global_params)
        
        return instance

    def __init__(self, lever1: LeverBase, lever2: LeverBase, params_yaml_dict: dict, global_params_dict: dict):
        self.lever1: LeverBase = lever1
        self.lever2: LeverBase = lever2
        self.params = params_yaml_dict
        self.global_params = global_params_dict
        self.start_time: float = 0.0

    def start_event(self):
        """
        This method gets called at the start of the event. 
        """
        self.start_time = time.time()
    
    def stop_event(self):
        """
        This method gets called when the event is stopped. 
        """
        pass        
    
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

       #throw an error if the parameter is not found in the training params or global params to make it more obvious that there is an issue with the yaml file
       if param_name not in self.params and param_name not in self.global_params:
           raise KeyError(f"Parameter '{param_name}' not found in training or global parameters.")
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
         #throw an error if the parameter is not found in the global params to make it more obvious that there is an issue with the yaml file
        if param_name not in self.global_params:
            raise KeyError(f"Global parameter '{param_name}' not found in global parameters.")
        return self.global_params.get(param_name, default)

    def update(self):
        """Called in a while loop. Should be overidden."""
        pass

    def should_end_traning(self) -> bool:
        '''Signals if the program should end or not. Checked in the main loop.
           
           Returns:
                Whether or not the program should end.
        '''
        return (time.time() - self.start_time) > self.get_global_param("SessionDuration", 60)*60

