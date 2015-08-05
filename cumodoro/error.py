class CumodoroError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class CursesFrameError(CumodoroError):
    pass

class CursesBoundsError(CumodoroError):
    pass

class DatabaseError(CumodoroError):
    pass
