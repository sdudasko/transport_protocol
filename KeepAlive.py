from threading import Timer

class KeepAlive(object):
    def __init__(self, interval, func):
        self.timer = None
        self.interval = interval
        self.function = func

        def _run(self):
            self.is_running = False
            self.start()
            self.func()

        def start(self):
            if not self.is_running:
                self._timer = Timer(self.interval, self._run)
                self._timer.start()
                self.is_running = True

        def stop(self):
            self._timer.cancel()
            self.is_running = False