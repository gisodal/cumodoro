#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import curses
import cumodoro.config as config
import cumodoro.interface as interface
import cumodoro.globals as globals
from cumodoro.cursest import Refresher
import logging

log = logging.getLogger('cumodoro')

def set_title(msg):
    print("\x1B]0;%s\x07" % msg)

def get_title():
    print("\x1B[23t")
    return sys.stdin.read()

def save_title():
    print("\x1B[22t")

def restore_title():
    print("\x1B[23t")

def main():
    globals.refresher = Refresher()
    globals.refresher.start()
    globals.database.create()
    globals.database.load_tasks()
    os.environ["ESCDELAY"] = "25"
    save_title()
    set_title("Cumodoro")

    curses.wrapper(interface.main)
    restore_title()

