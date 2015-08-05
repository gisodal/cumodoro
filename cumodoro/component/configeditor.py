from cumodoro.component.window import Window
from cumodoro.component.frame import Frame
from cumodoro.component.input import Input
from cumodoro.component.taskeditor import Taskeditor
from cumodoro.component.sloteditor import Sloteditor
import cumodoro.globals as globals
import cumodoro.config as config
import curses
import types
import logging

log = logging.getLogger('cumodoro')

class Configeditor(Window):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.current_select = -1
        self.position = [0,0]
        self.prev_select = 0

    def set_position(self,x,y):
        self.position = [x,y]

    def init(self):
        x,y = self.position

        # tasks
        window = Window()
        window.name = "tasks"

        frame = Frame()
        frame.name = "tasks_frame"
        frame.set_size(10,1)
        frame.set_position(x,y)
        def update_patch(target):
            target.erase()
            options = None
            if target.selected:
                options = curses.A_BOLD
                if target.selected_title:
                    options = options | curses.color_pair(config.COLOR_FOCUS)
            target.addstr(0,0,"Tasks",options)
        frame.update = types.MethodType(update_patch,frame)
        window.add_frame(frame.name,frame)

        frame = Taskeditor()
        frame.name = "taskeditor_frame"
        frame.set_position(x,y+2)
        window.add_frame(frame.name,frame)
        window.input_frame = frame

        self.stack.append(window)
        self.add_frame(window.name,window)

        # pomodoro time
        window = Window()
        window.name = "pomodoro_time"

        x,y = self.position
        frame = Frame()
        frame.name = "pomodoro_time_frame"
        frame.set_size(10,1)
        frame.set_position(40,y)
        def update_patch(target):
            target.erase()
            options = None
            if target.selected:
                options = curses.A_BOLD
                if target.selected_title:
                    options = options | curses.color_pair(config.COLOR_FOCUS)
            target.addstr(0,0,"Pomodoro",options)
        frame.update = types.MethodType(update_patch,frame)
        window.add_frame("pomodoro_time_frame",frame)

        frame = Input()
        frame.name = "pomodoro_time_edit_frame"
        frame.init("time")
        frame.variable = "TIME_POMODORO"
        frame.value = config.TIME_POMODORO
        frame.set_position(40+14,y)
        window.add_frame("pomodoro_time_edit_frame",frame)
        window.input_frame = frame

        self.stack.append(window)
        self.add_frame(window.name,window)

        # break time
        window = Window()
        window.name = "break_time"

        frame = Frame()
        frame.name = "break_time_frame"
        frame.set_size(10,1)
        frame.set_position(40,y+1)
        def update_patch(target):
            target.erase()
            options = None
            if target.selected:
                options = curses.A_BOLD
                if target.selected_title:
                    options = options | curses.color_pair(config.COLOR_FOCUS)
            target.addstr(0,0,"Break",options)
        frame.update = types.MethodType(update_patch,frame)
        window.add_frame("break_time_frame",frame)

        frame = Input()
        frame.name = "break_time_edit_frame"
        frame.init("time")
        frame.variable = "TIME_BREAK"
        frame.value = config.TIME_BREAK
        frame.set_position(40+14,y+1)
        window.add_frame("break_time_edit_frame",frame)
        window.input_frame = frame

        self.stack.append(window)
        self.add_frame(window.name,window)

        # slots
        window = Window()
        window.name = "slot_time"

        frame = Frame()
        frame.name = "slot_frame"
        frame.variable = "TIME_SLOT"
        frame.set_size(10,1)
        frame.set_position(40,y+2)
        def update_patch(target):
            target.erase()
            options = None
            if target.selected:
                options = curses.A_BOLD
                if target.selected_title:
                    options = options | curses.color_pair(config.COLOR_FOCUS)
            target.addstr(0,0,"Slots",options)
        frame.update = types.MethodType(update_patch,frame)
        window.add_frame("slot_frame",frame)

        frame = Sloteditor()
        frame.name = "slot_edit_frame"
        frame.set_position(40+3,y+4)
        window.add_frame(frame.name,frame)
        window.input_frame = frame

        self.stack.append(window)
        self.add_frame(window.name,window)

        # initial state
        for w in self.stack:
            w.set_variable("selected",False)
            w.set_variable("selected_title",False)

        self.select(0)
        self.set_variable("selected_input",False)

    def update(self):
        super().update()

    def refresh(self):
        super().refresh()

    def select(self,n = None):
        if n == None:
            n = self.prev_select

        if n < len(self.stack):
            pn = self.current_select
            self.current_select = n
            if pn >= 0:
                self.stack[pn].set_variable("selected",False)
                self.stack[pn].set_variable("selected_title",False)

            if n >= 0:
                self.stack[n].set_variable("selected",True)
                self.stack[n].set_variable("selected_title",True)
                self.prev_select = n

    def create(self):
        for w in self.stack:
            w.create()

    def handle_input(self):
        mb = globals.messageboard
        window = self.stack[self.current_select]
        window.set_variable("selected_title",False)
        window.set_variable("selected_input",True)
        window.update()
        window.refresh()

        if window.name == "pomodoro_time":
            value = window.input_frame.value
            window.input_frame.handle_input()
            nvalue = window.input_frame.value
            if value != nvalue:
                config.TIME_BREAK = nvalue
                globals.database.update_config("TIME_POMODORO",nvalue)
                config.init()
        elif window.name == "break_time":
            value = window.input_frame.value
            window.input_frame.handle_input()
            nvalue = window.input_frame.value
            if value != nvalue:
                config.TIME_BREAK = nvalue
                globals.database.update_config("TIME_BREAK",nvalue)
                config.init()
        else:
            window.input_frame.handle_input()

        window.set_variable("selected_title",True)
        window.set_variable("selected_input",False)
        window.update()
        window.refresh()

    def down(self):
        s = self.current_select + 1
        if s != 1 and s < 4:
            self.select(s)

    def up(self):
        s = self.current_select - 1
        if s > 0 or s >= 1:
            self.select(s)

    def left(self):
        if self.current_select > 0:
            self.select(0)

    def right(self):
        if self.current_select == 0:
            self.select(1)


