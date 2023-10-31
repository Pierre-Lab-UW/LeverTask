from EventBase import *
from LeverBase import *

lever = LeverBase("firstLever")
event = DebugEvent("debug")
lever.add_event(event)

for i in range(100):
    lever.execute_events()