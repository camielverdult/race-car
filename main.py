import data, math

from libraries import car_web_interface, hardware_interfacer, image

import asyncio
import os
import cv2
import tweaking

class CarController:

    def __init__(self):
        self.data = data.data()

        self.web_interface = car_web_interface.WebInterface(self.data.json)

        self.capture = self.get_capture()

        self.line_detector = image.LineFinder(self.capture, self.data.get)

        self.hw_interfacer = hardware_interfacer.HwInterfacer(self.data.get)

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
            # Value updating
            asyncio.ensure_future(self.value_updater())

            # Web interface
            asyncio.ensure_future(self.web_interface.run())

            # Hardware interface
            asyncio.ensure_future(self.hw_interfacer.drive(self.line_detector))

            # Run async stuff on new thread
            loop.run_forever()

        finally:
            print("Closing Loop")
            loop.close()

    async def value_updater(self):
        print("Starting value updater...")
        while asyncio.get_event_loop().is_running():

            # Update power readings
            if self.hw_interfacer.power_sensor:
                self.data.voltage = self.hw_interfacer.power_sensor.voltage
                self.data.current = self.hw_interfacer.power_sensor.current
                self.data.power = self.hw_interfacer.power_sensor.power

            # Update distance
            self.data.distance = self.hw_interfacer.distance_sensor.distance * 100

            # Compute new lines

            theta, lines = await self.line_detector.new_hough()

 
            if theta:
                theta = sum(theta)/len(theta)
            else:
                theta = 0

            angle = theta * (180/math.pi)

            self.data.angle = angle

            self.data.lines = lines

            self.data.resolution.x = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.data.resolution.y = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
            # Sleep for the amount of time we need to achieve our FPS
            await asyncio.sleep(0.05)

        print("Stopping value updater...")

if __name__ == "__main__":
    car = CarController()
    car.start()
