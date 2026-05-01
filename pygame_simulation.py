# from typing import Dict
# import pygame,sys
# from pygame.locals import *
# from LeverBase import *
# from LeverEventBase import LeverEventBase, DebugEvent
# from Trainings import *
# import importlib
# import os
# import yaml

# pygame.init()

# window = pygame.display.set_mode((600,600))

# pygame_events = None

# class PyGameLever(LeverBase):
#     def __init__(self, name, rect_center_x, rect_center_y, width, height):
#         super().__init__(name)
#         self.x = rect_center_x
#         self.y = rect_center_y
#         self.width = width
#         self.height = height
    
#     def update_state_continously(self):
#         for event in pygame_events:
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 x_pos, y_pos = pygame.mouse.get_pos()
#                 #print(x_pos, y_pos, self.x - float(self.width/2), self.x + float(self.width/2))
#                 if x_pos > self.x and x_pos < self.x + self.width and y_pos > self.y and y_pos < self.y + self.height:
#                     self.set_state(STATE_PRESSED)
#                 elif self.state == STATE_PRESSED:
#                     self.set_state(STATE_UNPRESSED)
#             elif self.state == STATE_PRESSED:
#                 self.set_state(STATE_UNPRESSED)   
                     
    # def draw(self):
    #     if not self.active:
    #         #draw lever as gray if it isn't active
    #         pygame.draw.rect(window, (128,128,128), [self.x,self.y,self.width,self.height],0)
    #     elif self.state == STATE_UNPRESSED:
    #         pygame.draw.rect(window, (255,0,0), [self.x,self.y,self.width,self.height],0)
    #     else:
    #         pygame.draw.rect(window, (0,255,0), [self.x,self.y,self.width,self.height],0)
    #         print("Lever being drawn")
    #     #draw current number of presses on the lever
    #     font = pygame.font.SysFont(None, 24)
    #     img = font.render(str(self.press_count), True, (0,0,0))
    #     window.blit(img, (self.x + self.width/2 - img.get_width()/2, self.y + self.height/2 - img.get_height()/2))
    
#     def update(self):
#         super().update()
#         self.draw()





# # Command line arguments: training class name, parameter file
# if len(sys.argv) < 2:
#     print("Usage: python main.py <GlobalParamFile>")
#     sys.exit(1)

# global_param_file: str = sys.argv[1]

# if not os.path.exists(global_param_file):
#     print(f"❌ Error: File not found -> {global_param_file}")
#     sys.exit(1)

# #data
# with open(global_param_file, 'r') as f:
#     data = yaml.safe_load(f)

# #yaml parse global param file for the other parameters
# params = data.get('parameters', {})

# # Extract individual parameter values (using "actual" field)
# param_file: str = params.get('training_param_file', {}).get('actual', '')
# lever_1_name: str = params.get('Lever1Name', {}).get('actual', '')
# lever_2_name: str = params.get('Lever2Name', {}).get('actual', '')

# lever_pygame_1 = PyGameLever(lever_1_name, 100, 350, 100, 100)
# lever_pygame_2 = PyGameLever(lever_2_name, 400, 350, 100, 100)

# #get training class name
# if not os.path.exists(param_file):
#     print(f"❌ Error: File not found -> {param_file}")
#     sys.exit(1)

# #data
# with open(param_file, 'r') as f:
#     data_param_file = yaml.safe_load(f)
# params_param_file = data_param_file.get('parameters', {})
# training_class_name: str = params_param_file.get('TaskName', {}).get('actual', '')


# # Dynamically import the training class
# try:
#     training_module = importlib.import_module(f"Trainings.{training_class_name}")
#     TrainingClass = getattr(training_module, training_class_name)
# except Exception as e:
#     print(f"Error when loading training '{training_class_name}': {e}")
#     sys.exit(1)


# training_instance = TrainingClass.from_filepath(lever_pygame_1, lever_pygame_2, param_file, global_param_file)
# training_instance.start_event()

# pygame_events = pygame.event.get()
# clock = pygame.time.Clock()
# while True:
#     clock.tick(60)
#     pygame_events = pygame.event.get()
#     if training_instance.should_end_traning():
#         training_instance.stop_event()
#         pygame.quit()
#         sys.exit(0)
#     for event in pygame_events:
#         if event.type == QUIT:
#             training_instance.stop_event()
#             pygame.quit()
#             sys.exit(0)
#     window.fill([255,255,255])
#     lever_pygame_1.update()
#     lever_pygame_2.update()
#     training_instance.update()
#     pygame.display.update()

