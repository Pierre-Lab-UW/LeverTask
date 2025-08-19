from typing import Dict
import sys
import importlib
import LeverBase
from LeverEventBase import DebugEvent
from SwitchLever import SwitchLever
from Training import Training
from ADU200 import ADU200


# Command line arguments: training class name, parameter file
if len(sys.argv) < 5:
    print("Usage: python main.py <TrainingClassName> <ParameterFile> <Lever1Name> <Lever2Name>")
    sys.exit(1)

training_class_name = sys.argv[1]
param_file = sys.argv[2]
lever_1_name = sys.argv[3]
lever_2_name = sys.argv[4]

lever_1:LeverBase = SwitchLever(lever_1_name, 0)
lever_2:LeverBase = SwitchLever(lever_2_name, 3)

# add a debug event for helpful logging
lever_1.add_event(DebugEvent("debug", lever_1))
lever_2.add_event(DebugEvent("debug", lever_2))

# Dynamically import the requested training class from Trainings
try:
    training_module = importlib.import_module(f"Trainings.{training_class_name}")
    TrainingClass = getattr(training_module, training_class_name)
except (ModuleNotFoundError, AttributeError):
    print(f"Could not find training class '{training_class_name}' in Trainings/{training_class_name}.py")
    sys.exit(1)

training_instance = TrainingClass(lever_1, lever_2, param_file)
training_instance.start_event()

ADU200.get_instance()

while True:
    try:
        lever_1.update()
        lever_2.update()
        training_instance.update()
        if training_instance.should_end_traning():
            break
    except Exception as e:
        raise Exception("Error when executing task: {}".format(e))
