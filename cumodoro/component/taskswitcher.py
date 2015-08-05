import curses
import sys
import cumodoro.config as config
from cumodoro.component.frame import Frame
import cumodoro.globals as globals
from cumodoro.timeconvert import *
import types
from cumodoro.component.window import Window
from cumodoro.database import Task
from cumodoro.error import *
import logging

log = logging.getLogger('cumodoro')

class Taskswitcher(Window):
    def __init__(self):
        super(Taskswitcher,self).__init__()
        self.enabled = True
        self.width = 36
        self.size = [ self.width, 1 ]
        self.stack = []
        self.current_switcher = -1

        if len(globals.database.task_list) > 0:
            self.push_switcher()

        self.focus = False
        self.enable()


    def reset(self):
        self.current_switcher = -1

        for i in range(len(self.stack)):
            self.pop_switcher()

        if len(globals.database.task_list) > 0:
            self.push_switcher()

        self.focus = False
        self.enable()

    def set_task(self,t):
        self.current_switcher = -1
        for i in range(len(self.stack)):
            self.pop_switcher()

        if t != None:
            idx,task = t[0:2]
            if task != None or self.enabled:
                if task == None:
                    self.push_switcher()
                else:
                    fidx = globals.database.task_chain[task]
                    for n,idls in enumerate(fidx):
                        idx2,i2 = idls
                        self.push_switcher()
                        self.stack[n].current_task = i2
                        self.stack[n].selected = False

                    if self.get_task() != None and len(globals.database.task_list[self.get_task()]) > 0:
                        self.push_switcher()

                    if len(self.stack) > 0:
                        self.stack[-1].selected = True
                        self.current_switcher = len(self.stack)-1


    def pop_switcher(self):
        frame = self.stack.pop()
        self.del_frame(frame.title)
        frame.erase()
        frame.refresh()
        del frame.window
        del frame

    def push_switcher(self):
        frame = Frame()
        frame.name = "taskswitcher_element"
        frame.task_list = []
        frame.current_task = -1
        frame.enabled = True
        frame.selected = False

        def update_patch(target):
            target.erase()
            color = config.COLOR_FOCUS
            if target.enabled and target.current_task > -1:
                if target.selected:
                    target.addstr(0,0,"\u25C0", curses.color_pair(color))
                else:
                    target.addstr(0,0,"\u25C0")
            else:
                if target.enabled and target.selected:
                    target.addstr(0,0,"\u25C1", curses.color_pair(color))
                else:
                    target.addstr(0,0,"\u25C1")

            if target.enabled and target.current_task+1 < len(target.task_list):
                if target.selected:
                    target.addstr(target.size[0]-3,0,"\u25B6", curses.color_pair(color))
                else:
                    target.addstr(target.size[0]-3,0,"\u25B6")
            else:
                if target.enabled and target.selected:
                    target.addstr(target.size[0]-3,0,"\u25B7", curses.color_pair(color))
                else:
                    target.addstr(target.size[0]-3,0,"\u25B7")

            if target.current_task >= 0:
                desc = globals.database.tasks[target.get_task()].desc
                target.addstr(3,0,desc)

        def get_task_patch(target):
            if target.current_task >= 0:
                return target.task_list[target.current_task]
            else:
                return None

        def next_patch(target):
            if target.enabled and target.current_task+1 < len(target.task_list):
                target.current_task += 1

        def prev_patch(target):
            if target.enabled and target.current_task-1 >= -1:
                target.current_task -= 1

        def task_list_patch(target,tasks):
            target.task_list = tasks

        frame.update = types.MethodType(update_patch,frame)
        frame.next_task = types.MethodType(next_patch,frame)
        frame.prev_task = types.MethodType(prev_patch,frame)
        frame.set_task_list = types.MethodType(task_list_patch,frame)
        frame.get_task = types.MethodType(get_task_patch,frame)

        idx = len(self.stack)
        try:
            frame.set_position(self.position[0],self.position[1]+idx)
            frame.set_size(self.size[0],self.size[1])
            frame.create()
        except: pass
        frame.focus = True
        frame.set_task_list(globals.database.task_list[self.get_task()])
        #if self.get_task() != None:
        #    frame.set_task_list(globals.database.task_list[self.get_task()])
        #else:
        #    frame.set_task_list([])

        self.add_frame(str(idx),frame)
        self.stack.append(frame)
        if self.current_switcher == -1:
           self.current_switcher = 0
           self.stack[0].selected = True

    def set_position(self,x,y):
        self.position = [ x, y ]
        for level,frame in enumerate(self.stack):
            frame.set_position(self.position[0],self.position[1]+level)
            frame.set_size(self.size[0],self.size[1])

    def enable(self):
        self.enabled = True
        for f in self.stack:
            f.enabled = True

    def disable(self):
        self.enabled = False
        for f in self.stack:
            f.enabled = False

    def get_frame(self,level = None):
        if level == None:
            if len(self.stack) > 0:
                return self.stack[self.current_switcher]
        elif level != -1:
            if level < len(self.stack):
                return self.stack[level]

        return None

    def get_task(self):
        if len(self.stack) == 0:
            return None
        else:
            for i in reversed(range(0,len(self.stack))):
                frame = self.get_frame(i)
                idx = frame.get_task()
                if idx != None:
                    return idx

            return None

    def get_current_task(self):
        frame = self.get_frame()
        if frame == None:
            return None
        else:
            return frame.get_task()

    def get_color(self):
        idx = self.get_task()
        if idx != None:
            if idx in globals.database.tasks:
                return globals.database.tasks[idx].color

        return 0

    def down(self):
        if len(self.stack) > 0 and self.enabled:
            if self.current_switcher+1 < len(self.stack):
                self.get_frame().selected = False
                self.current_switcher += 1
                self.get_frame().selected = True

    def up(self):
        if len(self.stack) > 0 and self.enabled:
            if self.current_switcher-1 >= 0:
                self.get_frame().selected = False
                self.current_switcher -= 1
                self.get_frame().selected = True

    def left(self):
        if len(self.stack) > 0 and self.enabled:
            frame = self.get_frame()
            idx = frame.get_task()
            frame.prev_task()
            if idx != frame.get_task():
                for i in range(len(self.stack)-self.current_switcher-1):
                    self.pop_switcher()

                if self.get_current_task() != None and len(globals.database.task_list[self.get_task()]) > 0:
                    self.push_switcher()

    def right(self):
        if len(self.stack) > 0 and self.enabled:
            frame = self.get_frame()
            idx = frame.get_task()
            frame.next_task()
            if idx != frame.get_task():
                for i in range(len(self.stack)-self.current_switcher-1):
                    self.pop_switcher()

                if self.get_current_task() != None and len(globals.database.task_list[self.get_task()]) > 0:
                    self.push_switcher()

