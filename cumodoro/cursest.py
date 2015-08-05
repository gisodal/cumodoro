import queue
import threading
import logging

log = logging.getLogger('cumodoro')

class Refresher:
    def __init__(self):
        self.q = queue.Queue(maxsize=0)
        self.thread = None

    def put(self, w):
        event = threading.Event()
        self.q.put([w,event])
        event.wait()
        del event

    def get(self):
        return self.q.get()

    def start(self):
        self.thread = threading.Thread(target=self.run, name="Refresher")
        self.thread.setDaemon(True)
        self.thread.start()

    def run(self):
        while True:
            w,event = self.q.get()
            try:
                w.refresh()
            except:
                log.error("Refresher: could not refresh window")

            event.set()

