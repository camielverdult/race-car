import numpy as np
import cv2, math, time

class LineFinder:

    def __init__(self, capture, data_get_function):
        self.capture = capture
        self.get_data = data_get_function

    async def get_hough_mask(self, shape, edges, ignore_mask_color=255):
        # Next we'll create a masked edges image using cv2.fillPoly()
        mask = np.zeros_like(edges)

        ignore_mask_color = 255

        # Draw a square in centre of the image, this will be masked and ran through the hough transform
        vertices = np.array([[(shape[1]/4, 0), (3*shape[1]/4, 0), (3*shape[1]/4, shape[0]), (shape[1]/4, shape[0])]], dtype=np.int32)
        cv2.fillPoly(mask, vertices, ignore_mask_color) 

        return cv2.bitwise_and(edges, mask)

    async def apply_hough_transform(self, image):

        start = time.perf_counter()
        
        #Convert to Grey Image
        grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Define a kernel size and apply Gaussian smoothing
        kernel_size = 5
        blur_gray = cv2.GaussianBlur(grey_image,(kernel_size, kernel_size), 0)
        
        # Define our parameters for Canny and apply
        low_threshold = 50
        high_threshold = 150
        edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
        
        masked_edges = await self.get_hough_mask(image.shape, edges)

        data = self.get_data()

        # Run Hough on edge detected image
        # Output "lines" is an array containing endpoints of detected line segments
        lines = cv2.HoughLinesP(masked_edges, data.tweaking.rho, data.tweaking.theta, data.tweaking.threshold, np.array([]),
                                    data.tweaking.min_line_length, data.tweaking.max_line_gap)
                                    
        theta = []
        
        # Iterate over the output "lines" and draw lines on a blank image
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    # cv2.line(image, (x1,y1), (x2,y2), (0,255,0), 2)

                    theta.append(math.atan2((y2-y1), (x2-x1)))

                    # theta = theta + math.atan2((y2-y1), (x2-x1))

            print("took {} seconds to run line detection".format(time.perf_counter() - start))

            return (theta, lines.tolist())

    async def process_frame(self):
        _, frame = self.capture.read()

        hough = await self.apply_hough_transform(frame)

        if hough:
            return hough
        else:
            return (0, [])

    async def new_hough(self):

        start = time.perf_counter()
        

        _, frame = self.capture.read()
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(frame, 180, 255, apertureSize = 3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)

        cv2.imwrite('frame.jpg', frame)
        cv2.imwrite('edges.jpg', edges)
        if lines is not None:
            cv2.imwrite('lines.jpg', lines)

        line_coords = []
        thetas = []

        if lines is None:
            print("No lines detected")
            return ([], [])

        for line in lines:
            rho, theta = line[0]
            thetas.append(theta)
            print(theta)
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))

            line_coords.append([x1, y1, x2, y2])

        print("took {} seconds to run line detection".format(time.perf_counter() - start))

        return (thetas, line_coords)