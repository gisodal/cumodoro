import curses
from cumodoro.component.frame import Frame
import datetime
import time
import logging
log = logging.getLogger('cumodoro')

class Clock(Frame):
    def __init__(self):
        super(Clock,self).__init__()
        self.set_size(6,1)

    def get_time(self):
        return datetime.datetime.now().strftime('%H:%M')

    def update(self):
        self.addstr(0,0,self.get_time())

    def init_wait(self):
        self.update()
        self.refresh()
        wait_time = 60.1 - (float(datetime.datetime.now().strftime('%S.%f')))
        time.sleep(wait_time)

    def run(self):
        while True:
            self.update()
            self.refresh()
            time.sleep(1)

