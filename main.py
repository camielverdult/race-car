import tweaking, data

from libraries import car_web_interface, hardware_interfacer, image

import asyncio
import os
import cv2
import time

class CarController:

    def __init__(self):
        self.web_interface = car_web_interface.WebInterface()

        self.capture = self.get_capture()

        self.line_detector = image.LineFinder(self.capture)

        self.hw_interfacer = hardware_interfacer.HwInterfacer(
            sonar_echo_pin=tweaking.sonar_echo,
            sonar_trig_pin=tweaking.sonar_trigger,
            servo_pin=tweaking.servo,
            motor_pin=tweaking.motor,

            servo_steer_range=tweaking.servo_steer_range,
            motor_speed_range=tweaking.motor_speed_range
        )
        
        self.data = data.data()

        self.fps = 10

    def get_capture(self):
        capture = cv2.VideoCapture(0)

        if capture is None or not capture.isOpened():
            # There is no camera
            print("There is no camera, make sure there is a camera passed through or a webcam plugged in (or both)")
            os._exit(1)

        capture.set(3, 360)
        capture.set(4, 240)

        return capture

    def start(self):
        # Setup loop
        print("Getting async loop...")
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        
        # Start coroutines
        try:
            asyncio.ensure_future(self.line_detector)

            # Value updating
            asyncio.ensure_future(self.value_updater())

            # Web interface
            asyncio.ensure_future(self.web_interface.run(self.data.json))

            # Hardware interface
            asyncio.ensure_future(self.hw_interfacer.drive())

            # Run async stuff on new thread
            loop.run_forever()

        finally:
            print("Closing Loop")
            loop.close()

    async def value_updater(self):
        print("Starting line scanner...")
        while asyncio.get_event_loop().is_running():

            start = time.perf_counter()

            # Update power readings
            self.data.voltage = self.hw_interfacer.power_sensor.voltage
            self.data.current = self.hw_interfacer.power_sensor.current
            self.data.power = self.hw_interfacer.power_sensor.power

            # Update distance
            self.data.distance = self.hw_interfacer.distance_sensor.distance

            # Compute new lines
            theta, lines = await self.line_detector.process_frame()

            self.data.theta.update(theta)
            self.data.lines = lines

            self.data.resolution.x = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.data.resolution.y = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
            # Sleep for the amount of time we need to achieve our FPS
            await asyncio.sleep((1.0 - (time.perf_counter() - start)/self.fps))

        print("Stopping value updater...")

if __name__ == "__main__":
    car = CarController()
    car.start()
