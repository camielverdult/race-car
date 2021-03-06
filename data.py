import tweaking, math

class resolution:
    def __init__(self, x = 0, y = 0):
        self.x: int = x
        self.y: int = y

class theta:
    def __init__(self, theta = 0, min = 0, max = 0):
        self.min: int = min
        self.max: int = max
        self.theta: int = theta
        self.previous = []

    def update(self, theta: int):

        self.previous.append([self.min, self.theta, self.max])

        if not theta:
            theta = 0

        self.theta = theta

        if theta > self.max:
            self.max = theta
        if theta < self.min:
            self.min = theta

    def get(self):
        return self.min, self.theta, self.max

    def get_angle(self):
        min_t, t, max_t = self.get()
        return (min_t * (180.0/math.pi)), (t * (180.0/math.pi)), (max_t * (180.0/math.pi))
    
class data:
    def __init__(self):
        self.tweaking = tweaking

        # Camera/sensor stuff
        self.lines: list = []
        self.theta: theta = theta()
        self.angle = 0
        self.resolution: resolution = resolution()

        # value from distance sensor
        self.distance: int = 0

        # Battery stuff
        self.voltage: int = 0
        self.current: int = 0
        self.power: int = 0

    def json(self):
        return {
            # Camera/sensor stuff
            "lines" : self.lines,
            "angle" : self.theta.get_angle()[1],
            "resolution" : [self.resolution.x, self.resolution.y],

            # Distance
            "distance" : self.distance,

            # Battery stuff
            "voltage" : self.voltage,
            "current" : self.current,
            "power" : self.power
        }

    def get(self):
        return self