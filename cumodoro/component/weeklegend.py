import curses
import sys
import datetime
from cumodoro.component.frame import Frame
import cumodoro.globals as globals
import logging
from cumodoro.error import *

log = logging.getLogger('cumodoro')

class Weeklegend(Frame):
    def __init__(self):
        super(Weeklegend,self).__init__()
        self.weekview = globals.interface.windows["Weekview"].frames["weekview_frame"]

    def create(self):
        self.size = [globals.X-self.position[0]+1,globals.Y-self.position[1]-1]
        super().create()

    def update_legend(self):
        table = []
        row_width = [len("Level "+str(i)) for i in range(globals.database.levels)]
        legend = self.weekview.legend
        levels = 0
        y = 0
        for color,taskdict in legend.items():
            for task,shape in taskdict.items():
                row = []
                row.append((self.weekview.shapes[shape],curses.color_pair(color)))
                for i,t in enumerate(globals.database.task_chain[task]):
                    desc = globals.database.tasks[t[0]].desc
                    if row_width[i] < len(desc):
                        row_width[i] = len(desc)
                    row.append(str(desc))
                    if levels < i+1:
                        levels = i+1

                table.append(row)

        if levels > 0:
            # draw table
            for l in range(levels):
                x = 2+l*3+sum(row_width[0:l])+1
                self.addstr(x+2,0,"Level "+str(l+1))
                for y in range(len(table)+2):
                    if l > 0:
                        self.addstr(x,y,'\u2502')
                    else:
                        self.addstr(x,y,'\u2503')

            self.addstr(0,1,'\u2501'*(5+3*levels+sum(row_width[0:levels])))
            self.addstr(3,1,'\u254B')
            for l in range(1,levels):
                self.addstr(2+l*3+sum(row_width[0:l])+1,1,'\u253F')

            # print legend
            for y,row in enumerate(table):
                self.addstr(1,y+2,row[0][0],row[0][1])
                for col,entry in enumerate(row[1:]):
                    x = 5+sum(row_width[0:col])+(col*3)
                    if entry == None:
                        entry = "None"
                    self.addstr(x,y+2,entry)

    def print_colors(self):
        for x in range(len(self.weekview.colors)):
            c = self.weekview.colors[x]
            self.addstr(4+3*x,24,'\u25CF',curses.color_pair(c))

        for x in range(16):
            self.addstr(4+3*x,21,'\u25CF',curses.color_pair(x))
            self.addstr(4+3*x,22,str(x))
        rows = 20

        for y in range(40):
            for x in range(6):
                if y*6+x > 255:
                    break
                xi = 4+2*x
                yi = 2*y
                d = int(yi/rows)
                xi = xi + (d*20)
                yi = yi % rows
                self.addstr(xi,yi,'\u25CF',curses.color_pair(16+y*6+x))
                self.addstr(xi,yi+1,str(x%10))

        for y in range(10):
            for d in range(4):
                self.addstr(d*20,1+y*2,str(16+6*(d*10+y)))


    def update_size(self,X,Y):
        if X >= self.size[0]:
            self.window.resize(X+1,self.size[1])

        if Y > self.size[1]:
            self.window.resize(self.size[0],Y)

    def update(self):
        self.erase()
        if self.weekview.level > 0:
            self.update_legend()

