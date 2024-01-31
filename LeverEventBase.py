class LeverEventBase:
    '''
    The LeverEventBase class contains different callback functions for the lever that can be overrided for custom use.
    
    Args:
        event_name (str): The name of the event. Used in order to prevent duplicate events from being ran on an event.
        lever (LeverBase): The LeverBase object that will run this event.
    Attributes:
        name (str): The name of the event.
        lever (LeverBase) The Lever that this event is attached to.
    '''
    def __init__(self, event_name:str, lever):
        self.name:str = event_name
        self.lever = lever
    
    def on_lever_initialize(self):
        '''Runs as soon as the lever initializes.'''
        pass
    
    def on_lever_update(self):
        '''Called continuously while the lever is active.'''
        pass
    
    def on_lever_state_change(self, new_lever_state):
        """
        Called when the state of the lever changes(Pressed or Unpressed).

        Parameters
        ----------
        state : int 
            The new state of the lever. 0 if the lever is not being pressed, 1 if the lever is being pressed.
        """
        pass
    
    def on_lever_stopped():
        """
        Called when the lever is stopped(usually at the end of a training).
        """
        pass


class DebugEvent(LeverEventBase):
    def on_lever_initialize(self):
        print("The lever has been created")
    def on_lever_state_change(self, new_lever_state):
        print("Lever "+self.lever.name+" state has been changed to "+str(new_lever_state))
    def on_lever_stopped(self):
        print("Lever is no longer active")
    