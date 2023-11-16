from LeverEventBase import LeverEventBase

STATE_UNPRESSED = 0
STATE_PRESSED = 1

class LeverBase():
    def __init__(self,leverName):
        self.events = []
        #0 means lever isn't pressed, 1 means it has been pressed
        self.state = STATE_UNPRESSED
        self.name = leverName
        self.active = True
    
    def get_state(self):
        return self.state
    
    def set_state(self, state):
        #check if the state is already currently set to what we want to prevent events form running every frame
        self.state = state
        for ev in self.events:
            ev.on_lever_state_change(self.state)
            
    def update_state_continously(self):
        pass
    
    def update(self):
        self.update_state_continously()
        for ev in self.events:
            ev.on_lever_update()
    
    def add_event(self, event):
        if not isinstance(event, LeverEventBase):
            raise Exception("{event} must be a LeverEventBase!")
        if event in self.events:
            raise Exception(event.name + " is already in the events for this lever!")
        self.events.append(event)
            
    def set_is_availiable(self, val):
        self.active = val
    
    