from LeverEventBase import DebugEvent
from RPILever import RPILever
from Trainings.FixedRatioTraining.FixedRatioTraining import FixedRatioTraining


lever_1:RPILever = RPILever("rpi_1_lever", 14)
lever_2:RPILever = RPILever("rpi_2_lever", 15)

#add a debug event for helful logging
lever_1.add_event(DebugEvent("debug", lever_1))
lever_2.add_event(DebugEvent("debug", lever_2))
#start a fixed ratio training
fixed_ratio_parameters = {"lever_presses":5, "update_interval":3}
fixed_ratio_training = FixedRatioTraining(lever_1 , lever_2, fixed_ratio_parameters)
fixed_ratio_training.start_event()

while True:
    lever_1.update()
    lever_2.update()