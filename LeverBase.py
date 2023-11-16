from LeverEventBase import LeverEventBase

STATE_UNPRESSED = 0
STATE_PRESSED = 1

class LeverBase():
    '''
    The LeverBase class is a specification for a lever and can be inherited to create different implementations. 
    This class can be inherited and modified to work with different types of levers
    
    Args:
        leverName (str): The name of the lever.
    
    Attributes:
        events (list[EventBase]): A list of events that will be executed as callback functions when something happens to the lever.
        state (int): An int that represents if the lever has been pressed or not. Should only be 0 or 1
        name (str): The name of the lever(Used for equality checking).
        active (bool): Stores if the lever can be pressed or not
    '''
    def __init__(self,leverName):
        self.events = []
        #0 means lever isn't pressed, 1 means it has been pressed
        self.state = STATE_UNPRESSED
        self.name = leverName
        self.active = True
    
    def get_state(self) -> int:
        '''Returns the current state of the lever.
        
           Returns:
                0 if the lever isn't pressed, 1 if it is pressed
        '''
        return self.state
    
    def set_state(self, state):
        #check if the state is already currently set to what we want to prevent events form running every frame
        self.state = state
        for ev in self.events:
            ev.on_lever_state_change(self.state)
    
    def update_state_continously(self):
        """
        This function should be overridden by a sub-class and continously check and update the state of the lever. 
        """
        pass
    
    def update(self):
        """
        This function is run every frame. The base implementation calls self.update_state_continously() 
        and runs a update callback function for all the events the lever is subscribed to. 
        Don't forget to call super().update() first when overriding this method.
        """
        self.update_state_continously()
        for ev in self.events:
            ev.on_lever_update()
    
    def add_event(self, event):
        if not isinstance(event, LeverEventBase):
            raise Exception("{event} must be a LeverEventBase!")
        if event in self.events:
            raise Exception(event.name + " is already in the events for this lever!")
        self.events.append(event)
            
    def set_is_active(self, val):
        self.active = val
    
    