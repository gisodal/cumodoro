#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import logging
from cumodoro.error import *
log = logging.getLogger("cumodoro")


def time_to_sec(t):
    if type(t) is str:
        timesplit = re.compile(':')
        t = timesplit.split(t)
        t = [int(x) for x in t]
        time_sec = [ 3600, 60 , 1 ]
        if len(t) == 3:
            return sum([a*b for a,b in zip(t,time_sec)])
    else:
        log.error("error time: " + str(t))
    raise CumodoroError("Argument not string: --> "+str(t)+" <--")

def sec_to_time(t):
    if type(t) is int:
        time_sec = [ 3600, 60 , 1 ]
        lsttime = []
        for ts in range(len(time_sec)):
            lsttime.append(int(t / time_sec[ts]))
            t = t % time_sec[ts]

        return "{0:02d}:{1:02d}:{2:02d}".format(*lsttime)
    else:
        log.error("error time: " + str(t))
    raise CumodoroError("Argument not int: '"+str(t)+"'")

