import pygame


class Timer:

    def __init__(
            self, clock, period: int,
            initial_value: bool = False,
            periodic: bool = False,
            running: bool = True,
            method=None,
    ):

        clock.timers.append(self)
        self.clock = clock
        self.period = period
        self.periodic = periodic

        self.statemark = self.clock.now - int(not running) * self.period
        self.modifier = 1

        self.running = running
        self.signal = [initial_value, False]

        self.method = method

    @property
    def progress(self) -> float:  # (0; 1]
        return self.raw_progress if self.running else 1

    @property
    def raw_progress(self) -> float:
        return (self.clock.now - self.statemark) / (self.period * self.modifier)

    def force(self):
        self.running = True
        self.statemark = -self.period

    def reset(self, period=None):
        self.statemark = self.clock.now
        self.running = True
        if period is not None:
            self.period = period

    def delay(self, period):
        self.statemark += period

    def update(self):
        self.signal[1] = self.signal[0]
        if self.running:
            self.signal[0] = False
            if self.clock.now - self.statemark >= self.period * self.modifier:
                self.signal[0] = True
                self.running = self.periodic
                self.statemark = self.clock.now
                if self.method is not None:
                    self.method()
                    if not self.periodic:
                        self.method = None

    def query(self, period=None) -> bool:
        if self.signal[0] and period is not None:
            self.reset(period)
        return self.signal[0]

    def tick(self, period=None) -> bool:
        result = self.signal[0] - self.signal[1] == 1
        if result and period is not None:
            self.reset(period)
        return result

    def time_method(self, method):
        if self.method is None:
            self.method = method
            self.reset()

    def kill(self):
        if self in self.clock.timers:
            self.clock.timers.remove(self)
        del self


class Clock:

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.timers = []
        self.now = 0
        self.dt = 0

    def timer(self, *args, **kwargs) -> Timer:
        return Timer(self, *args, **kwargs)

    def update(self):
        self.now = pygame.time.get_ticks()
        for timer in self.timers:
            timer.update()

    def tick(self, fps) -> float:
        self.update()
        self.dt = self.clock.tick(fps) / 1000
        return self.dt