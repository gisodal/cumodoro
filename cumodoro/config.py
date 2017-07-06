#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
from cumodoro.timeconvert import time_to_sec
import os
import logging
import sys
import math
#import cumodoro.signal

HOME = os.path.expanduser("~")
CONFIG_DIR = HOME + "/.cumodoro"
DATABASE = CONFIG_DIR + "/data.db"
LOGFILE = CONFIG_DIR + "/cumodoro.log"

TIME_SLOT = [ ('09:00:00','12:00:00'), ('13:00:00','18:00:00') ]
TIME_SLOT_NAME = [ 'MORNING', 'AFTERNOON' ]
TIME_POMODORO = '00:25:00'
TIME_BREAK = '00:05:00'

MESSAGE_TIME = 2

COLOR_FOCUS = 172
COLOR_SECONDARY = 202

# ---------- dont edit below this ----------------------------------

#sys.stderr = open(CONFIG_DIR + '/cumodoro.err', 'w')
def create_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CONFIG_DIR):
        print("could not create '" + CONFIG_DIR + "'")
        sys.exit(1)


create_config()

log = logging.getLogger('cumodoro')
level = logging.WARNING # logging.DEBUG
log.setLevel(level)
logfile = logging.FileHandler(LOGFILE)
logfile.setLevel(level)
formatter = logging.Formatter('[%(asctime)s] %(levelname)8s: %(message)s','%Y-%m-%d %H:%M:%S')
logfile.setFormatter(formatter)
log.addHandler(logfile)

TIME_POMODORO_SEC = 0
TIME_BREAK_SEC = 0
TIME_SLOT_SEC = []
SLOT_SIZE = []

def init():
    global TIME_POMODORO_SEC
    global TIME_BREAK_SEC
    global TIME_SLOT_SEC
    global SLOT_SIZE

    TIME_POMODORO_SEC = 0
    TIME_BREAK_SEC = 0
    TIME_SLOT_SEC = []
    SLOT_SIZE = []

    TIME_POMODORO_SEC = time_to_sec(TIME_POMODORO)
    TIME_BREAK_SEC = time_to_sec(TIME_BREAK)

    for s in range(0,len(TIME_SLOT)):
        TIME_SLOT_SEC.append((time_to_sec(TIME_SLOT[s][0]),time_to_sec(TIME_SLOT[s][1])))

    if len(TIME_SLOT_SEC) == 0:
        SLOT_SIZE = [ 16 ]
    else:
        for start,stop in TIME_SLOT_SEC:
            if start > stop:
                SLOT_SIZE.append(int(((24*3600+stop)-start)/(TIME_POMODORO_SEC+TIME_BREAK_SEC)))
            else:
                SLOT_SIZE.append(int((stop-start)/(TIME_POMODORO_SEC+TIME_BREAK_SEC)))
        SLOT_SIZE.append(int(math.ceil(len(TIME_SLOT_NAME[-1])/2)))

init()

COLORS = [0,1,18,22,27,69,46,52,57,202,213,226,234,240]
COLOR_TOTAL = 256
def init_all_color_pairs():
    for i in range(1,COLOR_TOTAL):
        curses.init_pair(i, i, -1)
        curses.init_pair(COLOR_TOTAL+i, -1, i)

