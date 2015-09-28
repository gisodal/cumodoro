# Cumodoro
Commandline interface to the *pomodoro* technique using ncursus.

<img style="max-width: 100%;" src="https://raw.githubusercontent.com/gisodal/cumodoro/screenshots/main.png" />

## Instructions
To execute simply type "./run.py" in the program directory. Upon first launch a folder *.cumodoro* will be created in your home directory that will contain a SQLITE database for holding all settings and pomodoros. No tasks will exist, so before assigning any pomodoro to a task, these will have to be created in the **Settings** window. Note that changing settings or pomodoros is only possible when the timer is not running.

| Action        | Key | Alternative |
| ------------- |:-------------:|:----------:|
| Left | *h* | [leftarrow]|
| Down | *j* | [downarrow] |
| Up | *k* | [uparrow] |
| Right | *l* | [rightarrow] |
| Quit | *q*| |
| Cancel | [esc] |
|Timer | *t* | *T* |
|Weekview | *w* | *W* |
|Settings | *s* | *S* |

For other actions follow the instructions at the bottom of the screen.

### Timer
The **Timer** window shows the pomodoro timer. Use the navigation keys to select the task you want to assign the pomodoro to. Upon completing a pomodoro, the screen will flash 3 times and an overtime clock will start at the bottom left of the main timer. Pressing [Enter] at this time will start a new pomodoro with current overtime deducted. The overtime clock will turn red once break time is over (default 5 min).

<img style="max-width: 100%;" src="https://raw.githubusercontent.com/gisodal/cumodoro/screenshots/timer2.png" />

### Weekview
The **Weekview** window show all pomodoros of the current week. Use navigation keys to traverse other weeks. Tasks have a hierarchical structure. You can display pomodoro colors according the *level* in the hierarchy.

<img style="max-width: 100%;" src="https://raw.githubusercontent.com/gisodal/cumodoro/screenshots/weekview2.png" />

### Settings
The **Settings** window shows all settings and tasks. Tasks are ordered with a hierarchy, by inserting a task and moving it under the appropriate task with the navigation keys.

<img style="max-width: 100%;" src="https://raw.githubusercontent.com/gisodal/cumodoro/screenshots/settings2.png" />

## Author

Giso H. Dal

