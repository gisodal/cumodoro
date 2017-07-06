import curses
import sys
import datetime
import cumodoro.config as config
from cumodoro.timeconvert import *
from cumodoro.component.frame import Frame
import cumodoro.globals as globals
from cumodoro.error import *
from collections import deque
import logging

log = logging.getLogger('cumodoro')

class Taskview(Frame):
    def __init__(self):
        super().__init__()
        self.shapes = ['\u25CF']
        self.edit_task_list = []

    def update(self):
        self.erase()
        if None in globals.database.full_task_list:

            q = deque([[1,None,x] for x in self.full_task_list[None]])
            while q:
                level,parent,idx = q.popleft()
                active = globals.database.tasks[idx].active
                q.extend([[level+1,idx,x] for x in globals.database.full_task_list[idx]])

    def right(self):
        pass

    def left(self):
        pass

    def up(self):
        pass

    def down(self):
        pass

    def delete_task(self):
        pass


