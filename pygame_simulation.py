import pygame,sys
from pygame.locals import *
from LeverBase import LeverBase
from LeverEventBase import LeverEventBase, DebugEvent
from Events.ResetLeverEvent import *

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
        if pygame_events == None:
            return
        for event in pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos, y_pos = pygame.mouse.get_pos()
                #print(x_pos, y_pos, self.x - float(self.width/2), self.x + float(self.width/2))
                if x_pos > self.x and x_pos < self.x + self.width and y_pos > self.y and y_pos < self.y + self.height:
                    self.switch_state()
                 
    def draw(self):
        if self.state == 0:
            pygame.draw.rect(window, (255,0,0), [self.x,self.y,self.width,self.height],0)
        else:
            pygame.draw.rect(window, (0,255,0), [self.x,self.y,self.width,self.height],0)
            
    def update(self):
        super().update()
        self.draw()
    
lever_pygame_1 = PyGameLever("Lever1",  100, 350, 100, 100)
lever_pygame_2 = PyGameLever("Lever2",  400, 350, 100, 100)

#add a debug event for helful logging
lever_pygame_1.add_event(DebugEvent("debug", lever_pygame_1))
lever_pygame_2.add_event(DebugEvent("debug", lever_pygame_2))
lever_pygame_2.add_event(ResetLeverEvent("reset",lever_pygame_2, 5))

clock = pygame.time.Clock()
while True:
    clock.tick(60)
    pygame_events = pygame.event.get()
    for event in pygame_events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)
    lever_pygame_1.update()
    lever_pygame_2.update()
    pygame.display.update()