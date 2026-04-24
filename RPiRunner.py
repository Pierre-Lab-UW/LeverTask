
from SwitchLever import SwitchLever
from TrainingRunnerBase import TrainingRunnerBase
import sys

class RPIRunner(TrainingRunnerBase):
    def __init__(self, input_args: list[str]):
        super().__init__(input_args)
    
    def run(self):
        lever_1_name: str = self.global_params.get('Lever1Name', {})
        lever_2_name: str = self.global_params.get('Lever2Name', {})

        lever_1 = SwitchLever(lever_1_name, 100, 350, 100, 100)
        lever_2 = SwitchLever(lever_2_name, 400, 350, 100, 100)

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