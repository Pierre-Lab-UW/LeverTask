from typing import Dict
import pygame,sys
from pygame.locals import *
from LeverBase import *
from LeverEventBase import LeverEventBase, DebugEvent
from Events.RecordDataEvent import *
from Trainings import *
import importlib
import os
pygame.init()

window = pygame.display.set_mode((600,600))

pygame_events = None

class PyGameLever(LeverBase):
    def __init__(self, name, rect_center_x, rect_center_y, width, height):
        super().__init__(name)
        self.x = rect_center_x
        self.y = rect_center_y
        self.width = width
        self.height = height
    
    def update_state_continously(self):
        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos, y_pos = pygame.mouse.get_pos()
                #print(x_pos, y_pos, self.x - float(self.width/2), self.x + float(self.width/2))
                if x_pos > self.x and x_pos < self.x + self.width and y_pos > self.y and y_pos < self.y + self.height:
                    self.set_state(STATE_PRESSED)
                elif self.state == STATE_PRESSED:
                    self.set_state(STATE_UNPRESSED)
            elif self.state == STATE_PRESSED:
                self.set_state(STATE_UNPRESSED)   
                     
    def draw(self):
        if self.state == STATE_UNPRESSED:
            pygame.draw.rect(window, (255,0,0), [self.x,self.y,self.width,self.height],0)
        else:
            pygame.draw.rect(window, (0,255,0), [self.x,self.y,self.width,self.height],0)

    def update(self):
        super().update()
        self.draw()





# Command line arguments: training class name, parameter file
if len(sys.argv) < 6:
    print("Usage: python pygame_simulation.py <TrainingClassName> <ParameterFile> <Lever1Name> <Lever2Name> <GlobalParamFile>")
    sys.exit(1)

training_class_name = sys.argv[1]
param_file = sys.argv[2]
lever_1_name = sys.argv[3]
lever_2_name = sys.argv[4]
global_param_file = sys.argv[5]

print(f"Global Parameter File: {global_param_file}")

if os.path.isfile(global_param_file):
    print(f"Global parameter file '{global_param_file}' found.")
else:
    print(f"Global parameter file '{global_param_file}' not found.")
    sys.exit(1)

lever_pygame_1 = PyGameLever(lever_1_name, 100, 350, 100, 100)
lever_pygame_2 = PyGameLever(lever_2_name, 400, 350, 100, 100)

# Dynamically import the training class
try:
    training_module = importlib.import_module(f"Trainings.{training_class_name}")
    TrainingClass = getattr(training_module, training_class_name)
except Exception as e:
    print(f"Error when loading training '{training_class_name}': {e}")
    sys.exit(1)


training_instance = TrainingClass(lever_pygame_1, lever_pygame_2, param_file, global_param_file)
training_instance.start_event()

pygame_events = pygame.event.get()
clock = pygame.time.Clock()
while True:
    clock.tick(60)
    pygame_events = pygame.event.get()
    if training_instance.should_end_traning():
        training_instance.stop_event()
        pygame.quit()
        sys.exit(0)
    for event in pygame_events:
        if event.type == QUIT:
            training_instance.stop_event()
            pygame.quit()
            sys.exit(0)
    window.fill([255,255,255])
    lever_pygame_1.update()
    lever_pygame_2.update()
    training_instance.update()
    pygame.display.update()

