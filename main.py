from ADU200 import ADU200
from typing import Dict
import sys
import importlib
import LeverBase
from LeverEventBase import DebugEvent
from SwitchLever import SwitchLever
import yaml
import os

# Command line arguments: training class name, parameter file
if len(sys.argv) < 2:
    print("Usage: python main.py <GlobalParamFile>")
    sys.exit(1)

global_param_file: str = sys.argv[1]

if not os.path.exists(global_param_file):
    print(f"❌ Error: File not found -> {global_param_file}")
    sys.exit(1)

#data
with open(global_param_file, 'r') as f:
    data = yaml.safe_load(f)

#yaml parse global param file for the other parameters
params = data.get('parameters', {})

# Extract individual parameter values (using "actual" field)
param_file: str = params.get('training_param_file', {}).get('actual', '')
lever_1_name: str = params.get('Lever1Name', {}).get('actual', '')
lever_2_name: str = params.get('Lever2Name', {}).get('actual', '')

#get training class name
if not os.path.exists(param_file):
    print(f"❌ Error: File not found -> {param_file}")
    sys.exit(1)

#data
with open(param_file, 'r') as f:
    data_param_file = yaml.safe_load(f)
params_param_file = data_param_file.get('parameters', {})
training_class_name: str = params_param_file.get('TaskName', {}).get('actual', '')


#CODE HERE
lever1_pin: int = params_param_file.get("Lever1_Relay_Port").get('actual', -1)
lever2_pin: int = params_param_file.get("Lever2_Relay_Port").get('actual', -1)

lever_1:LeverBase = SwitchLever(lever_1_name, lever1_pin)
lever_2:LeverBase = SwitchLever(lever_2_name, lever2_pin)

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

training_instance = TrainingClass(lever_1, lever_2, param_file, global_param_file)
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
