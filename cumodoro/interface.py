#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import datetime
import curses
import sys
import types
from cumodoro.timeconvert import *
import cumodoro.config as config
import cumodoro.globals as globals
from .component.timer import Timer
from .component.weekview import Weekview
from .component.taskswitcher import Taskswitcher
from .component.window import Window
from .component.message import Messageboard
from .component.clock import Clock
from .component.banner import Banner
from .component.overtime import Overtime
from .component.weekswitcher import Weekswitcher
from .component.weeklegend import Weeklegend
from .component.configeditor import Configeditor
from .component.frame import Frame
import threading
import logging

log = logging.getLogger('cumodoro')

class Interface:
    def __init__(self, stdscr):
        self.screen = stdscr
        globals.Y,globals.X = self.screen.getmaxyx()
        X,Y = globals.X,globals.Y
        globals.interface = self
        globals.database.load_config()
        config.init()
        globals.messageboard = Messageboard()
        mb = globals.messageboard
        mb.create()

        self.width = 81

        self.size = [ X, Y ]
        if self.size[0] < 81:
            self.size[0] = 81

        self.switch_window = None
        self.windows = { "Timer":Window(),"Weekview":Window(),"Settings":Window() }
        self.window_list = [ "Timer", "Weekview", "Settings" ]

        # create banner
        self.banner = Banner()
        self.banner.name = "Banner"
        self.banner.create()
        self.banner.set_focus(True)
        self.banner.set_window_list(self.window_list)

        # build setting window
        window = self.windows["Settings"]
        window.name = "Settings"

        frame = Configeditor()
        frame.name = "config_frame"
        frame.set_position(4,4)
        frame.init()
        window.add_frame(frame.name,frame)

        mb.message("[ENTER]: Edit",window.name)
        window.add_frame(mb.name,mb)

        window.create()
        self.patch_settings(window)

        # build weekview window
        window = self.windows["Weekview"]
        window.name = "Weekview"

        frame = Weekswitcher()
        frame.name = "weekswitcher_frame"
        frame.set_position(32,4)
        window.add_frame(frame.name,frame)

        frame = Weekview()
        frame.name = "weekview_frame"
        frame.set_size(80,9)
        frame.set_position(4,10)
        frame.reload()
        window.add_frame(frame.name,frame)

        frame = Weeklegend()
        frame.name = "weeklegend_frame"
        frame.set_size(80,10)
        frame.set_position(6,21)
        window.add_frame(frame.name,frame)

        frame = Taskswitcher()
        frame.name = "taskswitcher_frame"
        frame.set_position(5,21)
        frame.set_manual_focus(False)
        frame.disable()
        window.add_frame(frame.name,frame)

        mb.message("[ENTER]: Edit",window.name)
        window.add_frame(mb.name,mb)

        window.create()
        self.patch_weekview(window)

        # build Timer window
        window = self.windows["Timer"]
        window.name = "Timer"

        frame = Taskswitcher()
        frame.name = "taskswitcher_frame"
        x = int((self.width - frame.size[0]) / 2)
        frame.set_position(x,14)
        window.add_frame(frame.name,frame)

        frame = Overtime()
        frame.name = "overtime_frame"
        frame.set_position(x,6+5)
        window.add_frame(frame.name,frame)

        frame = Timer()
        frame.name = "timer_frame"
        frame.set_position(x,6)
        window.add_frame(frame.name,frame)

        frame = Frame()
        frame.name = "color_frame"
        frame.set_size(36,1)
        frame.set_position(x,4)
        def update_patch(target):
            taskswitcher = globals.interface.windows["Timer"].frames["taskswitcher_frame"]
            target.erase()
            width = 14
            start = int((target.size[0] - width) / 2)-1
            target.addstr(start,0,"\u25D6")
            target.addstr(start+width-1,0,"\u25D7")
            target.addstr(start+1,0,"\u25A0"*(width-2),curses.color_pair(taskswitcher.get_color()))
        frame.update = types.MethodType(update_patch,frame)
        window.add_frame(frame.name,frame)

        mb.message("[SPACE]: Start, [ENTER]: Edit, [b]: Break",window.name)
        window.add_frame(mb.name,mb)

        frame = Clock()
        frame.name = "clock_frame"
        frame.set_position(x+29,11)
        window.add_frame(frame.name,frame)

        window.create()

        clockthread = threading.Thread(target=frame.run,name="Clock")
        clockthread.setDaemon(True)
        clockthread.start()

        self.patch_timer(window)

    def resize(self,key):
        if key == "KEY_RESIZE":
            globals.Y,globals.X = self.screen.getmaxyx()
            self.size = [globals.X+1,globals.Y]
            self.destroy()
            self.create()
            self.banner.set_focus(True)
            window = self.get_window()
            window.set_focus(True)
            self.screen.erase()
            self.screen.refresh()
            self.banner.update()
            self.banner.refresh()
            mb = globals.messageboard
            mb.destroy()
            mb.create()
            window.update()
            window.refresh()
            mb.update()
            mb.refresh()
            return True

        return False

    def destroy(self):
        self.banner.destroy()

        for window_name,window in self.windows.items():
            window.destroy()

    def create(self):
        X = globals.X
        Y = globals.Y
        self.size = [ X , Y ]
        self.banner.create()

        for window_name,window in self.windows.items():
            window.create()

    def select_window(self,window_name):
        self.current_window = window_name
        self.banner.select(self.current_window)
        self.get_window().set_focus(True)

    def is_number(self,s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def alert(self):
        def run(self):
            X = globals.X
            Y = globals.Y
            frame = Frame()
            frame.set_focus(True)
            frame.set_size(X+1,Y)
            frame.set_position(0,0)
            frame.create()
            def update_patch(target):
                for y in range(Y):
                    frame.addstr(0,y,' '*X,curses.A_REVERSE)
            frame.update = types.MethodType(update_patch,frame)

            timer = self.windows["Timer"].frames["timer_frame"]
            for i in range(3):
                frame.update()
                frame.refresh()
                time.sleep(0.2)
                self.screen.erase()
                self.screen.refresh()
                window = self.get_window()
                timer.update()
                window.update()
                window.refresh()
                self.banner.update()
                self.banner.refresh()
                time.sleep(0.2)

            del frame

        thread = threading.Thread(target=run,name="alert",args = (self,))
        thread.setDaemon(True)
        thread.start()

    def switch_focus(self,key):
        if self.current_window != "Timer" and (key == 'T' or key == 't'):
            log.debug("switching to window 'Timer'")
            self.switch_window = "Timer"
            return True
        elif self.current_window != "Weekview" and (key == 'W' or key == 'w'):
            log.debug("switching to window 'Weekview'")
            self.switch_window = "Weekview"
            return True
        elif self.current_window != "Settings" and (key == 'S' or key == 's'):
            log.debug("switching to window 'Settings'")
            self.switch_window = "Settings"
            return True
        return False

    def patch_settings(self,target):
        def handle_input(target):
            interface = globals.interface
            window = interface.get_window()
            conf = window.frames["config_frame"]
            screen = interface.screen
            timer = interface.windows["Timer"].frames["timer_frame"]
            mb = globals.messageboard

            if timer.get_phase() == 0:
                conf.select()
            else:
                conf.select(-1)

            window.update()
            window.refresh()
            while True:
                key = screen.getkey()
                if interface.switch_focus(key):
                    break
                elif interface.resize(key):
                    pass
                elif key == 'q':
                    sys.exit(0)
                elif timer.get_phase() == 0:
                    if key == "KEY_RIGHT" or key == "l":
                        conf.right()
                        conf.update()
                        conf.refresh()
                    elif key == "KEY_LEFT" or key == "h":
                        conf.left()
                        conf.update()
                        conf.refresh()
                    elif key == "KEY_UP" or key == "k":
                        conf.up()
                        conf.update()
                        conf.refresh()
                    elif key == "KEY_DOWN" or key == "j":
                        conf.down()
                        conf.update()
                        conf.refresh()
                    elif len(key) == 1 and ord(key) == 13:
                        conf.handle_input()
                    else:
                        log.debug("unregistered key: '"+str(key)+"'")
                else:
                    log.debug("unregistered key: '"+str(key)+"'")

        target.handle_input = types.MethodType(handle_input,target)

    def patch_weekview(self,target):
        def handle_input(target):
            interface = globals.interface
            window = interface.get_window()
            screen = interface.screen
            weekswitcher = window.frames["weekswitcher_frame"]
            weekview = window.frames["weekview_frame"]
            weeklegend = window.frames["weeklegend_frame"]
            taskswitcher = window.frames["taskswitcher_frame"]
            database = globals.database
            timer = interface.windows["Timer"].frames["timer_frame"]
            mb = globals.messageboard

            while True:
                key = screen.getkey()

                if interface.resize(key):
                    pass
                elif key == 'q':
                    sys.exit(0)
                elif weekview.edit == 0:
                    if interface.switch_focus(key):
                        break
                    elif key == "KEY_RIGHT" or key == "l":
                        weekswitcher.right()
                        weekswitcher.update()
                        weekswitcher.refresh()
                        weekview.reload()
                        weekview.update()
                        weekview.refresh()
                        weeklegend.update()
                        weeklegend.refresh()
                    elif key == "KEY_LEFT" or key == "h":
                        weekswitcher.left()
                        weekswitcher.update()
                        weekswitcher.refresh()
                        weekview.reload()
                        weekview.update()
                        weekview.refresh()
                        weeklegend.update()
                        weeklegend.refresh()
                    elif key == "KEY_UP" or key == "k":
                        weekswitcher.up()
                        weekswitcher.update()
                        weekswitcher.refresh()
                    elif key == "KEY_DOWN" or key == "j":
                        weekswitcher.down()
                        weekswitcher.update()
                        weekswitcher.refresh()
                    elif len(key) == 1 and ord(key) == 13:
                        if timer.get_phase() == 0:
                            database.savepoint()
                            weekview.set_edit(1)
                            weekview.update_edit()
                            weekview.refresh()
                            weekswitcher.disable()
                            weekswitcher.update()
                            weekswitcher.refresh()
                            weeklegend.erase()
                            weeklegend.refresh()
                            weeklegend.set_manual_focus(False)
                            taskswitcher.set_manual_focus(True)
                            taskswitcher.set_task(weekview.get_task())
                            taskswitcher.disable()
                            taskswitcher.update()
                            taskswitcher.refresh()
                            mb.message("[ENTER]: Save, [ESC]: Cancel, [e]: Edit, [d]: Delete")
                        else:
                            mb.alert("Cannot edit while timer is running..")
                    else:
                        log.debug("unregistered key: '"+str(key)+"'")

                elif weekview.edit == 1:
                    if key == "KEY_RIGHT" or key == "l":
                        weekview.right()
                        weekview.update()
                        weekview.refresh()
                        taskswitcher.set_task(weekview.get_task())
                        taskswitcher.disable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                    elif key == "KEY_LEFT" or key == "h":
                        weekview.left()
                        weekview.update()
                        weekview.refresh()
                        taskswitcher.set_task(weekview.get_task())
                        taskswitcher.disable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                    elif key == "KEY_UP" or key == "k":
                        weekview.up()
                        weekview.update()
                        weekview.refresh()
                        taskswitcher.set_task(weekview.get_task())
                        taskswitcher.disable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                    elif key == "KEY_DOWN" or key == "j":
                        weekview.down()
                        weekview.update()
                        weekview.refresh()
                        taskswitcher.set_task(weekview.get_task())
                        taskswitcher.disable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                    elif key == "e":
                        weekview.set_edit(2)
                        t = weekview.get_task()
                        taskswitcher.enable()
                        taskswitcher.set_task(t)
                        taskswitcher.update()
                        taskswitcher.refresh()
                        weekview.set_task(taskswitcher.get_task())
                        weekview.update()
                        weekview.update_edit()
                        weekview.refresh()
                        mb.message("[ENTER]: Save, [ESC]: Cancel")
                    elif len(key) == 1 and ( ord(key) == 27 or ord(key) == 13 ):
                        if ord(key) == 27:
                            database.rollback()
                            weekview.empty_backorder()
                        else:
                            weekview.flush_backorder()
                        database.release()
                        database.commit()
                        taskswitcher.erase()
                        taskswitcher.refresh()
                        taskswitcher.set_manual_focus(False)
                        weekview.set_edit(0)
                        weekview.reload()
                        weekview.update()
                        weekview.refresh()
                        weekswitcher.enable()
                        weekswitcher.update()
                        weekswitcher.refresh()
                        weeklegend.set_manual_focus(True)
                        weeklegend.update()
                        weeklegend.refresh()
                        mb.pop()
                    elif key == 'd':
                        weekview.delete_task()
                        weekview.update()
                        weekview.refresh()
                        taskswitcher.set_task(weekview.get_task())
                        taskswitcher.disable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                        mb.refresh()
                    else:
                        log.debug("unregistered key: '"+str(key)+"'")

                elif weekview.edit == 2:
                    if key == "KEY_RIGHT" or key == "l":
                        taskswitcher.right()
                        taskswitcher.update()
                        taskswitcher.refresh()
                        weekview.set_task(taskswitcher.get_task())
                        weekview.update()
                        weekview.refresh()
                    elif key == "KEY_LEFT" or key == "h":
                        taskswitcher.left()
                        taskswitcher.update()
                        taskswitcher.refresh()
                        weekview.set_task(taskswitcher.get_task())
                        weekview.update()
                        weekview.refresh()
                    elif key == "KEY_UP" or key == "k":
                        taskswitcher.up()
                        taskswitcher.update()
                        taskswitcher.refresh()
                    elif key == "KEY_DOWN" or key == "j":
                        taskswitcher.down()
                        taskswitcher.update()
                        taskswitcher.refresh()
                    elif len(key) == 1 and ord(key) == 13:
                        taskswitcher.disable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                        weekview.update_database()
                        weekview.set_edit(1)
                        weekview.update()
                        weekview.update_edit()
                        weekview.refresh()
                        mb.pop()
                    elif len(key) == 1 and ord(key) == 27:
                        weekview.cancel()
                        weekview.set_edit(1)
                        weekview.update()
                        weekview.refresh()
                        taskswitcher.set_task(weekview.get_task())
                        taskswitcher.disable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                        mb.pop()
                    else:
                        log.debug("unregistered key: '"+str(key)+"'")

        target.handle_input = types.MethodType(handle_input,target)

    def patch_timer(self,target):
        def handle_input(target):
            interface = globals.interface
            window = interface.get_window()
            screen = interface.screen
            timer = window.frames["timer_frame"]
            color = window.frames["color_frame"]
            taskswitcher = window.frames["taskswitcher_frame"]
            weekview = interface.windows["Weekview"].frames["weekview_frame"]
            mb = globals.messageboard

            while True:
                key = screen.getkey()
                if interface.switch_focus(key):
                    break
                elif interface.resize(key):
                    pass
                elif key == 'q':
                    sys.exit(0)
                elif key == 'f':
                    self.alert()
                elif timer.edit_timer:
                    if self.is_number(key):
                        timer.edit_time(int(key))
                    elif len(key) == 1 and ord(key) == 27:
                        timer.edit_cancel()
                    elif len(key) == 1 and ord(key) == 13:
                        timer.edit_next()

                    if not timer.edit_timer:
                        mb.pop()

                    timer.update()
                    timer.refresh()
                    taskswitcher.update()
                    taskswitcher.refresh()
                elif timer.get_phase() == 2:
                    if key == ' ':
                        mb.pop()
                        timer.shift()
                        taskswitcher.enable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                    elif len(key) == 1 and ord(key) == 13:
                        overtime = timer.overtime.current_time
                        if timer.current_time == 0:
                            timer.current_time = config.TIME_POMODORO_SEC

                        timertime = timer.current_time
                        if overtime > timertime:
                            timer.current_time = 0
                            timer.overtime.current_time = overtime - timertime
                            globals.database.add_pomodoro_now(taskswitcher.get_task())
                            weekview.reload()
                            weekview.update_week()
                            weekview.refresh()
                        else:
                            timer.current_time = timertime - overtime
                            timer.overtime.current_time = 0
                            timer.shift()
                            mb.pop()
                            timer.shift()
                            mb.message("[SPACE]: Stop, [b]: Break")

                        timer.overtime.update()
                        timer.overtime.refresh()
                        timer.update()
                        timer.refresh()
                elif timer.get_phase() == 1:
                    if key == ' ':
                        mb.pop()
                        timer.shift()
                        timer.update()
                        timer.refresh()
                        taskswitcher.enable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                    elif key == "b":
                        mb.pop()
                        mb.message("[SPACE]: Stop/Reset, [ENTER]: Deduct break time")
                        timer.start_overtime()
                elif timer.get_phase() == 0:
                    if key == "b":
                        mb.message("[SPACE]: Stop/Reset, [ENTER]: Deduct break time")
                        taskswitcher.disable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                        timer.start_overtime()
                    elif key == "KEY_RIGHT" or key == "l":
                        taskswitcher.right()
                        taskswitcher.update()
                        taskswitcher.refresh()
                        color.update()
                        color.refresh()
                    elif key == "KEY_LEFT" or key == "h":
                        taskswitcher.left()
                        taskswitcher.update()
                        taskswitcher.refresh()
                        color.update()
                        color.refresh()
                    elif key == "KEY_UP" or key == "k":
                        taskswitcher.up()
                        taskswitcher.update()
                        taskswitcher.refresh()
                        color.update()
                        color.refresh()
                    elif key == "KEY_DOWN" or key == "j":
                        taskswitcher.down()
                        taskswitcher.update()
                        taskswitcher.refresh()
                        color.update()
                        color.refresh()
                    elif len(key) == 1 and ord(key) == 13:
                        mb.message("[ENTER]: Next, [ESC]: Cancel")
                        timer.edit_enable()
                        timer.update()
                        timer.refresh()
                        taskswitcher.disable()
                        taskswitcher.update()
                        taskswitcher.refresh()
                    elif key == ' ':
                        timer.shift()
                        if timer.get_running():
                            mb.message("[SPACE]: Stop, [b]: Break")
                            taskswitcher.disable()
                            taskswitcher.update()
                            taskswitcher.refresh()
                    else:
                        log.debug("unregistered key: '"+str(key)+"'")
                else:
                    log.debug("unregistered key: '"+str(key)+"'")

        target.handle_input = types.MethodType(handle_input,target)

    def get_window(self, index = None):
        if index == None:
            try:
                return self.windows[self.current_window]
            except:
                return None

        return self.windows[index]

    def main(self):
        self.create()
        self.select_window("Timer")
        self.screen.notimeout(0)
        screen = self.screen
        screen.refresh()
        banner = self.banner


        window = self.get_window()
        while True:
            window.update()
            window.refresh()
            banner.update()
            banner.refresh()
            window.handle_input()
            if self.switch_window != None:
                window.set_focus(False)
                self.current_window = self.switch_window
                self.switch_window = None
                window = self.get_window()
                window.set_focus(True)
                screen.erase()
                window.update()
                banner.select(window.name)
                screen.refresh()




def main(stdscr):
    curses.curs_set(False) # make cursor invisble
    curses.use_default_colors()
    curses.nonl()
    config.init_all_color_pairs()

    interface = Interface(stdscr)
    interface.main()

