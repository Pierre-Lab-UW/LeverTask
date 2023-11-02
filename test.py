import pygame
from pygame.locals import *
from LeverBase import LeverBase
from EventBase import DebugEvent

pygame.init()

window = pygame.display.set_mode((600,600))

class PyGameLever(LeverBase):
    def __init__(self, name, win, rect_center_x, rect_center_y, width, height):
        super().__init__(name)
        self.x = rect_center_x
        self.y = rect_center_y
        self.width = width
        self.win = win
        self.height = height
    
    def update_state(self):
        #print("update")
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_pos, y_pos = pygame.mouse.get_pos()
                #print(x_pos, y_pos, self.x - float(self.width/2), self.x + float(self.width/2))
                if x_pos > self.x and x_pos < self.x + self.width and y_pos > self.y and y_pos < self.y + self.height:
                    self.switch_state()
                    
    def draw(self):
        pygame.draw.rect(self.win, (0,0,255), [self.x,self.y,self.width,self.height],0)
        
    def update(self):
        super().update()
        self.draw()


lever_pygame = PyGameLever("test", window, 100, 100, 400, 100)
#add a debug event for helful logging
lever_pygame.add_event(DebugEvent("debug"))

clock = pygame.time.Clock()
while True:
    clock.tick(60)
    lever_pygame.update()
    pygame.display.update()