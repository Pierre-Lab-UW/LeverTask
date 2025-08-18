from typing import Dict
import LeverBase
from LeverEventBase import DebugEvent
from SwitchLever import SwitchLever
from Training import Training
from Trainings.FixedRatioTraining import FixedRatioTraining
from Trainings.ProgressiveRatioTraining import ProgressiveRatioTraining
from Trainings.GeometricRatioTraining import GeometricRatioTraining
from ADU200 import ADU200

lever_1:LeverBase = SwitchLever("rpi_1_lever", 0)
lever_2:LeverBase = SwitchLever("rpi_2_lever", 3)

#add a debug event for helful logging
lever_1.add_event(DebugEvent("debug", lever_1))
lever_2.add_event(DebugEvent("debug", lever_2))
#start a fixed ratio training
fixed_ratio_parameters: Dict[str, int] = {"FR":5, "ITI":3, "GR":1.5, "Timeout":10}
current_training: Training = GeometricRatioTraining(lever_1 , lever_2, fixed_ratio_parameters)
current_training.start_event()

ADU200.get_instance()

while True:
    try:
        lever_1.update()
        lever_2.update()
        current_training.update()
        if current_training.should_end_traning():
            break
    except Exception as e:
        raise Exception("Error when executing task: {}".format(e))
