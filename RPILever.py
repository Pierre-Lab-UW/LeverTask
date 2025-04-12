from datetime import time
import pandas as pd

import random
import threading
import os


class GO_NO_GO(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.m_params = m_params
        self.task_name = 'GO_NO_GO'
        self.monkey_name = monkey_name
        self.inter_trial_interval = int(self.m_params[self.monkey_name]['ITI'])



        try:
            self.ratio = int(self.m_params[self.monkey_name]['GNG_Ratio'])
        except:
            print('RATIO:  ' + self.m_params[self.monkey_name]['GNG_Ratio'])

        self.timeout = 5  # seconds
        self.treats_dispensed = 0
        self.time = 0
        self.stop_timer = False

        self.stim_x = 0
        self.stim_y = 0
        self.progressed = False
        self.stimulus_moving = False

        width, height = pg.display.get_window_size()
        self.width = width
        self.height = height
        self.shape_pos_x = width / 2
        self.shape_pos_y = height / 2

        print(f"position x{self.shape_pos_x}")
        print(f"position y{self.shape_pos_y}")

        pg.mouse.set_pos((self.shape_pos_x, self.shape_pos_y))

        self.phases = {
            "Phase 1": "Basic Training",
            "Phase 2": "Accelerated Training",
            "Phase 3": "Actual Trial"
        }

        self.trial_mode = random.choice([1, 2])
        self.go_threshold = 5

        self.max_trials = 10               # <--- Added for run loop
        self.current_trial = 0             # <--- Added for run loop

    def on_loop(self):
        if self.trial_mode == 1:
            self.region = pg.draw.rect(self.screen.fg, Color('White'),
                                       rect=(0, 0, self.width, 100), width=45)

            self.stimulus = pg.draw.circle(self.screen.fg, color=Color('White'),
                                           center=(self.shape_pos_x, self.shape_pos_y),
                                           radius=15)
            print('stim drawn 1')

        elif self.trial_mode == 2:
            self.region = pg.draw.rect(self.screen.fg, Color('red'),
                                       rect=(0, 0, self.width, 100), width=45)

            self.stimulus = pg.draw.circle(self.screen.fg, color=Color('red'),
                                           center=(self.shape_pos_x, self.shape_pos_y),
                                           radius=15)
            print('stim drawn 2')

        pg.display.update()  # <--- Important for rendering
        self.on_touch()

    def update_time(self):
        if not self.stop_timer:
            self.time += 1
            threading.Timer(1.0, self.update_time).start()

    def stop_updating(self):
        self.stop_timer = True

    def new_trial(self):
        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(
            self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))

        self.filepath_to_size = os.path.join('_progress', self.monkey_name, 'TouchTrain-size.txt')
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')

    def on_touch(self, touch_x=None, touch_y=None):
        mouse_x, mouse_y = pg.mouse.get_pos()
        self.shape_pos_x = mouse_x
        self.shape_pos_y = mouse_y

        if self.trial_mode == 1:
            if self.shape_pos_y <= 100:
                return 'ITI'
            elif self.shape_pos_y > 100 and (self.time < self.timeout):
                return 'timeout'

        if self.trial_mode == 2:
            if self.shape_pos_y > 100 and (self.time >= self.timeout):
                return 'ITI'
            elif self.shape_pos_y <= 100:
                return 'timeout'

    def set_mode(self, mode):
        if mode not in self.phases:
            return None
        else:
            print(f"Set mode to {mode}")
            return mode

    def run(self):  # <--- Main loop added
        while self.current_trial < self.max_trials:
            self.time = 0
            self.stop_timer = False
            self.trial_mode = random.choice([1, 2])  # randomize each trial

            print(f"\n--- Trial {self.current_trial + 1} ---")
            self.on_loop()
            self.update_time()

            while not self.stop_timer:
                pg.time.delay(100)
                result = self.on_touch()

                if result == 'ITI':
                    print("Proceeding to next trial (ITI)")
                    self.stop_updating()
                    break
                elif result == 'timeout':
                    print("Timeout occurred")
                    self.stop_updating()
                    break

            self.current_trial += 1
            pg.time.delay(self.ITI * 1000)

        print("All trials completed.")


if __name__ == "__main__":
    screen = Screen(fullscreen=True,
                         size=(800,800),
                         color=BLACK)



    m_params =  pd.read_csv('parameters.csv')


    # using george as a placeholder name


    gng = GO_NO_GO(screen=screen, monkey_name="George", g_params=None, m_params=m_params)
    gng.run()