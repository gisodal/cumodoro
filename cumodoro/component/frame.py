import curses
from cumodoro.error import *
import cumodoro.globals as globals
import logging
log = logging.getLogger('cumodoro')

class Frame(object):
    def __init__(self):
        self.exception_on_x = True
        self.focus = False
        self.manual_focus = True
        self.window = None
        self.name = ''
        self.size = [0,0]
        self.position = [0,0]
        self.created = False
        self.refresher = globals.refresher

    def set_focus(self,f):
        self.focus = f

    def set_manual_focus(self,f):
        self.manual_focus = f

    def set_size(self,x,y):
        self.size = [x,y]

    def set_position(self,x,y):
        self.position = [x,y]

    def destroy(self):
        if self.created:
            self.created = False
            del self.window
            self.window = None

    def erase(self):
        if self.created:
            self.window.erase()

    def update(self):
        log.error("called empty update function")

    def resize(self,X,Y):
        if self.created:
            self.size = [X, Y]
            self.window.resize(Y,X)

    def chgat(self,x,y,length,options):
        if self.created:
            if self.position[1]+y < globals.Y-1 or self.name == "Messageboard":
                width = globals.X - (self.position[0]+x)
                if width > 0:
                    if length > width:
                        length -= (length - width)

                    width = self.size[0] - x
                    if width > 0:
                        if x+length >= self.size[0]:
                            length = length-(length-width)
                    else:
                        return

                    try:
                        self.window.chgat(y,x,length,options)
                    except:
                        pass
                        #raise CursesBoundsError("[Window '"+self.name+"'] trying to change attribute with length "+str(length)+" at ("+str(x)+","+str(y)+") while window size is ("+str(self.size[0])+","+str(self.size[1])+")\n")

    def addstr(self,x,y,string,options=None):
        if self.created:
            if self.position[1]+y < globals.Y-1 or self.name == "Messageboard":
                conv_s = str(string)
                length = len(conv_s)
                width = globals.X - (self.position[0]+x)
                if width > 0:
                    if length > width:
                        conv_s = conv_s[0:length-(length-width)]
                        length = len(conv_s)

                    width = self.size[0] - x
                    if width > 0:
                        if x+length >= self.size[0]:
                            conv_s = conv_s[0:length-(length-width)]
                    else:
                        return

                    try:
                        if options == None:
                            self.window.addstr(y,x,conv_s)
                        else:
                            self.window.addstr(y,x,conv_s,options)
                    except:
                        pass
                        # raise CursesBoundsError("[Window '"+self.name+"'] trying to print string '"+conv_s+"' of size "+str(length)+" at ("+str(x)+","+str(y)+") while window size is ("+str(self.size[0])+","+str(self.size[1])+")\n")

    def create(self):
        if self.created:
            self.destroy()

        if self.position[0] <= globals.X and self.position[1] <= globals.Y and self.size[0] > 0 and self.size[1] > 0:
            try:
                self.window = curses.newwin(self.size[1],self.size[0],self.position[1],self.position[0])
                self.created = True
            except:
                self.window = None
                self.created = False

    def refresh(self):
        if self.created and self.focus and self.manual_focus:
            self.refresher.put(self.window)

        elif self.name != "taskswitcher_element":
            if not self.created:
                log.error("refreshing frame '"+self.name+"' but it is not created")
            elif self.name != "clock_frame" and self.name != "timer_frame" and self.name != "overtime_frame":
                log.error("refreshing frame '"+self.name+"' while not in focus ["+str(self.focus)+","+str(self.manual_focus)+"]")

