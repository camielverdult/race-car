import gpiozero, adafruit_ina260, busio, asyncio, time

class HwInterfacer:

    def __init__(self, 
                sonar_echo_pin, sonar_trig_pin, 
                servo_pin,
                motor_pin, get_data_function
                ):
        # https://gpiozero.readthedocs.io/en/stable/api_output.html#servo

        # Connect a power source (e.g. a battery pack or the 5V pin) to the power cable of the servo 
        # (this is typically colored red).
        # Connect the ground cable of the servo (typically colored 
        # black or brown) to the negative of your battery pack, or a GND pin.
        # Connect the final cable typically colored white or orange) to the GPIO pin 
        # you wish to use for controlling the servo.

        self.get_data_function = get_data_function

        self.servo = gpiozero.AngularServo(servo_pin)

        # https://gpiozero.readthedocs.io/en/stable/api_output.html#motor   

        # Attach an H-bridge motor controller to your Pi
        # Connect a power source (e.g. a battery pack or the 5V pin) to the controller
        # Connect the outputs of the controller board to the two terminals of the motor
        # Connect the inputs of the controller board to two GPIO pins.

        self.motor = gpiozero.PWMOutputDevice(motor_pin, active_high=False, frequency=50)

        # https://gpiozero.readthedocs.io/en/stable/api_input.html#distancesensor-hc-sr04

        # Connect the GND pin of the sensor to a ground pin on the Pi.
        # Connect the TRIG pin of the sensor a GPIO pin.
        # Connect one end of a 330Ω resistor to the ECHO pin of the sensor.
        # Connect one end of a 470Ω resistor to the GND pin of the sensor.
        # Connect the free ends of both resistors to another GPIO pin. This forms the required voltage divider.
        # Finally, connect the VCC pin of the sensor to a 5V pin on the Pi.

        self.distance_sensor = gpiozero.DistanceSensor(sonar_echo_pin, sonar_trig_pin)

        # Set to default values
        steer_range = self.get_data_function().steer_range
        start_angle = ( steer_range[0] + steer_range[1] ) / 2
        print("Setting servo to start value {}".format(start_angle))
        self.servo.angle = start_angle

        self.power_sensor = adafruit_ina260.INA260(busio.I2C(2, 3))

    def set_servo(self, degrees):   
        self.servo.value = degrees  

    def map_value(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    async def drive(self, get_data_function):
        while asyncio.get_event_loop().is_running():
            start = time.perf_counter()

            data = get_data_function()

            # Theta:
            # 0 means straight
            # -x means left
            # +x means right

            # Laat de motor sturen op basis van de hoek die we krijgen
            # De hoek die moet natuurlijk tussen de min en max stuur hoek liggen
            # Dus we gebruiken deze als out_min en out_max waardes
            angle = self.map_value(data.theta.theta, data.theta_min, data.theta_max, data.min_steer, data.max_steer)

            # https://gpiozero.readthedocs.io/en/stable/api_output.html#gpiozero.Motor.value

            # Hetzelfde geldt hier, maar dan op basis van de hoek waarmee we sturen
            # en de min en max waarde van de motor
            self.servo.angle = angle

            self.motor.value = 0

            await asyncio.sleep((1.0 - (time.perf_counter() - start)/5))
