import curses
import sys
import datetime
import time
import math
import cumodoro.config as config
from cumodoro.timeconvert import *
from copy import copy, deepcopy
from cumodoro.component.frame import Frame
import cumodoro.globals as globals
import logging
from cumodoro.error import *

log = logging.getLogger('cumodoro')

class Weekview(Frame):
    def __init__(self):
        super(Weekview,self).__init__()
        self.shapes = ['\u25CF','\u25C6','\u25A0','\u25B2','\u25B6','\u25BC','\u25C0','\u25D0','\u25D1','\u25D2','\u25D3','\u25E7','\u25E8','\u25E9','\u25EA', '\u25ED', '\u25EE','\u2738','\u2691','\u272A','\u263B','\u2665','\u2663','\u2660','\u25B0' ]
        self.switcher = globals.interface.windows["Weekview"].frames["weekswitcher_frame"]
        self.width = 0
        self.edit = 0
        self.edit_location = [0,0,0]
        self.edit_enabled = True
        self.backorder = []
        self.edit_element = None

    def create(self):
        self.size = [globals.X-self.position[0]+1,self.size[1]]
        super().create()

    def reload(self):
        self.load_data()
        self.load_pomodoros()

    def backup(self):
        t = self.get_task()
        if t[0] == None:
            self.edit_element = None
        else:
            self.edit_element = deepcopy(t)

    def cancel(self):
        daynr,slotnr,x = self.edit_location
        if self.pomodoros[daynr][slotnr][x][0] == None:
            for i in range(len(self.backorder)):
                if self.backorder[i][0] == self.edit_location:
                    del self.backorder[i]

            del self.pomodoros[daynr][slotnr][x]
        else:
            self.pomodoros[daynr][slotnr][x] = self.edit_element

    def set_edit(self,e):
        if e == 0:
            self.edit_location = [0,0,0]

        if e == 2:
            if self.edit != 2:
                self.backup()

            self.edit_enabled = False
        else:
            self.edit_enabled = True

        self.edit = e

    def empty_backorder(self):
        del self.backorder
        self.backorder = []

    def flush_backorder(self):
        for t in self.backorder:
            globals.database.alter_pomodoro_task(None,t[1],t[2])

        self.empty_backorder()

    def get_time(self):
        if self.edit:
            daynr,slotnr,x = self.edit_location
            time = None
            if slotnr < len(config.TIME_SLOT_SEC):
                if len(self.pomodoros[daynr][slotnr]) > 0:
                    time = self.pomodoros[daynr][slotnr][-1][5] + datetime.timedelta(seconds=(config.TIME_BREAK_SEC+config.TIME_POMODORO_SEC))
                    if self.in_slot(time) != slotnr:
                        time = self.pomodoros[daynr][slotnr][-1][5] + datetime.timedelta(seconds=1)
                        if self.in_slot(time) != slotnr:
                            time = self.pomodoros[daynr][slotnr][-1][5]
                            if self.in_slot(time) != slotnr:
                                time = config.TIME_SLOT_SEC[slotnr][1]

                else:
                    time = self.switcher.get_week_dates()[0]
                    time += datetime.timedelta(days=daynr)
                    time += datetime.timedelta(seconds=config.TIME_SLOT_SEC[slotnr][0])
            else:
                if len(self.pomodoros[daynr][slotnr]) > 0:
                    time = self.pomodoros[daynr][slotnr][-1][5] + datetime.timedelta(seconds=(config.TIME_BREAK_SEC+config.TIME_POMODORO_SEC))
                    t = time_to_sec(time.time().strftime('%H:%M:%S'))
                    if self.in_slot(t) >= 0:
                        time = self.pomodoros[daynr][slotnr][-1][5]
                else:
                    append_slot = -1
                    for i in reversed(range(len(config.TIME_SLOT_SEC))):
                        t = config.TIME_SLOT_SEC[i][1] + config.TIME_BREAK_SEC + config.TIME_POMODORO_SEC
                        if self.in_slot(t) < 0:
                            append_slot = i
                            break

                    if append_slot >= 0:
                        time_sec = config.TIME_SLOT_SEC[append_slot][1] + config.TIME_BREAK_SEC + config.TIME_POMODORO_SEC
                        time = self.switcher.get_week_dates()[0]
                        time += datetime.timedelta(days=daynr)
                        time += datetime.timedelta(seconds=time_sec)

            if time == None or (slotnr == len(config.TIME_SLOT) and self.in_slot(time) >= 0) or (slotnr < len(config.TIME_SLOT) and self.in_slot(time) < 0):
                raise CumodoroError("No suitable time found for timeslot "+str(slotnr)+" at location "+str(x)+": "+str(config.TIME_SLOT[slotnr]))

            return time
        else:
            return None

    def update_database(self):
        if self.edit == 2:
            self.load_size()
            self.load_locations()

            t = self.get_task()
            idx = t[0]
            if idx == None:
                for pomo in self.backorder:
                    if self.backorder[0] == self.edit_location:
                        self.backorder[1] = t[1]
                        return

                self.backorder.append([self.edit_location, t[1], t[5]])
            else:
                globals.database.alter_pomodoro_task(t[0],t[1])
        else:
            raise CumodoroError("cannot alter database in edit state "+str(self.edit))

    def set_task(self,task):
        t = self.get_task()
        shape = self.get_shape(task)
        task_level = self.get_task_level(task)
        color = globals.database.colors[task_level][self.level]
        t[1] = task
        t[3] = shape
        t[4] = color

    def update_pomodoro(self,location,shape,task):
        self.level = self.switcher.values[2][1]
        color = 0
        if task == -1:
            self.addstr(location[0],location[1]," ")
        elif task != None:
            if task in globals.database.colors:
                color = globals.database.colors[task][self.level]
            self.addstr(location[0],location[1],self.shapes[shape],curses.color_pair(color))
        else:
            self.addstr(location[0],location[1],self.shapes[shape],curses.color_pair(color))

    def load_data(self):
        week = self.switcher.get_week_dates()

        if week[0].weekday() != 0:
            raise CumodoroError("week delimiters do not start on monday")

        self.data = globals.database.request("SELECT id,time,task FROM pomodoros WHERE time >= ? AND time < ?",week)

    def in_slot(self,t):
        sec = None
        if type(t) is not int:
            sec = time_to_sec(t.time().strftime('%H:%M:%S'))
        else:
            sec = t

        for slotnr in reversed(range(0,len(config.TIME_SLOT_SEC))):
            start = config.TIME_SLOT_SEC[slotnr][0]
            stop = (config.TIME_SLOT_SEC[slotnr][1]+config.TIME_POMODORO_SEC)%(60*60*24)
            if start > stop:
                if sec >= start or sec < stop:
                    return slotnr
            elif sec >= start and sec < stop:
                return slotnr

        return -1

    def get_shape(self,task):
        task_level = self.get_task_level(task)
        color = globals.database.colors[task_level][self.level]
        shape = 0
        if color not in self.legend:
            self.legend.update({color:{task_level:shape}})
        else:
            if task_level not in self.legend[color]:
                shape = len(self.legend[color])
                shape = shape % len(self.shapes)
                self.legend[color].update({task_level:shape})
            else:
                shape = self.legend[color][task_level]

        return shape

    def get_task_level(self,task):
        task_level = None
        if self.level > 0:
            length = len(globals.database.task_chain[task])
            if self.level-1 < length:
                task_level = globals.database.task_chain[task][self.level-1][0]
            elif length > 0:
                task_level = globals.database.task_chain[task][-1][0]

        return task_level

    def load_locations(self):
        for slotnr in range(0,len(self.slot_size)):
            offset = 7 + 2*slotnr + 2*sum(self.slot_size[0:slotnr])
            for daynr in range(0,7):
                for x in range(0,len(self.pomodoros[daynr][slotnr])):
                    self.pomodoros[daynr][slotnr][x][2] = [offset+x*2,2+daynr]

        self.width = 7 + sum(self.slot_size) * 2 + (len(self.slot_size)-1) * 2

    def load_size(self):
        self.slot_size = [s+1 for s in config.SLOT_SIZE[:]]

        for slotnr in range(len(config.TIME_SLOT_NAME)):
            title_size = math.ceil(len(config.TIME_SLOT_NAME[slotnr])/2) + 1;
            if self.slot_size[slotnr] < title_size:
                self.slot_size[slotnr] = title_size

        for daynr in range(7):
            for slotnr in range(len(config.SLOT_SIZE)):
                try:
                    length = len(self.pomodoros[daynr][slotnr])
                    if length+1 > self.slot_size[slotnr]:
                        self.slot_size[slotnr] = length+1
                except: pass

    def load_pomodoros(self):
        # pomodoro = [idx,task,locations,shape,color,time]
        self.level = self.switcher.values[2][1]
        self.pomodoros = [[[] for slots in range(len(config.TIME_SLOT)+1)] for days in range(7)]
        self.legend = {}
        for idx,time,task in self.data:
            slotnr = self.in_slot(time)

            if slotnr < 0:
                slotnr = len(config.TIME_SLOT_SEC)

            daynr = time.weekday()
            shape = self.get_shape(task)
            task_level = self.get_task_level(task)
            color = globals.database.colors[task_level][self.level]

            self.pomodoros[daynr][slotnr].append([idx,task,[0,0],shape,color,time])

        for daynr in range(7):
            for slotnr in range(len(self.pomodoros[daynr])):
                try:
                    self.pomodoros[daynr][slotnr] = sorted(self.pomodoros[daynr][slotnr],key=lambda x: x[5])
                except: pass

        self.load_size()
        self.load_locations()

    def update_edit(self):
        if self.edit:
            daynr,slotnr,x = self.edit_location
            location = None
            if x < len(self.pomodoros[daynr][slotnr]):
                location = self.pomodoros[daynr][slotnr][x][2]
            else:
                offset = 7 + 2*slotnr + 2*sum(self.slot_size[0:slotnr])
                location = [offset+x*2,2+daynr]

            if self.edit_enabled:
                self.addstr(location[0]-1,location[1],'\u276A',curses.color_pair(config.COLOR_FOCUS)|curses.A_BOLD)
                self.addstr(location[0]+1,location[1],'\u276B',curses.color_pair(config.COLOR_FOCUS)|curses.A_BOLD)
            else:
                self.addstr(location[0]-1,location[1],'\u276A',curses.A_BOLD)
                self.addstr(location[0]+1,location[1],'\u276B',curses.A_BOLD)

    def update_week(self):
        for slotnr in range(0,len(self.slot_size)):
            for daynr in range(0,7):
                for x in range(0,len(self.pomodoros[daynr][slotnr])):
                    idx,task,location,shape,color,time = self.pomodoros[daynr][slotnr][x]
                    self.addstr(location[0], location[1],self.shapes[shape],curses.color_pair(color))

        self.update_edit()

    def update_table(self):
        weekday = [ "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" ]

        self.addstr(1,0,"DAY")
        for daynr in range(0,7):
            if self.switcher.get_week() == self.switcher.current_week and self.switcher.get_year() == self.switcher.current_year and self.switcher.current_day == daynr:
                self.addstr(1,2+daynr,weekday[daynr],curses.A_UNDERLINE|curses.A_BOLD)
            else:
                self.addstr(1,2+daynr,weekday[daynr])

        # vertical table line
        for x,y in [(5,i) for i in range(0,9)]:
            self.addstr(x,y,'\u2503')

        # horizontal table line
        width = 5 + len(self.slot_size)*2 + sum(self.slot_size)*2
        for x,y in [(i,1) for i in range(0,width)]:
            self.addstr(x,y,'\u2501')
        self.addstr(5,1,'\u254B')

        # horizontal separators
        for s in range(1,len(self.slot_size)):
            x = 7 + 2*(s-1) + 2*sum(self.slot_size[0:s])
            for y in range(0,9):
                self.addstr(x,y,'\u2502')
            self.addstr(x,1,'\u253F')

        # labels
        for s in range(0,len(config.TIME_SLOT_NAME)):
            x = 7 + 2*s + 2*sum(self.slot_size[0:s])
            self.addstr(x,0,config.TIME_SLOT_NAME[s])

    def update(self):
        self.erase()

        if self.width >= self.size[0]:
            self.destroy()
            self.size[0] = self.width+1
            self.create()

        self.update_table()
        self.update_week()

    def right(self):
        daynr,slotnr,x = self.edit_location
        if x < len(self.pomodoros[daynr][slotnr]):
            self.edit_location = [ daynr, slotnr, x+1 ]
        elif slotnr < len(self.pomodoros[daynr])-1:
            self.edit_location = [ daynr, slotnr+1, 0 ]

    def left(self):
        daynr,slotnr,x = self.edit_location
        if x > 0:
            self.edit_location = [ daynr, slotnr, x-1 ]
        elif slotnr > 0:
            self.edit_location = [ daynr, slotnr-1, len(self.pomodoros[daynr][slotnr-1]) ]

    def up(self):
        daynr,slotnr,x = self.edit_location
        if daynr > 0:
            if x < len(self.pomodoros[daynr-1][slotnr]):
                self.edit_location = [ daynr-1, slotnr, x ]
            else:
                self.edit_location = [ daynr-1, slotnr, len(self.pomodoros[daynr-1][slotnr]) ]

    def get_task(self):
        if self.edit:
            daynr,slotnr,x = self.edit_location
            if x < len(self.pomodoros[daynr][slotnr]):
                return self.pomodoros[daynr][slotnr][x]
            else:
                offset = 7 + 2*slotnr + 2*sum(self.slot_size[0:slotnr])
                x = len(self.pomodoros[daynr][slotnr])
                location = [offset+x*2,2+daynr]
                time = self.get_time()
                t = [None,None,location,0,0,time]
                if self.edit == 2:
                    self.pomodoros[daynr][slotnr].append(t)
                return t

        return None

    def delete_task(self):
        if self.edit:
            daynr,slotnr,x = self.edit_location
            length = len(self.pomodoros[daynr][slotnr])
            if length > 0:
                if x >= length-1 and x > 0:
                    self.edit_location[2] -= 1

                idx = self.pomodoros[daynr][slotnr][x][0]
                del self.pomodoros[daynr][slotnr][x]

                self.load_size()
                self.load_locations()

                if idx == None:
                    for i in range(len(self.backorder)):
                        if self.backorder[i][0] == self.edit_location:
                            del self.backorder[i]
                else:
                    globals.database.delete_pomodoro(idx)

    def down(self):
        daynr,slotnr,x = self.edit_location
        if daynr < 7-1:
            if x < len(self.pomodoros[daynr+1][slotnr]):
                self.edit_location = [ daynr+1, slotnr, x ]
            else:
                self.edit_location = [ daynr+1, slotnr, len(self.pomodoros[daynr+1][slotnr]) ]

