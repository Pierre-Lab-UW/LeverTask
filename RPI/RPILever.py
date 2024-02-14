from LeverBase import LeverBase

class RPILever(LeverBase):
    def __init__(self, lever_name: str):
        super().__init__(lever_name)
    
    def update_state_continously(self):
        pass
        #check for state via output pin of lever
    
    def set_is_active(self, val: bool):
        super().set_is_active(val)
        #Set relay voltage to this
