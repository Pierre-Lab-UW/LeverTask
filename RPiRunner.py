
import LeverBase
from LeverEventBase import DebugEvent
from SwitchLever import SwitchLever
from TrainingRunnerBase import TrainingRunnerBase
import sys

class RPIRunner(TrainingRunnerBase):
    def __init__(self, input_args: list[str]):
        super().__init__(input_args)
    
    def run(self):
        lever_1_name: str = self.global_params.get('Lever1Name', {})
        lever_2_name: str = self.global_params.get('Lever2Name', {})
        lever1_pin: int = self.global_params.get("Lever1_Relay_Port", {}).get('actual', -1)
        lever2_pin: int = self.global_params.get("Lever2_Relay_Port", {}).get('actual', -1)

        lever_1:LeverBase = SwitchLever(lever_1_name, lever1_pin)
        lever_2:LeverBase = SwitchLever(lever_2_name, lever2_pin)

        # add a debug event for helpful logging
        lever_1.add_event(DebugEvent("debug", lever_1))
        lever_2.add_event(DebugEvent("debug", lever_2))

        TrainingClass = self.get_training_class_instance()
        training_instance = TrainingClass(lever_1, lever_2, self.training_params, self.global_params)
        training_instance.start_event()

        while True:
            try:
                lever_1.update()
                lever_2.update()
                training_instance.update()
                if training_instance.should_end_traning():
                    break
            except Exception as e:
                raise Exception("Error when executing task: {}".format(e))
            
if __name__ == "__main__":
    # Command line arguments: training class name, parameter file    
    simulation_runner = RPIRunner(sys.argv)
    simulation_runner.run()