from LeverBase import LeverBase
try:
    # checks if you have access to RPi.GPIO, which is available inside RPi
    import RPi.GPIO as GPIO
except:
    # In case of exception, you are executing your script outside of RPi, so import Mock.GPIO
    import Mock.GPIO as GPIO


class RPILever(LeverBase):
    def __init__(self, lever_name: str, input_pin:int, output_pin:int):
        super().__init__(lever_name)
        self.input_pin = input_pin #pin that reads in if the lever is being pressed
        self.output_pin = output_pin #pin that controls the lever active property
        self.stateCount = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.input_pin, GPIO.IN)
        GPIO.setup(self.output_pin, GPIO.OUT)

    def update_state_continously(self) -> None:
        input_pin_val = GPIO.input(self.input_pin)
        if self.state != input_pin_val:
            print(str(self.stateCount)+") New State: "+str(input_pin_val))
        self.set_state(input_pin_val)
        #check for state via output pin of lever
    def set_is_active(self, val: bool):
        super().set_is_active(val)
        #Set relay voltage to this
        if self.active:
            GPIO.output(self.output_pin, 1)
        else:
            GPIO.output(self.output_pin, 0)

if __name__ == "__main__":
    print("Testing Hardware Lever...")
    import time 

    lever:LeverBase = RPILever("rpi_lever", 25, 24)
    print("Test 0")
    lever.set_is_active(False)
    time.sleep(2)
    lever.set_is_active(not lever.active)
    print("Test 1")
    time.sleep(5)
    lever.set_is_active(not lever.active)
    print("Test 2")
    while True:
        lever.update_state_continously()
