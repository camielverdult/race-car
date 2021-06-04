import numpy as np

# pins
servo_pin = 29
sonar_echo_pin = 24
sonar_trigger_pin = 23

# fine-tuning values
servo_left = 29
servo_right= -35
servo_middle = (servo_left + servo_right) / 2

motor_speed_range = [0, 0.3]

sonar_threshold_distance = 0.4

avoiding_backwards_time = 0.5
avoiding_forwards_time = 0.2
avoiding_steer_time = 0.5
avoiding_straight_time = 0.5
avoiding_drive_speed = 0.2

# motor shield pins
input_pins = [22, 25]  # This pin control the state of the bridge in normal operation according to the truth table (brake to VCC, brake to GND, clockwise and counterclockwise).
pwm_pin = 21     # Gates of low side FETs are modulated by the PWM signal during their ON phase allowing speed control of the motor.
enable_pin = 23  # When externally pulled low, they disable half-bridge A or B

# I2c pins
sda = 30
scl = 31

# hough transform stuff
rho = 2                 # rho : The resolution of the parameter r in pixels. We use 1 pixel.
theta = np.pi/180       # theta: The resolution of the parameter θ in radians. We use 1 degree (CV_PI/180)
threshold = 15          # threshold: The minimum number of intersections to "*detect*" a line
min_line_length = 100   # minLineLength: The minimum number of points that can form a line. Lines with less than this number of points are disregarded.
max_line_gap = 30       # maxLineGap: The maximum gap between two points to be considered in the same line.