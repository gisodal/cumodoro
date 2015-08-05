from cumodoro.component.frame import Frame
import cumodoro.config as config
from cumodoro.timeconvert import *
import threading
import time
import curses

class Overtime(Frame):
    def __init__(self):
        super(Overtime,self).__init__()
        self.set_size(12,1)
        self.current_time = 0
        self.phase_lock = threading.RLock()
        self.running_lock = threading.Lock()
        self.running = False
        self.phase = 0
        self.thread = None

    def update(self):
        self.erase()
        if self.current_time > 0:
            if self.current_time >= config.TIME_BREAK_SEC:
                self.addstr(0,0,"+" + sec_to_time(self.current_time),curses.color_pair(curses.COLOR_RED)|curses.A_BOLD)
            else:
                self.addstr(0,0,"+" + sec_to_time(self.current_time))

    def get_running(self):
        self.running_lock.acquire()
        r = self.running
        self.running_lock.release()
        return r

    def set_running(self,r):
        self.running_lock.acquire()
        self.running = r
        self.running_lock.release()

    def set_phase(self,p):
        self.phase_lock.acquire()
        self.phase = p
        if p == 0:
            self.current_time = 0
        self.phase_lock.release()

    def get_phase(self):
        self.phase_lock.acquire()
        phase = self.phase
        self.phase_lock.release()
        return phase

    def start(self):
        self.running_lock.acquire()
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run,name="Overtime")
            self.thread.setDaemon(True)
            self.thread.start()
        self.running_lock.release()

    def run(self):
        while self.get_phase() != 0:
            self.update()
            self.refresh()
            time.sleep(1)
            self.current_time += 1

        self.current_time = 0
        self.update()
        self.refresh()
        self.set_running(False)



