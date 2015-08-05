import sqlite3 as sql
import cumodoro.config as config
from cumodoro.error import DatabaseError
from collections import deque
import datetime
import sys
import logging

log = logging.getLogger('cumodoro')

class Task():
    pass

class Database():
    def __init__(self):
        self.db = None
        self.cursor = None
        self.tasks = None
        self.full_task_list = {}
        self.task_list = {}
        self.task_chain = {None:[]}
        self.has_savepoint = False

    def connect(self):
        if self.db == None:
            try:
                self.db = sql.connect(config.DATABASE, detect_types=sql.PARSE_DECLTYPES|sql.PARSE_COLNAMES, check_same_thread=False)
                self.db.isolation_level = None
                self.cursor = self.db.cursor()
                self.has_savepoint = False
            except sql.Error as e:
                print("Error:",e)
                sys.exit(1)

    def disconnect(self):
        if self.db != None:
            try:
                self.db.close()
                self.db = None
                self.cursor = None
            except sql.Error as e:
                print("Error:",e)
                sys.exit(1)

    def commit(self):
        try:
            if self.has_savepoint:
                raise DatabaseError("Savepoint not released")
            self.db.commit()
        except sql.Error as e:
            print("Error:",e)
            sys.exit(1)

    def execute(self,query,params = None,immediate=True):
        if self.db == None:
            self.connect()

        if isinstance(query,str) and ( params == None or isinstance(params,tuple) ):
            if isinstance(params,tuple):
                self.cursor.execute(query,params)
            else:
                self.cursor.execute(query)

            if immediate:
                self.commit()
        else:
            raise DatabaseError("parameter missmatch: string != "+str(type(query)))

    def request(self,query,params = None):
        if self.db == None:
            self.connect()

        self.execute(query,params)
        result = self.cursor.fetchall()
        return result

    def create(self):
        self.connect()

        try:

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    desc TEXT NOT NULL,
                    color INTEGER DEFAULT 0,
                    active INTEGER DEFAULT 1,
                    task INTEGER,
                    note TEXT
                )""")

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pomodoros (
                    id INTEGER PRIMARY KEY,
                    time TIMESTAMP NOT NULL,
                    duration INTEGER NOT NULL,
                    task INTEGER
                )""")

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    variable TEXT PRIMARY KEY NOT NULL,
                    value TEXT
                )""")

            if False:
                # remove these:
                self.cursor.execute("DELETE FROM tasks")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,desc) VALUES (1,'Education')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,desc) VALUES (2,'Research')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,desc) VALUES (3,'Learning')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,desc) VALUES (4,'Personal')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,desc) VALUES (5,'Config')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,desc) VALUES (6,'Project')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,desc) VALUES (20,'Reading')")

                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (7 ,1,1,'Formeel Denken')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (8 ,2,9,'RUDIN')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (9 ,4,2,'Cumodoro')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (10,4,4,'Cookbook')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (11,5,5,'Vim')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (12,6,11,'MoSCHA')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (30,20,5,'Reading Club')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (31,20,18,'Research')")

                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (13,8,6,'Paper')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (14,8,3,'Source')")
                self.cursor.execute("INSERT OR IGNORE INTO tasks (id,task,color,desc) VALUES (40,31,202,'Model Counting')")

                try:
                    self.cursor.execute("INSERT OR IGNORE INTO config (variable,value) VALUES (?,?)",('TIME_SLOT',str(config.TIME_SLOT)))
                    self.cursor.execute("INSERT OR IGNORE INTO config (variable,value) VALUES (?,?)",('TIME_SLOT_NAME',str(config.TIME_SLOT_NAME)))
                    self.cursor.execute("INSERT OR IGNORE INTO config (variable,value) VALUES (?,?)",('TIME_POMODORO',str(config.TIME_POMODORO)))
                    self.cursor.execute("INSERT OR IGNORE INTO config (variable,value) VALUES (?,?)",('TIME_BREAK',str(config.TIME_BREAK)))
                except: pass

            self.db.commit()
        except sql.Error as e:
            print("Query Error on creation:",e)
            sys.exit(1)

    def update_config(self,variable,value):
        self.execute("UPDATE config SET value = ? WHERE variable == ?",(str(value),variable))

    def savepoint(self):
        if not self.has_savepoint:
            self.cursor.execute("savepoint cumodoro")
            self.has_savepoint = True
        else:
            raise DatabaseError("Savepoint already present")

    def rollback(self):
        if self.has_savepoint:
            self.cursor.execute("rollback to savepoint cumodoro")
        else:
            raise DatabaseError("Cannot rollback: savepoint doesn't exist")

    def release(self):
        if self.has_savepoint:
            self.cursor.execute("release savepoint cumodoro")
            self.has_savepoint = False
        else:
            raise DatabaseError("Cannot release: savepoint doesn't exist")

    def load_config(self):
        configlist = self.request("SELECT variable,value FROM config")
        if configlist != None:
            for variable,value in configlist:
                try:
                    exec("config."+str(variable)+" = "+str(value))
                except:
                    exec("config."+str(variable)+" = '"+str(value)+"'")
        else:
            log.debug("No config loaded from database")

        config.init()

    def load_tasks(self):
        if self.tasks != None:
            del self.tasks
            del self.colors

        self.full_task_list = {}
        self.task_list = {}
        self.tasks = {}
        t = Task()
        t.idx = None
        t.task = None
        t.color = 0
        t.active = 1
        t.desc = "None"
        self.tasks[t.idx] = t

        raw_tasks = self.request("SELECT id,task,color,active,desc FROM tasks")
        for entry in raw_tasks:
            idx, task, color, active, desc = entry
            t = Task()
            t.idx = idx
            t.task = task
            t.color = color
            t.active = active
            t.desc = desc
            self.tasks[idx] = t

            if idx not in self.task_list:
                self.task_list[idx] = []
            if task not in self.task_list:
                self.task_list[task] = []

            self.task_list[task].append(idx)

        self.full_task_list = dict(self.task_list)
        self.colors = {None:[0]}
        self.levels = 0
        if None in self.task_list:
            q = deque([[1,None,x] for x in self.task_list[None]])
            while q:
                level,parent,idx = q.popleft()
                if self.tasks[idx].active > 0:
                    q.extend([[level+1,idx,x] for x in self.task_list[idx]])

                    if idx not in self.colors:
                        self.colors.update({idx:[]})
                    color_list = []
                    if parent in self.colors:
                        color_list.extend(self.colors[parent])
                    self.colors[idx].extend(color_list)
                    self.colors[idx].append(self.tasks[idx].color)

                    if self.levels <= level:
                        self.levels = level + 1

                else:
                    q2 = deque([[idx,x] for x in self.task_list[idx]])
                    del self.task_list[parent][self.task_list[parent].index(idx)]
                    while q2:
                        level2,parent2,idx2 = q2.popleft()
                        q2.extend([[level2+1,idx2,x] for x in self.task_list[idx2]])
                        del self.task_list[idx2]

            for idx,color_list in self.colors.items():
                length = len(color_list)
                if length < self.levels:
                    if length > 0:
                        self.colors[idx].extend([color_list[-1] for i in range(self.levels - length)])
                    else:
                        self.colors[idx].extend([0 for i in range(self.levels - length)])

        self.task_chain = {None:[]}
        for task in self.tasks.keys():
            self.task_chain.update({task:self.find_task(task)})

    def find_task_rec(self,idx,l):
        for i in range(0,len(l)):
            if l[i] == idx:
                return [(l[i],i)]

            if l[i] in self.task_list:
                rl = self.find_task_rec(idx,self.task_list[l[i]])
                if len(rl) > 0:
                    rl.insert(0,(l[i],i))
                    return rl

        return []

    def find_task(self,idx):
        if None not in self.task_list:
            return []
        else:
            rl = self.find_task_rec(idx,self.task_list[None])
            return rl

    def get_pomodoros(self):
        pass

    def sync(self,T):
        pass

    def delete_task_rec(self,tl):
        for i in range(len(tl)):
            t = tl[i]
            self.delete_task_rec(self.task_list[t])
            log.debug("delete task "+str(t)+": "+str(self.task_list[t]))
            self.cursor.execute("DELETE FROM tasks WHERE id = ?",(t,))
            self.cursor.execute("UPDATE pomodoros SET task = ? WHERE task = ?",(None,t))

    def delete_task(self,idx,immediate = False):
        self.connect()
        self.delete_task_rec([idx])
        if immediate:
            self.db.commit()

    def store_task(self,e):
        if e.idx == None:
            data = (e.desc, e.color, e.active, e.task)
            self.execute("INSERT INTO tasks (desc,color,active,task) VALUES (?,?,?,?)",data)
            e.idx = self.cursor.lastrowid
        else:
            data = (e.desc, e.color, e.active, e.task, e.idx)
            self.execute("UPDATE tasks SET desc = ?, color = ?, active = ?, task = ? WHERE id = ?", data)

    def alter_pomodoro_task(self,idx,task,time=None,immediate=False):
        if idx == None:
            self.execute("INSERT INTO pomodoros (time,duration,task) VALUES (?,?,?)", (time,config.TIME_POMODORO_SEC,task), immediate)
        else:
            self.execute("UPDATE pomodoros SET task = ? WHERE id == ?",(task,idx),immediate)

    def delete_pomodoro(self,idx,immediate=False):
        if idx != None:
            self.execute("DELETE FROM pomodoros WHERE id = ?", (idx,), immediate)

    def add_pomodoro_now(self,task):
        if task == None:
            self.execute("INSERT INTO pomodoros (time,duration) VALUES (?,?)",(datetime.datetime.now(),config.TIME_POMODORO_SEC))
        else:
            data = (datetime.datetime.now(),config.TIME_POMODORO_SEC,task)
            self.execute("INSERT INTO pomodoros (time,duration,task) VALUES (?,?,?)",data)

