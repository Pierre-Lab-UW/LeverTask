from LeverBase import LeverBase
from ADU200 import ADU200

class SwitchLever(LeverBase):
    def __init__(self, lever_name: str, relay_pin:int):
        super().__init__(lever_name)
        self.relay_pin = relay_pin #pin that reads in if the lever is being pressed

    def update_state_continously(self) -> None:
        try:
            new_state: int = ADU200.get_instance().get_port_status(self.relay_pin)
            if new_state != self.state and new_state != None:
                print(self.name+" State: "+str(new_state))
                self.set_state(new_state)
        except Exception as e:
            raise Exception("Error when trying to read lever state from ADU200: {}".format(e))
        #check for state via output pin of lever
    def set_is_active(self, val: bool):
        super().set_is_active(val)
        ADU200.get_instance().set_relay(self.relay_pin, set_open=not val)
        

if __name__ == "__main__":
    lever_1:LeverBase = SwitchLever("rpi_1_lever", 0)
    lever_2:LeverBase = SwitchLever("rpi_2_lever", 3)
    while True:
        lever_1.update_state_continously()
        lever_2.update_state_continously()
        
    
        
