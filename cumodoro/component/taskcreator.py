from cumodoro.component.frame import Frame
from cumodoro.component.element import Element
import cumodoro.globals as globals
import cumodoro.config as config
import curses
import sys
import logging

log = logging.getLogger('cumodoro')

class Taskcreator(Frame):
    def __init__(self):
        super().__init__()
        self.focus = True
        self.set_size(34,1)
        self.e = None
        self.field = 0
        self.initialized = False

    def handle_input(self):
        interface = globals.interface
        screen = interface.screen

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
            elif len(key) == 1 and ord(key) == 27:
                self.e = None
                break
            elif len(key) == 1 and ord(key) == 127:
                self.del_char()
                self.update()
                self.refresh()
            elif len(key) == 1 and ord(key) == 13:
                self.field += 1
                if self.field >= 2:
                    if len(self.e.desc) == 0:
                        globals.messageboard.alert("Task cannot have empty title")
                        self.field -= 1
                    else:
                        break
            elif self.field == 1 and len(key) == 1 and (
                ( ord(key) >= ord('a') and ord(key) <= ord('z') ) or
                ( ord(key) >= ord('A') and ord(key) <= ord('Z') ) or
                key == " " or key == "-" or key == "_"):
                self.add_char(key)
                self.update()
                self.refresh()
            else:
                if len(key) == 1:
                    log.debug("unregistered key: '"+str(key)+"' ord: "+str(ord(key)))
                else:
                    log.debug("unregistered key: '"+str(key)+"'")

    def right(self):
        if self.field == 0:
            # FIXME color
            #if self.current_color_idx < len(config.COLORS)-1:
            #    self.current_color_idx += 1
            if self.current_color_idx < 256-1:
                self.current_color_idx += 1
                self.e.color = self.current_color_idx
                self.e.modified = True

        if self.field == 1:
            self.add_char("l")
            self.e.modified = True

    def left(self):
        if self.field == 0:
            if self.current_color_idx > 0:
                self.current_color_idx -= 1
                self.e.color = self.current_color_idx
                self.e.modified = True

        if self.field == 1:
            self.add_char("h")
            self.e.modified = True

    def add_char(self,c):
        if len(self.e.desc) <= 25:
            self.e.desc += c
            self.e.modified = True

    def del_char(self):
        if len(self.e.desc) > 0:
            self.e.desc = self.e.desc[0:-1]
            self.e.modified = True

    def init(self):
        if not self.initialized:
            if self.e == None:
                self.e = Element()
                self.e.modified = True
                self.current_color_idx = 0
            else:
                self.current_color_idx = 0
                colors = config.COLORS
                for i in range(len(colors)):
                    if self.e.color == colors[i]:
                        self.current_color_idx = i
                        break
                # FIXME color
                self.current_color_idx = self.e.color
            self.initialized = True

    def update(self):
        self.erase()
        self.init()
        colors = config.COLORS
        color = config.COLOR_FOCUS

        if self.current_color_idx > 0:
            if self.field == 0:
                self.addstr(0,0,"\u25C0", curses.color_pair(color))
            else:
                self.addstr(0,0,"\u25C0")
        else:
            if self.field == 0:
                self.addstr(0,0,"\u25C1", curses.color_pair(color))
            else:
                self.addstr(0,0,"\u25C1")

        # FIXME color
        #self.addstr(2,0,'\u25CF',curses.color_pair(colors[self.current_color_idx]))
        self.addstr(2,0,'\u25CF',curses.color_pair(self.current_color_idx))

        #if self.current_color_idx < len(colors) - 2:
        if self.current_color_idx < 256:
            if self.field == 0:
                self.addstr(4,0,"\u25B6", curses.color_pair(color))
            else:
                self.addstr(4,0,"\u25B6")
        else:
            if self.field == 0:
                self.addstr(4,0,"\u25B7", curses.color_pair(color))
            else:
                self.addstr(4,0,"\u25B7")

        self.addstr(6,0,self.e.desc)
        if self.field == 1:
            self.chgat(6+len(self.e.desc),0,1,curses.A_REVERSE|curses.color_pair(config.COLOR_FOCUS))

    def set_element(self,e):
        self.e = e

    def get_element(self):
        return self.e




