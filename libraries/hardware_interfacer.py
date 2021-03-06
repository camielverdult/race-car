import gpiozero, asyncio, tweaking, cv2, time, os

import board #import the board facilities.
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33 #import the facilities of the gyroscope.

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

        self.distance_sensor = gpiozero.DistanceSensor(echo=tweaking.sonar_echo_pin, trigger=tweaking.sonar_trigger_pin)

        # Set servo to middle
        print("Setting servo to start value {}".format(tweaking.servo_middle))
        self.servo.angle = tweaking.servo_middle

        # try:
        #     self.power_sensor = adafruit_ina260.INA260(busio.I2C(tweaking.scl, tweaking.sda))
        # except:
        self.power_sensor = None

        try:
            i2c = board.I2C() # Determine the I2C address of the gyroscope.
            self.gyro = LSM6DS33(i2c) # Create an object of the specific library of the sensor (gyroscope).
        except:
            self.gyro = None

    # This function is called when an object is close to us
    async def avoid_object(self):
        print("Avoiding object!")

        # Brake and steer straight
        self.motor.brake()
        self.servo.angle = tweaking.servo_middle

        # brake, steer right and drive forwards for 1.5 seconds
        self.motor.brake()
        self.servo.angle = tweaking.servo_right
        self.motor.drive_forwards(tweaking.avoiding_drive_speed)
        await asyncio.sleep(0.5)

        # Steer straight
        self.servo.angle = tweaking.servo_middle
        await asyncio.sleep(0.5)

        # Steer left
        self.servo.angle = tweaking.servo_left
        await asyncio.sleep(0.8)

        # # Steer right to get back on the line
        # self.servo.angle = tweaking.servo_right
        # await asyncio.sleep(1)

        # self.motor.brake()
        # self.servo.angle = tweaking.servo_middle

    def set_servo(self, degrees):   
        self.servo.angle = degrees  

    def map_value(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    async def drive(self, line_detector):

        # while True:

        #     self.motor.drive_forwards(0.3)
        #     await asyncio.sleep(1)
        #     self.motor.brake()
        #     await asyncio.sleep(1)
        #     self.motor.drive_backwards(0.3)
        #     await asyncio.sleep(1)
        #     self.motor.brake()
        #     await asyncio.sleep(1)

        video_capture = cv2.VideoCapture(0)
        video_capture.set(3, 160)
        video_capture.set(4, 120)

        self.motor.drive_forwards(tweaking.motor_speed_range[0])

        timer = 0

        while True:

            # Capture the frames
            ret, frame = video_capture.read()

            frame = cv2.bitwise_not(frame)

            # Crop the image
            crop_img = frame[60:120, 0:160]

            # Convert to grayscale
            gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

            # Gaussian blur
            blur = cv2.GaussianBlur(gray,(5,5),0)
            
            # Color thresholding
            ret,thresh1 = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)

             # Erode and dilate to remove accidental line detections
            mask = cv2.erode(thresh1, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1.2, 100)
            # if circles:
            #     print("Circle found, goodbye!")
            #     self.servo.angle = tweaking.servo_middle
            #     await asyncio.sleep(1)
            #     os._exit(0)
                

            # Find the contours of the frame
            contours, hierarchy = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)

            if len(contours) > 0:
                self.motor.value = tweaking.motor_speed_range
                c = max(contours, key=cv2.contourArea)

                M = cv2.moments(c)

                cx = int(M['m10']/M['m00'])
                # cy = int(M['m01']/M['m00'])

                # cv2.line(crop_img,(cx,0),(cx,720),(255,0,0),1)

                # cv2.line(crop_img,(0,cy),(1280,cy),(255,0,0),1)

                # cv2.drawContours(crop_img, contours, -1, (0,255,0), 1)

                # cv2.imwrite("lines.jpg", crop_img)

                # (flag, encodedImage) = cv2.imencode(".jpg", crop_img)

                # if flag:
                #     pass

                print(cx)

                if cx >= 120:
                    self.motor.brake()
                    self.servo.angle = tweaking.servo_right / 2
                    self.motor.drive_forwards(tweaking.motor_speed_range[0])
                
                if cx < 120 and cx > 50:

                    if self.distance_sensor.value < tweaking.sonar_threshold_distance:
                        await self.avoid_object()

                    self.servo.angle = tweaking.servo_middle
                    self.motor.drive_forwards(tweaking.motor_speed_range[0])

                if cx <= 50:
                    self.motor.brake()
                    self.servo.angle = tweaking.servo_left / 2
                    self.motor.drive_forwards(tweaking.motor_speed_range[0])

                timer = time.perf_counter()

            else:
                self.servo.angle = tweaking.servo_right
                self.motor.drive_forwards(tweaking.motor_speed_range[0])
                if (time.perf_counter() - timer) > 1:
                    self.motor.drive_forwards(tweaking.motor_speed_range[0] + 0.025)
                else:
                    self.motor.drive_forwards(tweaking.motor_speed_range[0])

            # helling = 0

            # for i in range(10):
            #     helling += self.gyro.acceleration[0]

            # helling = helling / 10

            # print(helling)
            # if helling < tweaking.gyro_power_angle:
            #     print("hill!")
            #     self.servo.angle = tweaking.servo_middle
            #     self.motor.value = tweaking.motor_max
            #     await asyncio.sleep(0.5)
            #     self.motor.value = tweaking.motor_speed_range[0]
            
                

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

        self.cw = gpiozero.DigitalOutputDevice(tweaking.reverse_pin, active_high=True)

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
        self.cw.off()
        speed = min(speed, tweaking.motor_max)
        self.motor_go(1, speed)

    def drive_backwards(self, speed: float):
        self.cw.on()
        speed = min(speed, tweaking.motor_max)
        self.motor_go(2, speed)

    def brake(self):
        self.motor_go(3, 0)