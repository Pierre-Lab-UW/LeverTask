from LeverEventBase import LeverEventBase

class LeverBase():
    def __init__(self,leverName):
        self.events = []
        #0 means lever isn't pressed, 1 means it has been pressed
        self.state = 0
        self.name = leverName
        
    def switch_state(self):
        if self.state == 0:
            self.state = 1
        else:
            self.state = 0
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
            
    
    
    