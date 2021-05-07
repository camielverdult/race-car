import car_web_interface
import image
import asyncio
from threading import Thread
import os
import cv2

class CarController:

    def __init__(self):
        self.web_interface = car_web_interface.WebInterface()

        cap = cv2.VideoCapture(0)
        self.line_detector = image.LineFinder(cap)

        self.lines = []
        self.distance = 0
        self.theta = 0
        self.fps = -1

    def start(self):
        # Ready? Set. Go!
        
        # Start web interface
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

            # Run async stuff on new thread
            loop.run_forever()

        finally:
            print("Closing Loop")
            loop.close()

    async def value_updater(self):
        print("Starting line scanner...")
        while asyncio.get_event_loop().is_running():
            self.theta, self.lines = self.line_detector.process_frame()

            print(self.theta)

            # TODO:
            # Map theta to servo degrees


            # TODO: add distance sensor

            self.web_interface.update_values(self.distance, self.lines)
        
            # Sleep for the amount of time we need to achieve our FPS
            await asyncio.sleep(1.0/self.fps)

        print("Stopping line scanner...")

    async def fps_updater(self):
        print("Starting FPS updater...")
        while asyncio.get_event_loop().is_running():
            self.fps = os.getenv("CAMERA_FPS")
            if not self.fps:
                self.fps = 10
            await asyncio.sleep(1.0)

        print("Stopping FPS updater...")

if __name__ == "__main__":
    car = CarController()
    car.start()
