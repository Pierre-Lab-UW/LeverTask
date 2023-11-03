class LeverEventBase:
    def __init__(self, event_name, lever):
        self.name = event_name
        self.lever = lever
    
    def __eq__(self, other):
        return other.name == self.name
    
    def on_lever_initialize(self):
        pass
    
    def on_lever_update(self):
        pass
    
    def on_lever_state_change(self, new_lever_state):
        pass
    
    def on_lever_stopped():
        pass


class DebugEvent(LeverEventBase):
    def on_lever_initialize(self):
        print("The lever has been created")
    def on_lever_state_change(self, new_lever_state):
        print("Lever "+self.lever.name+" state has been changed to "+str(new_lever_state))
    def on_lever_stopped(self):
        print("Lever is no longer active")
    