from cumodoro.component.frame import Frame
import cumodoro.globals as globals
import cumodoro.config as config
import curses
import sys
import logging
import types
from cumodoro.timeconvert import *
log = logging.getLogger('cumodoro')

class Input(Frame):
    def __init__(self):
        super().__init__()
        self.input_type = ""
        self.selected = False
        self.variable = ''
        self.selected_input = False

    def init(self,t):
        option = str(t)
        if option == "time":
            self.input_type = option
            self.init_time()
        elif option == "text":
            self.input_type = option
            self.init_text()
        else:
            log.error("unknown input initialisation")

    def is_number(self,s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def init_text(self):
        self.set_size(20,1)
        self.value = None
        def update_patch(target):
            target.erase()
            target.addstr(0,0,target.value)
            if target.selected_input:
                target.chgat(len(target.value),0,1,curses.color_pair(config.COLOR_TOTAL+config.COLOR_FOCUS))

        def handle_input_patch(target):
            interface = globals.interface
            screen = interface.screen
            old_value = self.value
            mb = globals.messageboard

            mb.message("[ENTER]: Next, [ESC]: Cancel")
            while True:
                target.update()
                target.refresh()
                key = screen.getkey()
                if interface.resize(key):
                    pass
                elif key == 'q':
                    sys.exit(0)
                elif len(key) == 1 and ord(key) == 27:
                    target.current = 0
                    target.value = old_value
                    break
                elif len(key) == 1 and ord(key) == 13:
                    if len(target.value) == 0:
                        target.current = 0
                        target.value = old_value
                        globals.messageboard.alert("Cannot store empty value")
                    break
                elif len(key) == 1 and ord(key) == 127:
                    if len(target.value) > 0:
                        self.value = self.value[0:-1]
                elif len(key) == 1 and (
                    ( ord(key) >= ord('a') and ord(key) <= ord('z') ) or
                    ( ord(key) >= ord('A') and ord(key) <= ord('Z') ) ):
                    if len(target.value) < self.size[0] - 2:
                        self.value += key
                else:
                    log.debug("unregistered key: '"+str(key)+"'")

            mb.pop()

        self.update = types.MethodType(update_patch,self)
        self.handle_input = types.MethodType(handle_input_patch,self)

    def init_time(self):
        self.set_size(10,1)
        self.current = 0
        self.value = None
        self.pos = [0,1,3,4,6,7]
        def update_patch(target):
            target.addstr(0,0,target.value)
            if target.selected_input:
                target.chgat(target.pos[target.current],0,1,curses.color_pair(config.COLOR_TOTAL+config.COLOR_FOCUS))

        def handle_input_patch(target):
            interface = globals.interface
            screen = interface.screen
            old_value = self.value
            mb = globals.messageboard

            mb.message("[ENTER]: Next, [ESC]: Cancel")
            while True:
                target.update()
                target.refresh()
                key = screen.getkey()
                if interface.resize(key):
                    pass
                elif key == 'q':
                    sys.exit(0)
                elif len(key) == 1 and ord(key) == 27:
                    target.current = 0
                    target.value = old_value
                    break
                elif len(key) == 1 and ord(key) == 13:
                    if target.current < len(target.pos):
                        target.current += 1
                        if target.current >= len(target.pos):
                            target.current = 0
                            break
                elif target.is_number(key):
                    c = target.current
                    n = int(key)
                    if not ( (c == 0 and n > 2)
                        or ((c == 2 or c == 4) and n > 5)
                        or (c == 1 and int(self.value[0:1]+key) >= 24)):
                        if target.current < len(target.pos):
                            t = list(target.value)
                            t[target.pos[target.current]] = key
                            target.value = "".join(t)
                            target.current += 1
                            if target.current >= len(target.pos):
                                target.current = 0
                                break
                else:
                    log.debug("unregistered key: '"+str(key)+"'")

            mb.pop()

        self.update = types.MethodType(update_patch,self)
        self.handle_input = types.MethodType(handle_input_patch,self)

    def handle_input(self):
        pass

