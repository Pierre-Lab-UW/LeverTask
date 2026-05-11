from __future__ import annotations
from typing import Type

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
        self.lever:LeverBase = lever
    
    def on_lever_initialize(self):
        '''Runs as soon as the lever initializes.'''
        pass
    
    def on_lever_update(self):
        '''Called continuously while the lever is active.'''
        pass
    
    def on_lever_state_change(self, new_lever_state, time_since_last_change):
        """
        Called when the state of the lever changes (Pressed or Unpressed).

        Parameters
        ----------
        new_lever_state : int
            The new state of the lever. 0 if the lever is not being pressed, 1 if the lever is being pressed.
        time_since_last_change : float
            The time in seconds since the last state change.
        """
        pass
    
    def on_lever_stopped():
        """
        Called when the lever is stopped(usually at the end of a training).
        """
        pass

    def on_lever_active_state_change(self, old_active_state: bool, new_active_state: bool):
        """
        Called when the active state of the lever changes.

        Parameters
        ----------
        new_active_state : bool
            The new active state of the lever. True if the lever is now active, False if the lever is now inactive.
        """
        pass


class DebugEvent(LeverEventBase):
    def on_lever_initialize(self):
        print("The lever has been created")
    def on_lever_state_change(self, new_lever_state, time_since_last_change):
        print(f"Lever {self.lever.name} state changed to {new_lever_state} after {time_since_last_change:.3f} seconds")
    def on_lever_stopped(self):
        print("Lever is no longer active")
    