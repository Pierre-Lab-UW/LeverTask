from LeverBase import LeverBase


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
    def __init__(self, lever1:LeverBase, lever2:LeverBase, params:dict[str, int] = {}):
        self.lever1:LeverBase = lever1
        self.lever2:LeverBase = lever2
        self.params:dict[str, int] = params
        pass
    
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
    
    def get_param(self, param_name) -> int:
        '''Gets the value of a parameter.
           
           Parameters
           ----------
                param_name : str 
                The name of the param we want.

           Returns:
                The value of the specified parameter for this training.
        '''
        if not param_name in self.params.keys():
            raise Exception("Param "+str(param_name)+" not found in the dict!")
        return self.params[param_name]
    
    
    