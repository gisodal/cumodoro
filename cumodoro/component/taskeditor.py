from cumodoro.component.frame import Frame
import cumodoro.database as database
import cumodoro.globals as globals
import cumodoro.config as config
from copy import copy, deepcopy
from cumodoro.component.taskcreator import Taskcreator
from cumodoro.component.element import Element
import curses
import sys
import logging
from cumodoro.dynamiclist import Dynamiclist
log = logging.getLogger('cumodoro')

class Taskeditor(Frame):
    def __init__(self):
        super().__init__()
        self.size = [35,globals.Y-self.position[1]-1]
        self.selected_input = False
        self.entries = 0
        self.tasks = None
        self.current = Dynamiclist(-1)
        self.state = None
        self.modified = True
        self.prev_tasks = None
        self.delete_list = []

    def create(self):
        self.size = [35,globals.Y-self.position[1]-1]
        super().create()

    def reload_rec(self,tasks,E):
        task_list = globals.database.full_task_list
        task_data = globals.database.tasks
        for i in range(0,len(tasks)):
            T = task_data[tasks[i]]
            e = Element()
            e.idx = T.idx
            e.desc = T.desc
            e.color = T.color
            e.active = T.active
            e.task = T.task

            E.append(e)
            self.entries += 1

            if tasks[i] in task_list:
                self.reload_rec(task_list[e.idx],e.tasks)

    def reload(self):
        if self.modified:
            self.modified = False
            if self.prev_tasks == None:
                self.entries = 0
                self.tasks = []

                if list(globals.database.full_task_list) and len(globals.database.full_task_list[None]) > 0:
                    self.reload_rec(globals.database.full_task_list[None],self.tasks)
                    self.current[0] = 0
                else:
                    self.current = Dynamiclist(0)

                self.prev_entries = self.entries
                self.prev_tasks = deepcopy(self.tasks)
            else:
                del self.tasks
                self.tasks = deepcopy(self.prev_tasks)
                self.entries = self.prev_entries
                self.delete_list = []

    def reset_current(self):
        if self.tasks != None and len(self.tasks) > 0:
            self.current = Dynamiclist(0)
            self.current[0] = 0

    def sync_rec(self,tasks):
        for i in range(len(tasks)):
            if tasks[i].modified:
                tasks[i].modified = False
                log.debug("sync update task '"+str(tasks[i].idx)+": "+tasks[i].desc)
                globals.database.store_task(tasks[i])
            self.sync_rec(tasks[i].tasks)

    def sync(self):
        if self.modified:
            self.modified = False
            for i in range(len(self.delete_list)):
                globals.database.delete_task(self.delete_list[i].idx)
            del self.delete_list
            self.delete_list = []

            self.sync_rec(self.tasks)
            globals.database.load_tasks()
            globals.interface.windows["Timer"].frames["taskswitcher_frame"].reset()
            globals.interface.windows["Weekview"].frames["weekswitcher_frame"].reset()
            globals.interface.windows["Weekview"].frames["weekview_frame"].reload()

    def insert(self):
        if len(self.current) > 0:
            self.state = "insert"

    def move(self):
        if len(self.current) > 0:
            self.state = "move"

    def edit(self):
        if len(self.current) > 0:
            self.state = "edit"

    def delete(self):
        if len(self.current) > 0:
            self.modified = True

            l = self.tasks
            for level in range(len(self.current)-1):
                i = self.current[level]
                task = l[i].idx
                l = l[i].tasks

            i = self.current[-1]
            self.delete_list.append(l[i])
            del l[i]

            if i > 0:
                if i == len(l):
                    self.current[-1] -= 1
            elif len(l) == 0:
                    self.current.pop()

            self.modified = True

    def active(self):
        l = self.tasks
        for level in range(len(self.current)-1):
            i = self.current[level]
            l = l[i].tasks

        i = self.current[-1]
        l[i].active = not l[i].active
        l[i].modified = True
        self.modified = True

    def handle_input(self):
        interface = globals.interface
        screen = interface.screen
        mb = globals.messageboard

        self.prev_tasks = deepcopy(self.tasks)
        self.prev_entries = self.entries
        self.reset_current()
        mb.message("[ENTER]: Save, [ESC]: Cancel, [e]: Edit, [m]: Move, [i]: Insert, [d]: Delete, [t]: Toggle")
        while True:
            self.update()
            self.refresh()
            key = screen.getkey()
            if interface.resize(key):
                pass
            elif key == "i":
                self.insert()
                self.update()
                self.refresh()

                taskcreator = Taskcreator()
                taskcreator.set_position(*self.position)
                taskcreator.create()
                taskcreator.update()
                taskcreator.refresh()
                mb.message("[ENTER]: Save, [ESC]: Cancel")
                taskcreator.handle_input()
                e = taskcreator.get_element()
                del taskcreator

                if e != None:
                    if len(self.tasks) > 0:
                        self.tasks.insert(0,e)
                    else:
                        self.tasks = [e]
                    self.reset_current()
                    self.modified = True

                self.state = None
                self.update()
                self.refresh()
                mb.pop()
            elif len(key) == 1 and ord(key) == 27:
                if self.state == None:
                    self.reload()
                    self.update()
                    self.refresh()
                    break
                elif self.state == "move":
                    self.state = None
                    self.tasks = self.move_data
                    self.current = self.move_current
                    self.update()
                    self.refresh()
                    mb.pop()
            elif len(key) == 1 and ord(key) == 13:
                if self.state == None:
                    break
                else:
                    mb.pop()
                    self.state = None
            elif key == 'q':
                    sys.exit(0)
            elif len(self.tasks) > 0:
                if key == "KEY_RIGHT" or key == "l":
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
                    self.delete()
                    self.update()
                    self.refresh()
                elif key == "t":
                    self.active()
                    self.update()
                    self.refresh()
                elif key == "e":
                    self.edit()
                    self.update()
                    self.refresh()

                    taskcreator = Taskcreator()
                    taskcreator.set_position(*self.position)
                    taskcreator.create()
                    e = self.get_element()
                    color = e.color
                    desc = e.desc
                    taskcreator.set_element(e)
                    taskcreator.update()
                    taskcreator.refresh()
                    mb.message("[ENTER]: Save, [ESC]: Cancel")
                    taskcreator.handle_input()
                    e = taskcreator.get_element()
                    del taskcreator

                    if e != None:
                        if e.modified:
                            self.modified = True
                    else:
                        e = self.get_element()
                        e.color = color
                        e.desc = desc

                    self.state = None
                    self.update()
                    self.refresh()
                    mb.pop()
                elif key == "m":
                    self.move()
                    self.move_data = deepcopy(self.tasks)
                    self.move_current = deepcopy(self.current)
                    self.update()
                    self.refresh()
                    mb.message("[ENTER]: Save, [ESC]: Cancel")
            else:
                log.debug("unregistered key: '"+str(key)+"'")

        mb.pop()
        self.sync()

    def get_element(self):
        if self.current != None and len(self.current) > 0:
            l = self.tasks
            for level in range(len(self.current)-1):
                i = self.current[level]
                l = l[i].tasks

            i = self.current[-1]
            return l[i]
        else:
            return None

    def right(self):
        if len(self.current) > 0:
            l = self.tasks
            for level in range(len(self.current)):
                i = self.current[level]
                l = l[i].tasks

            if self.state == "move":
                if self.current[-1] > 0:
                    l = self.tasks
                    for level in range(len(self.current)-1):
                        i = self.current[level]
                        l = l[i].tasks

                    i1 = self.current[-1]
                    i2 = i1 -1
                    l[i1].modified = True
                    self.modified = True
                    l[i1].task = l[i2].idx
                    l[i2].tasks.append(l[i1])

                    del l[i1]
                    self.current[-1] -= 1
                    self.current.append(len(l[i2].tasks)-1)

            elif len(l) > 0:
                self.current.append(0)


    def left(self):
        if len(self.current) > 1:
            if self.state == "move":
                task = None
                l = self.tasks
                for level in range(len(self.current)-2):
                    i = self.current[level]
                    task = l[i].idx
                    l = l[i].tasks

                i1,i2 = self.current[-2:]
                l[i1].tasks[i2].modified = True
                l[i1].tasks[i2].task = task
                self.modified = True
                if len(l) < i1+1:
                    l.append(l[i1].tasks[i2])
                else:
                    l.insert(i1+1,l[i1].tasks[i2])

                del l[i1].tasks[i2]
                self.current[-2] += 1

            self.current.pop()

    def up(self):
        if self.current != None and len(self.current) > 0 and self.current[-1] > 0:
            if self.state == "move":
                l = self.tasks
                for level in range(len(self.current)-1):
                    i = self.current[level]
                    l = l[i].tasks

                i1 = self.current[-1]
                i2 = i1 -1
                e = l[i1]
                l[i1] = l[i2]
                l[i2] = e

            self.current[-1] -= 1

    def down(self):
        if len(self.current) > 0:
            l = self.tasks
            for level in range(len(self.current)-1):
                i = self.current[level]
                l = l[i].tasks

            if self.current[-1] < len(l)-1:
                if self.state == "move":
                    l = self.tasks
                    for level in range(len(self.current)-1):
                        i = self.current[level]
                        l = l[i].tasks

                    i1 = self.current[-1]
                    i2 = i1 +1
                    e = l[i1]
                    l[i1] = l[i2]
                    l[i2] = e

                self.current[-1] += 1

    def update_rec(self, tasks, current, row = [0], vline = set(), blank = [False], level = 0, active = True):
        offset = 0
        if self.state == "edit" or self.state == "insert":
            offset = 2

        for i in range(0,len(tasks)):
            level_width = 2
            offset2 = 5
            current[level] = i
            e = tasks[i]

            if blank[0]:
                blank[0] = False
                for x in vline:
                    self.addstr(x,offset+row[0],'\u2502')
                row[0] += 1

            if i < len(tasks)-1:
                vline.add(level*level_width)
            else:
                try:
                    vline.remove(level*level_width)
                except: pass

            for x in vline:
                self.addstr(x,offset+row[0],'\u2502')

            if len(e.tasks) > 0:
                self.addstr(level_width*level+1,offset+row[0],'\u2500\u252C')
            else:
                self.addstr(level_width*level+1,offset+row[0],'\u2500'*2)

            if i < len(tasks)-1:
                self.addstr(level_width*level,offset+row[0],'\u251C')
            else:
                self.addstr(level_width*level,offset+row[0],'\u2514')

            self.addstr(level_width*level+3,offset+row[0],'\u25CF',curses.color_pair(e.color))
            if self.selected_input and self.current == current and self.state != "insert":
                if self.state == "move":
                    self.addstr(level_width*level+offset2,offset+row[0],e.desc,curses.A_BOLD|curses.color_pair(1))
                elif self.state == "edit":
                    self.addstr(level_width*level+offset2,offset+row[0],e.desc,curses.A_BOLD)
                else:
                    self.addstr(level_width*level+offset2,offset+row[0],e.desc,curses.A_BOLD|curses.color_pair(config.COLOR_FOCUS))
            else:
                if active and e.active:
                    self.addstr(level_width*level+offset2,offset+row[0],e.desc)
                else:
                    self.addstr(level_width*level+offset2,offset+row[0],e.desc,curses.color_pair(240))
            row[0] += 1

            if not active or not e.active:
                self.update_rec(e.tasks,current,row,vline,blank,level+1,False)
            else:
                self.update_rec(e.tasks,current,row,vline,blank,level+1,True)

            current.pop()

        if len(tasks) > 0:
            blank[0] = True

    def update(self):
        self.erase()
        if self.tasks == None:
            self.reload()

        self.update_rec(self.tasks,Dynamiclist(0),[0,0],set(),[False])

