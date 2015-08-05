import curses
import sys
import time
import cumodoro.config as config
import cumodoro.globals as globals
from cumodoro.component.frame import Frame
import threading
import logging
log = logging.getLogger('cumodoro')

class Messageboard(Frame):
    def __init__(self):
        super().__init__()
        self.screen = globals.interface.screen
        self.name = "Messageboard"
        self.focus = True
        self.msg = {}
        self.lock = threading.Lock()
        self.alert_msg = [0,0,"",None]

    def alert(self,msg):
        def run(target):
            idx = threading.current_thread().ident
            while True:
                target.lock.acquire()
                msg = target.alert_msg
                if msg[0] != idx:
                    target.lock.release()
                    return

                if msg[1] == 0:
                    target.lock.release()
                    break

                msg[1] -= 1
                target.lock.release()
                time.sleep(1)

            target.erase()
            target.update()
            target.refresh()

        self.lock.acquire()
        self.window.erase()
        self.addstr(0,0,str(msg))
        self.chgat(0,0,self.size[0]-1,curses.color_pair(config.COLOR_TOTAL+config.COLOR_FOCUS))
        self.refresh()

        self.thread = threading.Thread(target=run,name="Alert",args=(self,))
        self.thread.setDaemon(True)
        self.thread.start()
        self.alert_msg = [self.thread.ident,config.MESSAGE_TIME,msg,self.get_idx()]
        self.lock.release()

    def create(self):
        X = globals.X
        Y = globals.Y
        self.size = [X+2,1]
        self.position = [0,Y-1]
        super().create()

    def erase(self):
        self.lock.acquire()
        if self.alert_msg[3] != self.get_idx() or self.alert_msg[1] == 0:
            self.alert_msg[1] = 0
            self.window.erase()
        self.lock.release()

    def update(self):
        self.erase()
        self.lock.acquire()
        try:
            idx = self.get_idx()
            if self.alert_msg[3] != idx or self.alert_msg[1] == 0:
                self.alert_msg[1] = 0
                timer = globals.interface.windows["Timer"].frames["timer_frame"]
                if idx == "Timer" or timer.get_phase() == 0:
                    if idx in self.msg:
                        if len(self.msg[idx]) > 0:
                            self.addstr(0,0,self.msg[idx][-1])
        except: pass
        self.lock.release()

    def clear(self):
        idx = self.get_idx()
        if idx in self.msg:
            while len(self.msg[idx]) > 0:
                self.msg[idx].pop()

    def pop_and_message(self,m):
        idx = self.get_idx()
        if idx not in self.msg:
            self.msg.update({idx:[]})

        if len(self.msg[idx]) > 0:
            self.msg[idx].pop()
        self.msg[idx].append(m)
        self.update()
        self.refresh()

    def pop(self):
        idx = self.get_idx()
        if idx in self.msg:
            if len(self.msg[idx]) > 0:
                self.msg[idx].pop()

        self.update()
        self.refresh()

    def get_idx(self):
        w = globals.interface.get_window()
        if w == None:
            return None
        else:
            return w.name

    def message(self, m, w = None):
        idx = w
        if idx == None:
            idx = self.get_idx()

        if idx not in self.msg:
            self.msg.update({idx:[]})

        self.msg[idx].append(m)
        self.update()
        self.refresh()

