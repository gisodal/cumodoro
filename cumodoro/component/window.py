from cumodoro.error import *
import logging

log = logging.getLogger('cumodoro')

class Window(object):
    def __init__(self):
        self.frames = {}
        self.focus = False
        self.name = ""

    def add_frame(self,frame_id,frame):
        frame.title = frame_id
        self.frames[frame_id] = frame

    def del_frame(self,frame_id):
        if frame_id in self.frames:
            del self.frames[frame_id]

    def update(self):
        for title,frame in self.frames.items():
            frame.update()

    def refresh(self):
        for title,frame in self.frames.items():
            frame.refresh()

    def set_focus(self,f):
        self.focus = f
        for title,frame in self.frames.items():
            frame.set_focus(f)

    def set_manual_focus(self,f):
        self.manual_focus = f
        for title,frame in self.frames.items():
            frame.set_manual_focus(f)

    def destroy(self):
        for title,frame in self.frames.items():
            frame.destroy()

    def create(self):
        for title,frame in self.frames.items():
            frame.create()

    def set_variable(self,var,value):
        if isinstance(var,str):
            exec(var+" = "+str(value))
            for frame in self.frames.values():
                exec("frame."+var+" = "+str(value))
        else:
            raise CumodoroError("Variable in window assignment must be of type string")

    def erase(self):
        for title,frame in self.frames.items():
            frame.erase()

    def set_position(self, positions):
        if isinstance(positions,tuple):
            if len(positions) != 2:
                raise CursesFrameError("Position tuple does not contain 2 values")
            else:
                positions = [ positions ]

        if isinstance(positions,list):
            if len(positions) != len(self.frames):
                raise CursesFrameError("Number of position not equal to number of frames")
            else:
                for i,title in zip(range(len(self.frames)),list(self.frames.keys())):
                    if len(positions[i]) != 2:
                        raise CursesFrameError("Position tuple "+str(i)+" does not contain 2 values")

                    x,y = positions[i]
                    self.frames[title].set_position(x,y)
        else:
            raise CursesFrameError("Position argument must be as list of (x,y) tuples")


