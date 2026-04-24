#create a abstract training classs similar to the one above but it only has one lever and not two
import yaml
from LeverBase import LeverBase
import time

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
        should_end: bool =  (time.time() - self.start_time) > self.get_global_param("SessionDuration", 60)*60
        if should_end:
            print(f"{self.lever1.name} training ended.")
        return should_end

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