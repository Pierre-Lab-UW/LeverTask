class LeverEventBase:
    '''
    The LeverEventBase class contains different callback functions for the lever that can be overrided for custom use.
    
    Args:
        event_name (str): The name of the event. Used in order to prevent duplicate events from being ran on an event.
        lever (LeverBase): The LeverBase object that will run this event.
    Attributes:
        events (list[EventBase]): A list of events that will be executed as callback functions when something happens to the lever.
        state (int): An int that represents if the lever has been pressed or not. Should only be 0 or 1
        name (str): The name of the lever(Used for equality checking).
        active (bool): Stores if the lever can be pressed or not
    '''
    def __init__(self, event_name:str, lever):
        self.name:str = event_name
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
    