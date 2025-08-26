from LeverEventBase import LeverEventBase
from typing import List

STATE_UNPRESSED:int = 0
STATE_PRESSED:int = 1

class LeverBase():
    '''
    The LeverBase class is a specification for a lever and can be inherited to create different implementations. 
    This class can be inherited and modified to work with different types of levers(eg. switches, retractable)
    
    Args:
        lever_name (str): The name of the lever.
    
    Attributes:
        events (list[EventBase]): A list of events that will be executed as callback functions when something happens to the lever.
        state (int): An int that represents if the lever has been pressed or not. Should only be 0 or 1
        name (str): The name of the lever(Used for equality checking).
        active (bool): Stores if the lever can be pressed or not
    '''
    def __init__(self,lever_name: str):
        self.events: List[LeverEventBase] = []
        #0 means lever isn't pressed, 1 means it has been pressed
        self.state:int = STATE_UNPRESSED
        self.name:str = lever_name
        self.active:bool = True
        self._last_state_change_time = None
    def get_state(self) -> int:
        '''Returns the current state of the lever.

           Returns:
                0 if the lever isn't pressed, 1 if it is pressed
        '''
        return self.state
    def set_state(self, state:int):
        """
        Sets the state of the lever if it's pressed or not. 

        Parameters
        ----------
        state : int
            The value that we want to set the state to. 0 if the lever is not being pressed, 1 if the lever is being pressed.
        """
        import time
        #check if the state is already currently set to what we want to prevent events form running every frame
        if self.state != state:
            now = time.time()
            if self._last_state_change_time is None:
                time_since_last_change = 0.0
            else:
                time_since_last_change = now - self._last_state_change_time
            self._last_state_change_time = now
            self.state = state
            for ev in self.events:
                ev.on_lever_state_change(self.state, time_since_last_change)
    
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
        if self.active:
            self.update_state_continously()
        for ev in self.events:
            ev.on_lever_update()
    
    def add_event(self, event: LeverEventBase):
        """
        Adds a LeverEvent to this lever for it to execute as a callback function. 

        Parameters
        ----------
        event : LeverEventBase 
            The LeverEventBase that we want to be ran during callbacks.
        """
        if not isinstance(event, LeverEventBase):
            raise Exception("{event} must be a LeverEventBase!")
        if event in self.events:
            raise Exception(event.name + " is already in the events for this lever!")
        #TODO:check for duplicate events, use a hashmap.
        self.events.append(event)
            
    def set_is_active(self, val: bool):
        """
        Sets if the lever should process events when it is being pressed. 

        Parameters
        ----------
        val : bool 
            A boolean representing if the lever should process events when it is being pressed.
        """
        self.active = val
    
    
