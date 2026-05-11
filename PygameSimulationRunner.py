from typing import Dict
from TrainingRunnerBase import TrainingRunnerBase
import pygame,sys
from pygame.locals import *
from LeverBase import *
from LeverEventBase import LeverEventBase, DebugEvent
from Trainings import *
import importlib
import os
import yaml
import Events.LeverStateChangedEvent as LeverStateChangeEvent

pygame.init()

window = pygame.display.set_mode((600,600))


class PyGameLever(LeverBase):
    def __init__(self, name, rect_center_x, rect_center_y, width, height):
        super().__init__(name)
        self.x = rect_center_x
        self.y = rect_center_y
        self.width = width
        self.height = height
        self.pygame_events = None
    
    def update_state_continously(self):
        if self.pygame_events is None:
            return
        for event in self.pygame_events:
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
        if not self.active:
            #draw lever as gray if it isn't active
            pygame.draw.rect(window, (128,128,128), [self.x,self.y,self.width,self.height],0)
        elif self.state == STATE_UNPRESSED:
            pygame.draw.rect(window, (255,0,0), [self.x,self.y,self.width,self.height],0)
        else:
            pygame.draw.rect(window, (0,255,0), [self.x,self.y,self.width,self.height],0)
        #draw current number of presses on the lever

    def update(self):
        super().update()
        self.draw()
    

class PyGameSimulationRunner(TrainingRunnerBase):
    def __init__(self, input_args: list[str]):
        file_path = input_args[1]
        self.output_dir_base = '/'.join(file_path.split('/')[:-1])
        print("Output dir base:", self.output_dir_base)
        super().__init__(input_args)
    
    def run(self):
        super().run()
        lever_1_name: str = self.global_params.get('Lever1Name', {})
        lever_2_name: str = self.global_params.get('Lever2Name', {})

        lever_pygame_1 = PyGameLever(lever_1_name, 100, 350, 100, 100)
        lever_pygame_2 = PyGameLever(lever_2_name, 400, 350, 100, 100)

        TrainingClass = self.get_training_class_instance()
        training_instance = TrainingClass(lever_pygame_1, lever_pygame_2, self.training_params, self.global_params, self.output_dir_base)
        training_instance.start_event()

        ev = pygame.event.get()
        lever_pygame_1.pygame_events = ev
        lever_pygame_2.pygame_events = ev
        clock = pygame.time.Clock()
        
        while True:
            clock.tick(60)
            if training_instance.should_end_traning():
                training_instance.stop_event()
                pygame.quit()
                self.on_finish()
                sys.exit(0)
            ev = pygame.event.get()
            lever_pygame_1.pygame_events = ev
            lever_pygame_2.pygame_events = ev
            for event in ev:
                if event.type == QUIT:
                    training_instance.stop_event()
                    pygame.quit()
                    self.on_finish()
                    sys.exit(0)
            window.fill([255,255,255])
            lever_pygame_1.update()
            lever_pygame_2.update()
            training_instance.update()
            pygame.display.update()
    
    def on_lever_state_change(self, lever: LeverBase, new_lever_state: int, time_since_last_change: float):
        print(f"Lever {lever.name} changed to state {new_lever_state} with time since last change {time_since_last_change}")

if __name__ == "__main__":
    # Command line arguments: training class name, parameter file    
    simulation_runner = PyGameSimulationRunner(sys.argv)
    simulation_runner.run()