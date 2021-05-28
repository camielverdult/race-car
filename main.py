from libraries import car_web_interface, hardware_interfacer, LSM6DS3, image

import asyncio
import os
import cv2

class CarController:

    def __init__(self):
        self.web_interface = car_web_interface.WebInterface()

        self.capture = cv2.VideoCapture(0)

        if self.capture is None or not self.capture.isOpened():
            # There is no camera
            print("There is no camera, make sure there is a camera passed through or a webcam plugged in (or both)")
            os._exit(1)

        self.capture.set(3, 360)
        self.capture.set(4, 240)

        self.line_detector = image.LineFinder(self.capture)

        self.hw_interfacer = hardware_interfacer.HwInterfacer()
        
        self.data = {
            # Camera/sensor stuff
            "lines" : [],
            "distance" : 0,
            "theta" : 0,
            "theta_min" : -30,
            "theta_max" : 30,
            "image" : "",
            "resolution" : [],

            # Battery stuff
            "voltage" : 0.0,
            "current" : 0.0,
            "power" : 0.0
        }

        self.fps = -1

    def start(self):
        # Ready? Set. Go!
        
        # Setup loop
        print("Getting async loop...")
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)

        # Start coroutines
        try:
            # FPS polling
            asyncio.ensure_future(self.fps_updater())

            # Sensor/OpenCV values polling
            asyncio.ensure_future(self.value_updater())

            # Web interface
            asyncio.ensure_future(self.web_interface.run())

            # Hardware interface
            asyncio.ensure_future(self.hw_interfacer.drive(self.get_theta))

            # Run async stuff on new thread
            loop.run_forever()

        finally:
            print("Closing Loop")
            loop.close()

    async def get_theta(self):
        return (self.data["theta_min"], self.data["theta"], self.data["theta_max"])

    async def value_updater(self):
        print("Starting line scanner...")
        while asyncio.get_event_loop().is_running():
            hough = self.line_detector.process_frame()

            self.data["theta"], self.data["lines"] = hough[0], hough[1]

            if self.data["theta"] > self.data["theta_max"]:
                self.data["theta_max"] = self.data["theta"]

            if self.data["theta"] < self.data["theta_min"]:
                self.data["theta_min"] = self.data["theta"]

            self.data["resolution"] = [self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)]

            self.web_interface.update_values(self.data)
        
            # Sleep for the amount of time we need to achieve our FPS
            await asyncio.sleep(1.0/self.fps)

        print("Stopping line scanner...")

    async def fps_updater(self):
        print("Starting FPS updater...")
        while asyncio.get_event_loop().is_running():
            self.fps = os.getenv("CAMERA_FPS")
            if not self.fps:
                self.fps = 10

            self.web_interface.set_fps(self.fps)
            await asyncio.sleep(1.0)

        print("Stopping FPS updater...")

if __name__ == "__main__":
    car = CarController()
    car.start()
