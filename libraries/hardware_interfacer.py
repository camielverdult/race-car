import gpiozero, asyncio, time, tweaking #, adafruit_ina260, busio

class HwInterfacer:

    def __init__(self, get_data_function):
        # https://gpiozero.readthedocs.io/en/stable/api_output.html#servo

        # Connect a power source (e.g. a battery pack or the 5V pin) to the power cable of the servo 
        # (this is typically colored red).
        # Connect the ground cable of the servo (typically colored 
        # black or brown) to the negative of your battery pack, or a GND pin.
        # Connect the final cable typically colored white or orange) to the GPIO pin 
        # you wish to use for controlling the servo.

        self.get_data_function = get_data_function

        self.servo = gpiozero.AngularServo(tweaking.servo_pin)

        # https://gpiozero.readthedocs.io/en/stable/api_output.html#motor   

        # Attach an H-bridge motor controller to your Pi
        # Connect a power source (e.g. a battery pack or the 5V pin) to the controller
        # Connect the outputs of the controller board to the two terminals of the motor
        # Connect the inputs of the controller board to two GPIO pins.

        self.motor = MotorShield()

        # https://gpiozero.readthedocs.io/en/stable/api_input.html#distancesensor-hc-sr04

        # Connect the GND pin of the sensor to a ground pin on the Pi.
        # Connect the TRIG pin of the sensor a GPIO pin.
        # Connect one end of a 330Ω resistor to the ECHO pin of the sensor.
        # Connect one end of a 470Ω resistor to the GND pin of the sensor.
        # Connect the free ends of both resistors to another GPIO pin. This forms the required voltage divider.
        # Finally, connect the VCC pin of the sensor to a 5V pin on the Pi.

        self.distance_sensor = gpiozero.DistanceSensor(echo=tweaking.sonar_echo_pin, trigger=tweaking.sonar_trigger_pin, threshold_distance=tweaking.sonar_threshold_distance)
        self.distance_sensor.when_activated = self.avoid_object
        self.in_range = False

        # Set servo to middle
        print("Setting servo to start value {}".format(tweaking.servo_middle))
        self.servo.angle = tweaking.servo_middle

        # try:
        #     self.power_sensor = adafruit_ina260.INA260(busio.I2C(tweaking.scl, tweaking.sda))
        # except:
        self.power_sensor = None

    # This function is called when an object is close to us
    def avoid_object(self):
        print("Avoiding object!")
        self.in_range = True

        # Brake, steer straight, and back up for a second
        self.motor.brake()
        self.servo.angle = tweaking.servo_middle
        self.motor.drive_backwards(tweaking.avoiding_drive_speed)
        time.sleep(tweaking.avoiding_backwards_time)

        # brake, steer right and drive forwards for 1.5 seconds
        self.motor.brake()
        self.servo.angle = tweaking.servo_right
        self.motor.drive_forwards(tweaking.avoiding_drive_speed)
        time.sleep(tweaking.avoiding_forwards_time)

        # Steer straight
        self.servo.angle = tweaking.servo_middle
        time.sleep(tweaking.avoiding_straight_time)

        # Steer left towards the line
        self.servo.angle = tweaking.servo_left
        time.sleep(tweaking.avoiding_steer_time)

        # Steer right to get back on the line
        self.servo.angle = tweaking.servo_right
        time.sleep(tweaking.avoiding_steer_time)

        self.motor.brake()
        self.servo.angle = tweaking.servo_middle

        # Let line following take over
        self.in_range = False

    def set_servo(self, degrees):   
        self.servo.angle = degrees  

    def map_value(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    async def drive(self, get_data_function):
        while asyncio.get_event_loop().is_running():

            # Only drive while not avoiding obstacle
            if not self.in_range:

                print("driving")

                data = get_data_function()

                # Theta:
                # 0 means straight
                # -x means left
                # +x means right

                # Laat de motor sturen op basis van de hoek die we krijgen
                # De hoek die moet natuurlijk tussen de min en max stuur hoek liggen
                # Dus we gebruiken deze als out_min en out_max waardes
                a_min, angle, a_max = data.theta.get_angle()
                print("angle_min: {} angle: {} angle_max: {}".format(a_min, angle, a_max))
                self.servo.angle = self.map_value(a_min - 180, angle - 180, a_max - 180, tweaking.servo_right, tweaking.servo_right)

                # https://gpiozero.readthedocs.io/en/stable/api_output.html#gpiozero.Motor.value

                # Hetzelfde geldt hier, maar dan op basis van de hoek waarmee we sturen
                # en de min en max waarde van de motor
                # if self.map_value(self.servo.angle, 0, tweaking.servo_right, tweaking.motor_speed_range[0], tweaking.motor_speed_range[1]):
                #     # Take turn as slow as possible
                #     self.motor.drive_forwards(tweaking.motor_speed_range[0])

                self.motor.drive_forwards(tweaking.motor_speed_range[0])

                await asyncio.sleep(0.1)

class MotorShield:

    # This is the pinout on the shield for both motor drivers
    # const int inAPin[2] = {7, 4};
    # const int pwmPin[2] = {5, 6};
    # const int enPin[2] = {0, 1};
    # const int csPin[2] = {2, 3};
    # const int statPin = 13;

    # https://github.com/sparkfun/Monster_Moto_Shield/blob/0cc320981caf554b5b359a62a0d8ff98512941fe/Firmware/MonsterMoto_Shield_Example_Sketch/MonsterMoto_Shield_Example_Sketch.ino#L122
    def __init__(
        self, 
        input_pins: list = tweaking.input_pins, # These two pins control the state of the bridge in normal operation according to the truth table (brake to VCC, brake to GND, clockwise and counterclockwise).
        pwm_pin: int = tweaking.pwm_pin,
        enable_pin: int = tweaking.enable_pin,
    ):
        # these values are either 0 or 1
        self.m_input_1 = gpiozero.DigitalOutputDevice(input_pins[0], active_high=True)
        self.m_input_2 = gpiozero.DigitalOutputDevice(input_pins[1], active_high=True)

        self.m_enable_1 = gpiozero.DigitalOutputDevice(enable_pin, active_high=True)

        # pwm value is between 0 and 1
        self.m_pwm = gpiozero.PWMOutputDevice(pwm_pin)

        self.motor_off()

    # https://github.com/sparkfun/Monster_Moto_Shield/blob/0cc320981caf554b5b359a62a0d8ff98512941fe/Firmware/MonsterMoto_Shield_Example_Sketch/MonsterMoto_Shield_Example_Sketch.ino#L141
    def motor_off(self):
        self.motor_go(3, 0.0)

    def motor_go(self, mode: int, speed: float):
        #define BRAKEVCC 0: BRAKEVCC (0): Brake to VCC
        #define CW  1: CW (1): Turn Clockwise
        #define CCW 2: CCW (2): Turn Counter-Clockwise
        #define BRAKEGND 3: BRAKEGND (3): Brake to GND

        #define MOTOR_A 0
        #define MOTOR_B 1

        self.m_enable_1.on()

        if mode == 0:
            self.m_input_1.on()
            self.m_input_2.on()
        elif mode == 1:
            self.m_input_1.on()
            self.m_input_2.off()
        elif mode == 2:
            self.m_input_1.off()
            self.m_input_2.on()
        elif mode == 3:
            self.m_input_1.off()
            self.m_input_2.off()

        self.m_pwm.value = speed

    def drive_forwards(self, speed: float):
        speed = min(speed, tweaking.motor_max)
        self.motor_go(1, speed)

    def drive_backwards(self, speed: float):
        speed = min(speed, tweaking.motor_max)
        self.motor_go(2, speed)

    def brake(self):
        self.motor_go(3, 0)