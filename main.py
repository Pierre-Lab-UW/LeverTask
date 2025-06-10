from typing import Dict
from LeverEventBase import DebugEvent
from RPILever import RPILever
from Training import Training
from Trainings.FixedRatioTraining import FixedRatioTraining
from Trainings.ProgressiveRatioTraining import ProgressiveRatioTraining


lever_1:RPILever = RPILever("rpi_1_lever", 14)
lever_2:RPILever = RPILever("rpi_2_lever", 15)

#add a debug event for helful logging
lever_1.add_event(DebugEvent("debug", lever_1))
lever_2.add_event(DebugEvent("debug", lever_2))
#start a fixed ratio training
fixed_ratio_parameters: Dict[str, int] = {"FR":5, "ITI":3, "PR":1, "Timeout":10}
current_training: Training = ProgressiveRatioTraining(lever_1 , lever_2, fixed_ratio_parameters)
current_training.start_event()

while True:
    lever_1.update()
    lever_2.update()
    current_training.update()
    if current_training.should_end_traning():
        break