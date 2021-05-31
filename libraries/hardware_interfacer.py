
import time, gpiozero

class HwInterfacer:

    def __init__(self, 
                sonar_echo_pin = 0, sonar_trig_pin = 0, 
                servo_pin = 12, servo_steer_range = [55, 65], 
                motor_pin = 13, motor_speed_range = [-1, 1]
                ):
        # https://gpiozero.readthedocs.io/en/stable/api_output.html#servo

        # Connect a power source (e.g. a battery pack or the 5V pin) to the power cable of the servo 
        # (this is typically colored red).
        # Connect the ground cable of the servo (typically colored 
        # black or brown) to the negative of your battery pack, or a GND pin.
        # Connect the final cable typically colored white or orange) to the GPIO pin 
        # you wish to use for controlling the servo.

        self.servo = gpiozero.AngularServo(servo_pin)
        self.servo_steer_range = servo_steer_range
        self.servo_start_angle = (self.servo_steer_range[1] + self.servo_steer_range[0]) / 2

        if self.servo_start_angle > 180 or self.servo_steer_range < 0:
            self.servo_start_angle = 0
        
        self.servo.angle = self.servo_start_angle

        # https://gpiozero.readthedocs.io/en/stable/api_output.html#motor   

        # Attach an H-bridge motor controller to your Pi
        # Connect a power source (e.g. a battery pack or the 5V pin) to the controller
        # Connect the outputs of the controller board to the two terminals of the motor
        # Connect the inputs of the controller board to two GPIO pins.

        self.motor = gpiozero.Motor(motor_pin)
        self.motor_speed_range = motor_speed_range

        # https://gpiozero.readthedocs.io/en/stable/api_input.html#distancesensor-hc-sr04

        # Connect the GND pin of the sensor to a ground pin on the Pi.
        # Connect the TRIG pin of the sensor a GPIO pin.
        # Connect one end of a 330Ω resistor to the ECHO pin of the sensor.
        # Connect one end of a 470Ω resistor to the GND pin of the sensor.
        # Connect the free ends of both resistors to another GPIO pin. This forms the required voltage divider.
        # Finally, connect the VCC pin of the sensor to a 5V pin on the Pi.

        self.sonar = gpiozero.DistanceSensor(sonar_echo_pin, sonar_trig_pin)

        # Set to default values
        print("Setting servo to start value {}".format(self.servo_start_angle))
        self.servo.angle = self.servo_start_angle

    async def get_distance(self):
        return self.sonar.distance
        
    def set_servo(self, degrees):   
        self.servo.value = degrees  

    def map_value(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    async def drive(self, get_theta_function, initial_speed = 0):
        theta_min, theta, theta_max = get_theta_function()

        # Theta:
        # 0 means straight
        # -x means left
        # +x means right

        # Laat de motor sturen op basis van de hoek die we krijgen
        # De hoek die moet natuurlijk tussen de min en max stuur hoek liggen
        # Dus we gebruiken deze als out_min en out_max waardes
        angle = self.map_value(theta, theta_min, theta_max, self.servo_steer_range[0], self.servo_steer_range[1])

        # https://gpiozero.readthedocs.io/en/stable/api_output.html#gpiozero.Motor.value

        # Hetzelfde geldt hier, maar dan op basis van de hoek waarmee we sturen
        # en de min en max waarde van de motor
        speed = self.map_value(angle, self.servo_steer_range[0], self.servo_steer_range[1], self.motor_speed_range[0], self.motor_speed_range[1])

        self.servo.angle = angle

        self.motor.value = speed