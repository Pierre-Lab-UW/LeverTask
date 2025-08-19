from LeverBase import LeverBase
from typing import Dict
import yaml

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
    def __init__(self, lever1: LeverBase, lever2: LeverBase, yaml_path: str):
        self.lever1: LeverBase = lever1
        self.lever2: LeverBase = lever2
        # Load parameters from YAML file
        with open(yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        # Use 'actual' value if present, else 'default'
        self.params = {k: v.get('actual', v.get('default')) for k, v in yaml_data['parameters'].items()}


    
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
    
    def update(self):
        """Called in a while loop. Should be overidden."""
        pass

    def should_end_traning(self) -> bool:
        '''Signals if the program should end or not. Checked in the main loop.
           
           Returns:
                Whether or not the program should end.
        '''
        return False