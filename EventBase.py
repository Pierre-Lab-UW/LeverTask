class LeverEventBase:
    def __init__(self, event_name):
        self.name = event_name
    
    def __eq__(self, other):
        return other.name == name
    
    def on_lever_initialize(self):
        pass
    
    def on_lever_state_change(self, lever_state):
        pass
    
    def on_lever_stopped():
        pass


class DebugEvent(LeverEventBase):
    def on_lever_initialize(self):
        print("The lever has been created")
    def on_lever_state_change(self, lever_state):
        print("State of lever has been changed to "+str(lever_state))
    def on_lever_stopped(self):
        print("Lever is no longer active")
    