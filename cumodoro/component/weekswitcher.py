import curses
import sys
import datetime
import cumodoro.config as config
from cumodoro.component.frame import Frame
import cumodoro.globals as globals
from cumodoro.timeconvert import *
import types
from cumodoro.component.window import Window
from cumodoro.error import *
import logging

log = logging.getLogger('cumodoro')

class Weekswitcher(Window):
    def __init__(self):
        super(Weekswitcher,self).__init__()

        self.update_current_time()
        self.frame_titles = [ "week_frame" , "year_frame", "level_frame" ]
        self.values = [ [True,self.current_week,False], [True,self.current_year,False], [True,globals.database.levels-1,False] ]

        frame = Frame()
        frame.set_size(16,1)
        frame.name = "Level  "
        frame.title = "level_frame"
        self.add_frame(frame.title,frame)
        self.level_frame = frame

        frame = Frame()
        frame.set_size(16,1)
        frame.name = "Year   "
        frame.title = "year_frame"
        self.add_frame(frame.title,frame)
        self.year_frame = frame

        frame = Frame()
        frame.set_size(16,1)
        frame.name = "Week   "
        frame.title = "week_frame"
        self.add_frame(frame.title,frame)
        self.week_frame = frame

        for i in range(len(self.frame_titles)):
            frame = self.frames[self.frame_titles[i]]
            frame.switcher = self
            frame.idx = i

        self.update_frame_patch()
        self.current_frame = 0
        self.get_frame().selected = True
        self.enable()

    def reset(self):
        self.values = [ [True,self.current_week,False], [True,self.current_year,False], [True,globals.database.levels-1,False] ]

    def update(self):
        self.update_current_time()
        super().update()

    def get_week(self):
        return self.values[0][1]

    def get_year(self):
        return self.values[1][1]

    def get_level(self):
        return self.values[2][1]

    def mondayinweek(self,year,week):
        ret = datetime.datetime.strptime('%04d-%02d-1' % (year, week), '%Y-%W-%w')
        if datetime.date(year, 1, 4).isoweekday() > 4:
            ret -= datetime.timedelta(days=7)
        return ret

    def update_current_time(self):
        today = datetime.date.today()
        self.current_year = today.year
        self.current_week = today.isocalendar()[1]
        self.current_day = today.weekday()

        try:
            if self.values[0][1] < self.current_week:
                self.values[0][2] = True
            if self.values[1][1] < self.current_year:
                self.values[1][2] = True
        except: pass

    def get_week_dates(self,year=None,week=None):
        weekstart = None
        if year == None:
            weekstart = self.mondayinweek(self.values[1][1],self.values[0][1])
        else:
            weekstart = self.mondayinweek(year,week)
        weekstop = weekstart + datetime.timedelta(days=7)
        return ( weekstart, weekstop )

    def enable(self):
        self.enabled = True
        for frame in self.frames.values():
            frame.enabled = True

    def disable(self):
        self.enabled = False
        for frame in self.frames.values():
            frame.enabled = False

    def update_frame_patch(self):
        def update_patch(target):
            target.erase()

            color = config.COLOR_FOCUS
            if target.enabled and target.selected:
                target.addstr(0,0,str(target.name),curses.A_BOLD)
            else:
                target.addstr(0,0,str(target.name))

            value = target.switcher.values[target.idx]
            offset = len(target.name)
            if target.enabled and value[0]:
                if target.selected:
                    target.addstr(offset,0,"\u25C0", curses.color_pair(color))
                else:
                    target.addstr(offset,0,"\u25C0")
            else:
                if target.enabled and target.selected:
                    target.addstr(offset,0,"\u25C1", curses.color_pair(color))
                else:
                    target.addstr(offset,0,"\u25C1")

            if target.enabled and value[2]:
                if target.selected:
                    target.addstr(offset+7,0,"\u25B6", curses.color_pair(color))
                else:
                    target.addstr(offset+7,0,"\u25B6")
            else:
                if target.enabled and target.selected:
                    target.addstr(offset+7,0,"\u25B7", curses.color_pair(color))
                else:
                    target.addstr(offset+7,0,"\u25B7")

            target.addstr(offset+2+(4-len(str(value[1]))),0,str(value[1]))

        for i in range(len(self.frame_titles)):
            frame = self.get_frame(i)
            frame.selected = False
            frame.update = types.MethodType(update_patch,frame)

    def set_position(self,x,y):
        self.frames["week_frame"].set_position(x,y)
        self.frames["year_frame"].set_position(x,y+1)
        self.frames["level_frame"].set_position(x,y+2)

    def get_frame(self,n = None):
        if n == None:
            return self.frames[self.frame_titles[self.current_frame]]
        else:
            return self.frames[self.frame_titles[n]]

    def down(self):
        if self.current_frame+1 < len(self.frame_titles):
            self.get_frame().selected = False
            self.current_frame += 1
            self.get_frame().selected = True

    def up(self):
        if self.current_frame-1 >= 0:
            self.get_frame().selected = False
            self.current_frame -= 1
            self.get_frame().selected = True

    def left(self):
        frame = self.get_frame()
        i = frame.idx
        if frame.title == "level_frame":
            if self.values[i][1] - 1 >= 0:
                self.values[i][1] -= 1
                self.values[i][2] = True
                if self.values[i][1] == 0:
                    self.values[i][0] = False

        elif frame.title == "year_frame":
            self.values[0][2] = True
            self.values[i][2] = True
            self.values[i][1] -= 1

        elif frame.title == "week_frame":
            self.values[i][2] = True
            if self.values[i][1] == 1:
                self.values[i][1] = 52
                self.values[1][1] -= 1
            else:
                self.values[i][1] -= 1
                self.values[i][2] = True

        if self.values[1][1] < self.current_year and self.values[0][1] <= self.current_week:
            self.values[1][2] = True
        else:
            self.values[1][2] = False

    def right(self):
        frame = self.get_frame()
        i = frame.idx
        if frame.title == "level_frame":
            if self.values[i][1] + 1 < globals.database.levels:
                self.values[i][1] += 1
                self.values[i][0] = True
                if self.values[i][1] == globals.database.levels-1:
                    self.values[i][2] = False

        elif frame.title == "year_frame":
            if self.values[i][1] < self.current_year and self.values[0][1] <= self.current_week:
                self.values[i][1] += 1
                if self.values[i][1] == self.current_year:
                    self.values[i][2] = False

        elif frame.title == "week_frame":
            if self.values[1][1] < self.current_year or self.values[0][1] < self.current_week:
                self.values[i][1] += 1
                if self.values[i][1] == 53:
                    self.values[i][1] = 1
                    self.values[1][1] += 1

        if self.values[1][1] < self.current_year or self.values[0][1] < self.current_week:
            self.values[0][2] = True
        else:
            self.values[0][2] = False

        if self.values[1][1] < self.current_year and self.values[0][1] <= self.current_week:
            self.values[1][2] = True
        else:
            self.values[1][2] = False

