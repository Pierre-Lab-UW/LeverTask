from LeverBase import LeverBase
try:
    # checks if you have access to RPi.GPIO, which is available inside RPi
    import RPi.GPIO as GPIO
except:
    # In case of exception, you are executing your script outside of RPi, so import Mock.GPIO
    import Mock.GPIO as GPIO


class RPILever(LeverBase):
    def __init__(self, lever_name: str, input_pin:int):
        super().__init__(lever_name)
        self.input_pin = input_pin #pin that reads in if the lever is being pressed
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def update_state_continously(self) -> None:
        input_pin_val = -1
        for i in range(30):
            input_pin_val = GPIO.input(self.input_pin)
        if self.state != input_pin_val:
            print(self.name+" State: "+str(input_pin_val))
        self.set_state(input_pin_val)
        #check for state via output pin of lever
    def set_is_active(self, val: bool):
        super().set_is_active(val)
        

if __name__ == "__main__":
    lever_1:LeverBase = RPILever("rpi_1_lever", 14)
    lever_2:LeverBase = RPILever("rpi_2_lever", 15)
    while True:
        lever_1.update_state_continously()
        lever_2.update_state_continously()
        
    
        
