import curses
from cumodoro.component.frame import Frame
import cumodoro.globals as globals

class Banner(Frame):
    def __init__(self):
        super(Banner,self).__init__()
        self.focus = True
        self.set_position(0,0)
        self.set_size(81,2)
        self.window_list = []
        self.window_map = {}
        self.current_window = None
        self.SIZE = 81
        self.screen = globals.interface.screen

    def update(self):
        self.erase()
        for i,w in enumerate(self.window_list):
            offset = int((self.widthpc - len(w))/2)
            self.addstr(i*self.widthpc+offset,0,w)
            self.chgat(i*self.widthpc+offset,0,1,curses.A_BOLD|curses.A_UNDERLINE)
            if i == self.current_window:
                self.chgat(i*self.widthpc+2,0,self.widthpc-4,curses.A_BOLD)
                self.addstr(i*self.widthpc+2+1,1,"\u25A0"*(self.widthpc-4-2))
                self.addstr(i*self.widthpc+2,1,"\u25D6")
                self.addstr(i*self.widthpc+2+self.widthpc-4-1,1,"\u25D7")

    def create(self):
        X = globals.X
        Y = globals.Y
        if X >= self.SIZE:
            self.size = X+2,2
        super(Banner,self).create()

    def set_window_list(self, l):
        self.window_list = l
        self.window_map = { w:i for i,w in enumerate(self.window_list) }
        self.widthpc = int((self.SIZE-1) / len(self.window_list))
        self.width = self.widthpc * len(self.window_list)

    def select(self,window_name):
        self.current_window = self.window_map[window_name]
