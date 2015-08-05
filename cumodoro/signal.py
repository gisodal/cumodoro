#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import signal
import sys
import curses
import subprocess

def signal_handler(signal, frame):
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    sys.exit(0)

def sigwinch_handler(n,frame):
    curses.endwin()
    curses.initscr()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGWINCH, sigwinch_handler)

