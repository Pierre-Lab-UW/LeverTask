class Training:
    def __init__(self, lever1, lever2, params = {}):
        self.lever1 = lever1
        self.lever2 = lever2
        self.params = params
        pass
    
    def start_event(self):
        pass
    
    def stop_event(self):
        pass        
    
    def get_param(self, param_name):
        if not param_name in self.params.keys():
            raise Exception("Param "+str(param_name)+" not found in the dict!")
        return self.params[param_name]
    
    
    