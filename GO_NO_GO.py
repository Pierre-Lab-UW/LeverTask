from pygame import Color

from pgtools import *  # use an altenative
import pandas as pd
import numpy as np

import random
from threading import Timer



class GO_NO_GO(object):

    def __init__(self, screen=None, m_params=None, arm_used=None, clipart=None):

        self.trial_mode = None  # initially none will be set
        self.region = None  # represents the go/no-go region to be dragged into
        self.stimulus = None  # represents the actual circle/shape to be dragged
        self.screen = screen  # screen object, being passed in through the actual
        self.m_params = m_params
        self.task_name = 'GO_NO_GO'
        self.monkey_name = self.m_params['subject']
        self.inter_trial_interval = int(self.m_params['ITI'].iloc[0])  # must be an integer
        try:
            self.ratio = float(self.m_params['RatioTrials'].iloc[0])
        except:
            print('RATIO:  ' + self.m_params['RatioTrials'].iloc[0])

        self.treats_dispensed = 0
        self.time = 0
        self.stop_timer = False

        self.stim_x = 0
        self.stim_y = 0
        self.abort_time = self.m_params['AbortTrialTime'].iloc[0]

        self.max_trials = int(self.m_params['NumTrials'].iloc[0])  # <--- Added for run loop
        print(self.max_trials)
        self.trials_arr = np.zeros(self.max_trials, dtype=int)  # will be ued for

        width, height = pg.display.get_window_size()
        self.width = width
        self.height = height

        self.shape_pos_x = width / 2
        self.shape_pos_y = height / 2
        pg.mouse.set_pos((self.shape_pos_x, self.shape_pos_y))

        self.phases = {
            "Phase 1": "Basic Training",
            "Phase 2": "Accelerated Training",
            "Phase 3": "Actual Trial"
        }

        self.current_trial = 1  # <--- Added for run loop, it is the initial trial marker


          #strictly for future us (randomization of trials)
        for i in range(1, self.max_trials, 1):
            if i <= self.ratio * self.max_trials:
                self.trials_arr[i - 1] = 1  # GO trial

            else:
                self.trials_arr[i - 1] = 2  # NO_GO_TRIAL

        self.timer = Timer(1.0, self.update_time)  # timer that calls every second (part of Threading library)

    def on_loop(self):

        self.screen.fg.fill(BLACK)  # Clear screen before drawing

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

        pg.display.update()  # <--- Important for rendering,

        # if in the go trial mode
        if self.trial_mode == 1:
            if self.shape_pos_y <= 100:
                return 'ITI'  # succeeded in completing trial if in the GO region
            elif self.shape_pos_y > 100:
                if self.time >= self.abort_time:  # failed to complete trial
                    return 'timeout'

                else:
                    return 'Running'  # in the running state if time isn't up yet

        # else  in the NO_GO tral mode
        if self.trial_mode == 2:
            # if in the safe region
            if self.shape_pos_y > 100:
                # time up in the safe region means success
                if self.time >= self.abort_time:
                    return 'ITI'
                else:
                    # if time isn't up yet, it is still running
                    return 'Running'
            else:
                return 'timeout'

    def update_time(self):
        if not self.stop_timer:
            self.time += 0.5
            print(f"Time: {self.time}")  # Optional for debug

            self.timer = Timer(0.5, self.update_time)
            self.timer.start()

    def stop_updating(self):

        self.stop_timer = True
        if self.timer:
            self.timer.cancel()

    # what actually runs
    def run(self):

        self.time = 0
        self.stop_timer = False

        # create a new instance of thread timer , bypassing the run time excption of restarting thread
        self.timer = Timer(0.5, self.update_time)
        self.timer.start()

        self.trial_mode = random.randint(1, 2)  # randomize trial type
        print(f"\n--- Trial {self.current_trial} ---")

        while self.time < self.abort_time:
            pg.event.get()
            mouse_x, mouse_y = pg.mouse.get_pos()
            self.shape_pos_x = mouse_x
            self.shape_pos_y = mouse_y
            print(mouse_x)
            print(mouse_y)

            result = self.on_loop()

            if result == 'ITI':
                print("Successful Trial (GO or NO_GO)")
                sounds['correct'].play()
                return 'success'
            elif result == 'Running':
                print(f'Still Running (Time={self.time})')
            elif result == 'timeout':
                print("Timeout occurred")
                sounds['incorrect'].play()
                return 'timeout'


if __name__ == "__main__":
    screen = Screen(fullscreen=False, size=(800, 800), color=BLACK)
    m_params = pd.read_csv('GNG_PARAMS.csv')
    gng = GO_NO_GO(screen=screen, m_params=m_params)

    # gng instance doesn't represent a trial, we're changing the trial mode with each
    # trial instance
    while gng.current_trial <= gng.max_trials:
        result = gng.run()  # run trials
        gng.current_trial += 1
        gng.stop_updating()  # stop updating timer
        pg.time.delay(int(gng.inter_trial_interval) * 1000)  # delay by inter trial interval

    print("All trials completed.")
