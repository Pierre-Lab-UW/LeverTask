class LeverBase():
    def __init__(self):
        self.events = []
        #0 means lever isn't pressed, 1 means it has been pressed
        self.state = 0
        
    def listen_for_input(self):
        pass
    
    def execute_events(self):
        for ev in events():
            ev.execute(state)

    def set_state(self, newState):
        if newState != 0 or newState != 1:
            raise Exception("Invalid State value!")
        self.state = newState
        #inherited classeses will actually make the lever move based on the state