import tweaking

class resolution:
    def __init__(self, x = 0, y = 0):
        self.x: int = x
        self.y: int = y

class theta:
    def __init__(self, theta = 0, min = 0, max = 0):
        self.min: int = min
        self.max: int = max
        self.theta: int = theta

    def update(self, theta: int):

        self.theta = theta

        if theta > self.max:
            self.max = theta
        if theta < self.min:
            self.min = theta

    def get(self):
        return self.min, self.theta, self.max
    
class data:
    def __init__(self):
        self.tweaking = tweaking

        # Camera/sensor stuff
        self.lines: list = []
        self.theta: theta = theta()
        self.resolution: resolution = resolution()

        # value from distance sensor
        self.distance: int = 0

        # Battery stuff
        self.voltage: int = 0
        self.current: int = 0
        self.power: int = 0

        self.servo_left = tweaking.servo_left
        self.servo_right = tweaking.servo_right

        self.servo_pin = self.tweaking.servo
        self.motor_pin = self.tweaking.motor
        self.sonar_echo = self.tweaking.sonar_echo
        self.sonar_trigger = self.tweaking.sonar_trigger
        self.steer_range = self.tweaking.servo_steer_range
        self.steer_angle = (self.steer_range[0] + self.steer_range[1])/2

    def json(self):
        return {
            # Camera/sensor stuff
            "lines" : self.lines,
            "theta" : self.theta.theta,
            "theta_min" : self.theta.min,
            "theta_max" : self.theta.max,
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