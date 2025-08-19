from typing import Dict
import LeverBase
from LeverEventBase import DebugEvent
from SwitchLever import SwitchLever
from Training import Training
from Trainings.RatioTraining import RatioTraining
from ADU200 import ADU200

lever_1:LeverBase = SwitchLever("rpi_1_lever", 0)
lever_2:LeverBase = SwitchLever("rpi_2_lever", 3)

#add a debug event for helful logging
lever_1.add_event(DebugEvent("debug", lever_1))
lever_2.add_event(DebugEvent("debug", lever_2))
#start a fixed ratio training
ratio_training = RatioTraining(lever_1 , lever_2, "Trainings/RatioTraining.yaml")
ratio_training.start_event()

ADU200.get_instance()

while True:
    try:
        lever_1.update()
        lever_2.update()
        ratio_training.update()
        if ratio_training.should_end_traning():
            break
    except Exception as e:
        raise Exception("Error when executing task: {}".format(e))
