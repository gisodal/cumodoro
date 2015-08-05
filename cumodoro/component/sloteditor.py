from cumodoro.component.frame import Frame
from cumodoro.component.input import Input
import cumodoro.database as database
import cumodoro.globals as globals
import cumodoro.config as config
from cumodoro.timeconvert import *
from copy import copy, deepcopy
from cumodoro.component.taskcreator import Taskcreator
from cumodoro.component.element import Element

import curses
import sys
import logging

log = logging.getLogger('cumodoro')

class Sloteditor(Frame):
    def __init__(self):
        super().__init__()
        self.size = [50,30]
        self.selected_input = False
        self.state = None
        self.modified = False
        self.slots = []
        self.titles = []
        self.offset = [0,11,22]

    def reload(self):
        self.slots = deepcopy(config.TIME_SLOT)
        self.titles = deepcopy(config.TIME_SLOT_NAME)

    def sync(self):
        if self.modified:
            self.modified = False
            self.slots
            self.titles

            globals.database.update_config("TIME_SLOT",self.slots)
            globals.database.update_config("TIME_SLOT_NAME",self.titles)

            globals.database.load_config()
            config.init()
            weekview = globals.interface.windows["Weekview"].frames["weekview_frame"]
            weekview.reload()
            weekview.update()

    def handle_input(self):
        interface = globals.interface
        screen = interface.screen

        self.selected_input = True
        self.reload()
        self.current = [0,0]
        mb = globals.messageboard
        mb.message("[ENTER]: Save, [ESC]: Cancel, [e]: Edit, [i]: Insert, [d]: Delete")
        while True:
            self.update()
            self.refresh()
            key = screen.getkey()
            if interface.resize(key):
                pass
            elif key == 'q':
                sys.exit(0)
            elif key == "KEY_RIGHT" or key == "l":
                self.right()
                self.update()
                self.refresh()
            elif key == "KEY_LEFT" or key == "h":
                self.left()
                self.update()
                self.refresh()
            elif key == "KEY_UP" or key == "k":
                self.up()
                self.update()
                self.refresh()
            elif key == "KEY_DOWN" or key == "j":
                self.down()
                self.update()
                self.refresh()
            elif key == "d":
                if len(self.slots) > 0:
                    self.modified = True
                    del self.slots[self.current[0]]
                    del self.titles[self.current[0]]
                    if self.current[0] == len(self.slots):
                        self.current[0] -= 1

                self.update()
                self.refresh()
            elif key == "i":
                if len(self.slots) < 10:
                    self.modified = True
                    self.slots.append(('00:00:00','00:00:00'))
                    self.titles.append("")
                    self.current = [len(self.slots)-1,0]
                    self.update()
                    self.refresh()
                else:
                    mb.alert("Cannot add more than 10 slots")

            elif key == "e":
                i,j = self.current
                value = [self.slots[i][0],self.slots[i][1],self.titles[i]]

                inp = Input()
                if self.current[1] < 2:
                    inp.init("time")
                else:
                    inp.init("text")

                inp.value = value[j]
                pos = self.position
                inp.set_position(pos[0]+self.offset[j],pos[1]+i)
                if j < 2:
                    inp.set_size(9,1)
                inp.focus = True
                inp.selected_input = True
                inp.name = 'input'
                inp.create()
                inp.erase()
                inp.update()
                inp.refresh()
                inp.handle_input()
                if inp.value != value[j]:
                    self.modified = True
                    if j == 0:
                        self.slots[i] = (inp.value,self.slots[i][1])
                    elif j == 1:
                        self.slots[i] = (self.slots[i][0],inp.value)
                    else:
                        self.titles[i] = inp.value
                del inp

                self.update()
                self.refresh()
            elif len(key) == 1 and ord(key) == 27:
                self.reload()
                break
            elif len(key) == 1 and ord(key) == 13:
                if not self.check():
                    break
            else:
                log.debug("unregistered key: '"+str(key)+"'")

        if self.modified:
            self.sort()
            self.update()
            self.refresh()
            self.current[0] = -1

        self.selected_input = False
        self.sync()
        mb.pop()

    def check(self):
        mb = globals.messageboard
        for i in range(len(self.slots)):
            if self.slots[i][0] == self.slots[i][1]:
                mb.alert("Slot "+str(i+1)+" has duration 0")
                return True
            if self.titles[i] == "":
                mb.alert("Slot "+str(i+1)+" has no title")
                return True

        for i in range(len(self.slots)):
            time_start, time_stop = time_to_sec(self.slots[i][0]),time_to_sec(self.slots[i][1])

            for j in range(len(self.slots)):
                if i == j:
                    continue

                start, stop = time_to_sec(self.slots[j][0]),time_to_sec(self.slots[j][1])
                overlap = False
                if start > stop:
                    if (time_start >= start or time_start < stop):
                        overlap = True
                    elif (time_stop >= start or time_stop < stop):
                        overlap = True
                else:
                    if (time_start >= start and time_start < stop):
                        overlap = True
                    elif (time_stop >= start and time_stop < stop):
                        overlap = True

                if overlap:
                    mb.alert("Slot "+str(i+1)+" overlaps with slot "+str(j+1))
                    return True

        return False

    def right(self):
        if self.current[1] < 2:
            self.current[1] += 1

    def left(self):
        if self.current[1] > 0:
            self.current[1] -= 1

    def up(self):
        if self.current[0] > 0:
            self.current[0] -= 1

    def down(self):
        if self.current[0] < len(self.slots)-1:
            self.current[0] += 1

    def sort(self):
        changed = True
        while changed:
            changed = False
            for i in range(len(self.slots)-1):
                if time_to_sec(self.slots[i][0]) > time_to_sec(self.slots[i+1][0]):
                    tmp = self.slots[i]
                    self.slots[i] = self.slots[i+1]
                    self.slots[i+1] = tmp
                    tmp = self.titles[i]
                    self.titles[i] = self.titles[i+1]
                    self.titles[i+1] = tmp
                    changed = True

    def update(self):
        self.erase()

        if not self.selected_input:
            slots = config.TIME_SLOT
            titles = config.TIME_SLOT_NAME
        else:
            slots = self.slots
            titles = self.titles

        if len(slots) == 0:
            self.addstr(0,0,"no slots")
        else:
            for i in range(len(slots)):
                if titles[i] == "":
                    value = [slots[i][0],slots[i][1],"none"]
                else:
                    value = [slots[i][0],slots[i][1],titles[i]]

                self.addstr(9,i,'-')
                for j in range(3):
                    if self.selected_input and i == self.current[0] and j == self.current[1]:
                        self.addstr(self.offset[j],i,value[j],curses.color_pair(config.COLOR_FOCUS))
                    else:
                        self.addstr(self.offset[j],i,value[j])

