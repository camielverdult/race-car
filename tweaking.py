import numpy as np
import math

# pins
servo_pin = 21
sonar_echo_pin = 27
sonar_trigger_pin = 22

# fine-tuning values
servo_left = 23
servo_right= -50
servo_middle = (servo_left + servo_right) / 2 #-16
nerf_angle = 10
steer_after_angle = 5

servo_mapping_values = [50, -50]

motor_speed_range = [0.03, 0.05]
motor_max = 0.1

sonar_threshold_distance = 0.05

avoiding_backwards_time = 1.5
avoiding_forwards_time = 3.5
avoiding_steer_time = 0.5
avoiding_straight_time = 0.5
avoiding_drive_speed = motor_speed_range[0]

# motor shield pins:
# const int inAPin[2] = {7, 4};
# const int pwmPin[2] = {5, 6};
# const int enPin[2] = {0, 1};
# const int csPin[2] = {2, 3};
# const int statPin = 13;

# pi -> shield pins:
input_pins = [6, 26]  # This pin control the state of the bridge in normal operation according to the truth table (brake to VCC, brake to GND, clockwise and counterclockwise).
pwm_pin = 5     # Gates of low side FETs are modulated by the PWM signal during their ON phase allowing speed control of the motor.
enable_pin = 13  # When externally pulled low, they disable half-bridge A or B

# I2c pins
sda = 2
scl = 3

# hough transform stuff
rho = 2                 # rho : The resolution of the parameter r in pixels. We use 1 pixel.
theta = np.pi/180       # theta: The resolution of the parameter θ in radians. We use 1 degree (CV_PI/180)
threshold = 15          # threshold: The minimum number of intersections to "*detect*" a line
min_line_length = 100   # minLineLength: The minimum number of points that can form a line. Lines with less than this number of points are disregarded.
max_line_gap = 10       # maxLineGap: The maximum gap between two points to be considered in the same line.

theta_check = 100/(180/math.pi) # 1,745329252
theta_modifier = math.pi    