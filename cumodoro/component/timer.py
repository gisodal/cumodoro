import curses
import time
import threading
import datetime
import cumodoro.globals as globals
import cumodoro.config as config
from cumodoro.timeconvert import *
from cumodoro.component.frame import Frame
import math
import logging

log = logging.getLogger("cumodoro")

class Timer(Frame):
    def __init__(self):
        super().__init__()
        self.overtime = globals.interface.windows["Timer"].frames["overtime_frame"]
        self.edit_timer = False
        self.running = False
        self.running_lock = threading.Lock()
        self.set_size(35,5)
        self.current_time = config.TIME_POMODORO_SEC
        self.phase_lock = threading.Lock()
        self.phase = 0
        self.taskswitcher = globals.interface.windows["Timer"].frames["taskswitcher_frame"]
        self.weekview = globals.interface.windows["Weekview"].frames["weekview_frame"]
        self.digit = [
                [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(0,1),(1,1),(4,1),(5,1),(0,2),(1,2),(4,2),(5,2),(0,3),(1,3),(4,3),(5,3),(0,4),(1,4),(2,4),(3,4),(4,4),(5,4)],
                [(4,0),(5,0),(4,1),(5,1),(4,2),(5,2),(4,3),(5,3),(4,4),(5,4)],
                [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(4,1),(5,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(0,3),(1,3),(0,4),(1,4),(2,4),(3,4),(4,4),(5,4)],
                [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(4,1),(5,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(4,3),(5,3),(0,4),(1,4),(2,4),(3,4),(4,4),(5,4)],
                [(0,0),(1,0),(4,0),(5,0),(0,1),(1,1),(4,1),(5,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(4,3),(5,3),(4,4),(5,4)],
                [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(0,1),(1,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(4,3),(5,3),(0,4),(1,4),(2,4),(3,4),(4,4),(5,4)],
                [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(0,1),(1,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(0,3),(1,3),(4,3),(5,3),(0,4),(1,4),(2,4),(3,4),(4,4),(5,4)],
                [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(4,1),(5,1),(4,2),(5,2),(4,3),(5,3),(4,4),(5,4)],
                [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(0,1),(1,1),(4,1),(5,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(0,3),(1,3),(4,3),(5,3),(0,4),(1,4),(2,4),(3,4),(4,4),(5,4)],
                [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(0,1),(1,1),(4,1),(5,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(4,3),(5,3),(0,4),(1,4),(2,4),(3,4),(4,4),(5,4)]
            ]

    def digit_to_win(self,offset_x,offset_y,n,color=None):
        ni = int(n)
        if ni >= 0 and ni < 10:
            if color != None:
                for x,y in self.digit[int(ni)]:
                    self.addstr(offset_x+x,offset_y+y,' ',curses.A_REVERSE|curses.color_pair(config.COLOR_TOTAL+color))
            else:
                for x,y in self.digit[int(ni)]:
                    self.addstr(offset_x+x,offset_y+y,' ',curses.A_REVERSE)

    def blank_to_win(self, o):
        offset = [0, 8, 20, 28]
        for y in range(0,5):
            for x in range(0,6):
                self.addstr(offset[o]+x,y,' ',curses.A_REVERSE|curses.color_pair(config.COLOR_TOTAL+config.COLOR_FOCUS))

    def time_to_win(self,t):
        self.erase()
        tl = [ [0,0,int(t/600)],[8,0,(t%600)/60],[20,0,(t%60)/10],[28,0,t%10] ]
        self.digit_to_win(*tl[0])
        self.digit_to_win(*tl[1])
        self.digit_to_win(*tl[2])
        self.digit_to_win(*tl[3])
        self.addstr(16,1,' ',curses.A_REVERSE)
        self.addstr(17,1,' ',curses.A_REVERSE)
        self.addstr(16,3,' ',curses.A_REVERSE)
        self.addstr(17,3,' ',curses.A_REVERSE)
        if self.edit_timer:
            self.blank_to_win(self.edit_location)
            self.digit_to_win(*tl[self.edit_location],color=config.COLOR_SECONDARY)

    def reset(self):
        self.current_time = config.TIME_POMODORO_SEC

    def decrement(self):
        self.current_time -= 1

    def update(self):
        self.erase()
        self.time_to_win(self.current_time)

    def start_overtime(self):
        if self.get_phase() != 2:
            self.set_phase(2)
            self.overtime.set_phase(2)
            self.overtime.start()

    def refresh(self):
        super().refresh()

    def run(self):
        count = 0
        cum = 0

        start_time = self.current_time-1
        start = datetime.datetime.now()
        while self.get_phase() == 1:
            duration = int((datetime.datetime.now() - start).total_seconds())
            self.current_time = start_time - duration
            if self.current_time < 0:
                self.current_time = 0

            self.update()
            self.refresh()
            if self.current_time == 0:
                globals.interface.alert()
                mb = globals.messageboard
                mb.pop_and_message("[SPACE]: Stop/Reset, [ENTER]: Deduct break time")
                self.start_overtime()

                log.debug("adding task to database")
                globals.database.add_pomodoro_now(self.taskswitcher.get_task())
                log.debug("added task")
                self.weekview.reload()
                self.weekview.update_week()
                self.weekview.refresh()
                break

            time.sleep(1)

        self.running_lock.acquire()
        self.running = False
        self.running_lock.release()

    def get_running(self):
        self.running_lock.acquire()
        r = self.running
        self.running_lock.release()
        return r

    def set_running(self,r):
        self.running_lock.acquire()
        self.running = r
        self.running_lock.release()

    def start(self):
        self.running_lock.acquire()
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run,name="Timer")
            self.thread.setDaemon(True)
            self.thread.start()
        self.running_lock.release()

    def edit_toggle(self):
        if self.phase == 0:
            self.edit_timer = not self.edit_timer
            self.edit_location = 0

    def edit_enable(self):
        if self.phase == 0:
            if not self.edit_timer:
                self.edit_old_time = self.current_time
            self.edit_timer = True
            self.edit_location = 0
            self.taskswitcher.disable()

    def edit_cancel(self):
        if self.edit_timer:
            self.current_time = self.edit_old_time
        self.edit_disable()

    def edit_disable(self):
        self.edit_timer = False
        self.taskswitcher.enable()

    def edit_next(self):
        if self.edit_timer:
            self.edit_location += 1
            if self.edit_location == 4:
                self.edit_disable()

    def edit_time(self, num):
        if self.edit_timer:
            loc = self.edit_location

            tmp = list(sec_to_time(self.current_time))
            if loc == 0:
                if num >= 6:
                    tmp[1] = "1"
                    num -= 6
                else:
                    tmp[0] = "0"
                    tmp[1] = "0"

                tmp[3] = str(num)
            elif loc == 1:
                tmp[4] = str(num)
            elif loc == 2:
                if num < 6:
                    tmp[6] = str(num)
                else:
                    self.edit_location -= 1
            elif loc == 3:
                tmp[7] = str(num)

            self.current_time = time_to_sec("".join(tmp))
            self.edit_next()

    def set_phase(self,p):
        self.phase_lock.acquire()
        self.phase = p
        self.phase_lock.release()

    def get_phase(self):
        self.phase_lock.acquire()
        phase = self.phase
        self.phase_lock.release()
        return phase

    def shift(self):
        if not self.edit_timer:
            if self.get_phase() == 0:
                if self.current_time == 0:
                    self.set_phase(0)
                    self.current_time = config.TIME_POMODORO_SEC
                    self.update()
                    self.refresh()
                else:
                    self.set_phase(1)
                    self.start()
                    if not self.get_running():
                        self.set_phase(0)
            elif self.get_phase() == 1:
                self.set_phase(0)
            elif self.get_phase() == 2:
                self.set_phase(0)
                self.overtime.set_phase(0)
                if self.current_time == 0:
                    self.current_time = config.TIME_POMODORO_SEC
                self.overtime.update()
                self.overtime.refresh()
                self.update()
                self.refresh()

